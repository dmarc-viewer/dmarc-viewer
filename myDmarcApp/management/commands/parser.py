#----------------------------------------------------------------------
# Insipred by Alan Hicks
# https://github.com/alan-hicks/django-dmarc/blob/master/dmarc/management/commands/importdmarcreport.py
#
#----------------------------------------------------------------------

from __future__ import unicode_literals
import xml.etree.ElementTree as ET
from datetime import datetime
import logging
import os
import pytz
import geoip2.database

from django.core.management.base import BaseCommand, CommandError
from myDmarcApp.models import Report, Reporter, ReportError, Record, PolicyOverrideReason, AuthResultDKIM, AuthResultSPF
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.contrib.gis.geos import Point

import myDmarcApp.choices as choices

logger = logging.getLogger('django')
logger.info("Parse DMARC Aggregate Report into MyDMARC DB")
geoip_reader = geoip2.database.Reader('/Users/topfpflanze/projectsOther/master/mydmarc/myDmarcApp/data/GeoLite2-City.mmdb')

class Command(BaseCommand):
    help = 'Parses DMARC aggregate reports'

    def add_arguments(self, parser):
        # Files
        parser.add_argument('file_name', nargs='+', type=str)

        # Report Type
        parser.add_argument('--type',
            action='store',
            dest='type',
            default=choices.INCOMING,
            help='Incoming ('+str(choices.INCOMING)+') or outgoing ('+str(choices.OUTGOING)+') Report')

    def handle(self, *args, **options):
        report_type = options['type']
        # Iterate over files
        for file_name in options['file_name']:
            self.iterate(file_name, report_type)

    def iterate(self, file_name, report_type):
        if os.path.isfile(file_name):
            self.parse(file_name, report_type)
        elif os.path.isdir(file_name):
            for root, dirs, files in os.walk(file_name):
                for file in files:
                    self.iterate(os.path.join(root, file), report_type)
        else:
            msg = "Could not find %s" % file_name
            logger.debug(msg)

    def parse(self, file_name, report_type):
        if not file_name.endswith('.xml'):
            return False

        # Parse the file into XML Element Tree
        try:
            tree = ET.parse(file_name)
        except Exception, e:
            msg = "Could not parse file '%s': %s" % (file_name, e)
            logger.error(msg)
            return False

        root = tree.getroot()

        # Create new report object and assign metadata
        report                      = Report()

        report.report_type          = report_type
        
        version                     = root.findtext('version')
        if version:
            report.version          = float(version)

        node_metadata               = root.find('report_metadata')
        report.report_id            = node_metadata.findtext('report_id')
        report.date_range_begin     = datetime.fromtimestamp(float(
                                        node_metadata.find('date_range').findtext('begin')), tz=pytz.utc)
        report.date_range_end       = datetime.fromtimestamp(float(
                                        node_metadata.find('date_range').findtext('end')), tz=pytz.utc)

        # Report Sender meta data is stored in an extra object
        # If we don't have it create a new one
        org_name                    = node_metadata.findtext('org_name')
        email                       = node_metadata.findtext('email')
        extra_contact_info          = node_metadata.findtext('extra_contact_info')
        try:
            reporter = Reporter.objects.get(org_name=org_name, email=email, 
                extra_contact_info=extra_contact_info)
        except ObjectDoesNotExist:
            reporter = Reporter()
            reporter.org_name               = org_name
            reporter.email                  = email
            reporter.extra_contact_info     = extra_contact_info
            try:
                reporter.save()
            except Exception, e:
                msg = "Unable to create DMARC reporter for %s: %s" % (org_name, e)
                logger.error(msg)
                #raise CommandError(msg)
        report.reporter                     = reporter

        # Add policy published data to report object 
        node_policy_published   = root.find('policy_published')
        report.domain           = node_policy_published.findtext('domain')
        report.adkim            = choices.convert(choices.ALIGNMENT_MODE, 
                                                    node_policy_published.findtext('adkim'))
        report.aspf             = choices.convert(choices.ALIGNMENT_MODE, 
                                                    node_policy_published.findtext('aspf'))
        report.p                = choices.convert(choices.DISPOSITION_TYPE,
                                                    node_policy_published.findtext('p'))
        report.sp               = choices.convert(choices.DISPOSITION_TYPE,
                                                    node_policy_published.findtext('sp'))
        pct                     = node_policy_published.findtext('pct')
        if pct:
            report.pct          = int(pct)
        report.fo               = node_policy_published.findtext('fo')

        try:
            report.save()
        except Exception, e:
            msg = "Unable to create DMARC report for %s: %s" % (report.report_id, e)
            logger.error(msg)
            #raise CommandError(msg)

        # Save report errors
        for node_error in node_metadata.findall('error'):
            error               = ReportError()
            error.error         = node_error.text
            error.report        = report
            try:
                error.save()
            except Exception, e:
                msg  = "Unable to save error for %s: %s" % (report.report_id, e)
                logger.error(msg)
                #raise CommandError(msg)


        for node_record in root.findall('record'):
            record                   = Record()
            record.report            = report

            node_row                 = node_record.find('row')

            ip_element               = node_row.find('source_ip')
            # Univie special case for anonymised IP addresses
            if (ip_element.attrib.get('anonymised_ip', '0') == '1'):
                record.country_iso_code = ip_element.attrib.get('geoip', '')
            else: 
                record.source_ip         = ip_element.text
                try:
                    response                 = geoip_reader.city(record.source_ip)
                    record.geometry          = Point(float(response.location.longitude), 
                                                        float(response.location.latitude))
                    record.country_iso_code   = response.country.iso_code
                except Exception, e:
                    msg  = "Unable to retrieve geometry for ip %s: %s" % (record.source_ip, e)
                    logger.error(msg)

            
            record.count             = int(node_row.findtext('count'))

            node_policy_evaluated    = node_row.find('policy_evaluated')
            record.disposition       = choices.convert(choices.DISPOSITION_TYPE, 
                                         node_policy_evaluated.findtext('disposition'))
            record.dkim              = choices.convert(choices.DMARC_RESULT,
                                         node_policy_evaluated.findtext('dkim'))
            record.spf               = choices.convert(choices.DMARC_RESULT,
                                         node_policy_evaluated.findtext('spf'))

            node_identifiers         = node_record.find('identifiers')
            if node_identifiers is not None:
                record.envelope_to       = node_identifiers.findtext('envelope_to')
                record.envelope_from     = node_identifiers.findtext('envelope_from')
                record.header_from       = node_identifiers.findtext('header_from')

            try:
                record.save()
            except Exception, e:
                msg = "Unable to save the DMARC record for %s: %s" % (report.report_id, e)
                logger.error(msg)
                #raise CommandError(msg)

            for node_reason in node_policy_evaluated.findall('reason'):
                reason          = PolicyOverrideReason()
                reason.record   = record
                reason.type     = choices.convert(choices.POLICY_REASON_TYPE,
                                    node_reason.findtext('type'))
                reason.comment  = node_reason.findtext('comment')
                try:
                    reason.save()
                except Exception, e:
                    msg = "Unable to save reason for %s: %s" % (report.report_id, e)
                    logger.error(msg)
                    #raise CommandError(msg)

            node_auth_results = node_record.find('auth_results')
            dkim_count = 0
            for node_dkim_result in node_auth_results.findall('dkim'):
                result_dkim                 = AuthResultDKIM()
                result_dkim.record          = record
                result_dkim.domain          = node_dkim_result.findtext('domain')
                result_dkim.selector        = node_dkim_result.findtext('selector')
                result_dkim.result          = choices.convert(choices.DKIM_RESULT,
                                                node_dkim_result.findtext('result'))
                result_dkim.human_result    = node_dkim_result.findtext('human_result')
                try:
                    result_dkim.save()
                    dkim_count += 1
                except Exception, e:
                    msg = "Unable to save DKIM auth_result for %s: %s" % (report.report_id, e)
                    logger.error(msg)
                    #raise CommandError(msg)

            for node_spf_result in node_auth_results.findall('spf'):
                result_spf          = AuthResultSPF()
                result_spf.record   = record
                result_spf.domain   = node_spf_result.findtext('domain')
                result_spf.scope    = choices.convert(choices.SPF_SCOPE, 
                                        node_spf_result.findtext('scope'))
                result_spf.result   = choices.convert(choices.SPF_RESULT, 
                                        node_spf_result.findtext('result'))
                try:
                    result_spf.save()
                except Exception, e:
                    msg = "Unable to save SPF auth_result for %s: %s" % (report.report_id, e)
                    logger.error(msg)
                    #raise CommandError(msg)

            try:
                record.auth_result_dkim_count = dkim_count
                record.save()
            except Exception, e:
                msg = "Unable to save the DMARC record for %s: %s" % (report.report_id, e)
                logger.error(msg)
                #raise CommandError(msg)
