#----------------------------------------------------------------------
# Copyright (c) 2015, Persistent Objects Ltd http://p-o.co.uk/
#
# License: BSD
#
# https://github.com/alan-hicks/django-dmarc/blob/master/dmarc/management/commands/importdmarcreport.py
# Customized for dmarc_viewer
#----------------------------------------------------------------------

from __future__ import unicode_literals
import xml.etree.ElementTree as ET
from datetime import datetime
import logging
import os
import pytz
import geoip2.database
import hashlib

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from website.models import Report, Reporter,\
     ReportError, Record, PolicyOverrideReason, AuthResultDKIM, AuthResultSPF
from django.core.exceptions import ObjectDoesNotExist

import website.choices as choices

logger = logging.getLogger("parser")
logger.info("Parse DMARC Aggregate Report into DMARC VIEWER DB")

geoip_reader = geoip2.database.Reader(settings.GEO_LITE2_CITY_DB)

class Command(BaseCommand):
    """Parses DMARC aggregate reports and writes to DMARC VIEWER database."""

    help = "Parses DMARC aggregate reports and writes to DMARC VIEWER database."

    def add_arguments(self, parser):
        """Defines the arguments for command line usage."""

        # One or more file/directory names for aggregate reports
        parser.add_argument("file_name", nargs="+", type=str)

        # Report type - default is incoming
        parser.add_argument("--type",
            action="store",
            dest="type",
            default=choices.INCOMING,
            help="Incoming ("+str(choices.INCOMING)+") or outgoing ("+str(choices.OUTGOING)+") Report")

    def handle(self, *args, **options):
        """Entry point for parser. Iterates over file_name arguments."""

        report_type = options["type"]
        # Iterate over files/directories
        for file_name in options["file_name"]:
            self.iterate(file_name, report_type)

    def iterate(self, file_name, report_type):
        """Parses for each file. Recurses if file is directory. """

        if os.path.isfile(file_name):
            self.parse(file_name, report_type)
        elif os.path.isdir(file_name):
            for root, dirs, files in os.walk(file_name):
                for f in files:
                    self.iterate(os.path.join(root, f), report_type)
        else:
            msg = "Could not find '%s'" % file_name
            logger.info(msg)

    def parse(self, file_name, report_type):
        """Parses single DMARC aggregate report and stores to db."""

        try:
            logger.info("Parsing '%s'" % file_name)

            # File extension check
            if not file_name.endswith('.xml'):
                msg = "Skipping '%s'" % (file_name)
                logger.info(msg)
                return False


            # with open(file_name) as f:
            #     # Parse the file into XML Element Tree
            #     try:
            #         tree = ET.parse(f)
            #     except Exception, e:
            #         msg = "Could not parse file '%s' into tree: %s" % (file_name, e)
            #         logger.error(msg)
            #         return False

            #     # Create md5 hash from file content
            #     hasher = hashlib.md5()
            #     hasher.update(f.read())

            # report_hash = hasher.hexdigest()

            # # Check if file already exists
            # if Report.objects.find(report_hash=report_hash):
            #     msg = "Skipping duplicate '%s' into tree" % (file_name,)
            #     logger.info(msg)
            #     return False


            # Parse the file into XML Element Tree
            try:
                tree = ET.parse(file_name)
            except Exception, e:
                msg = "Could not parse file '%s' into tree: %s" % (file_name, e)
                logger.error(msg)
                return False

            root = tree.getroot()

            # Create report object
            report                      = Report()
            #report.report_hash          = report_hash

            # Assign report metadata
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

            # Create or use existing reporter object
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

                # New reporter has to be stored to db to reference it
                # in report
                try:
                    reporter.save()
                except Exception, e:
                    msg = "Could not save reporter '%s': %s" % (org_name, e)
                    logger.error(msg)
                    return False

            # Assign reporter
            report.reporter = reporter

            # Assign policy published
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

            # Save report
            try:
                report.save()
            except Exception, e:
                msg = "Could not save DMARC report for '%s': %s" % (report.report_id, e)
                logger.error(msg)
                return False

            # Create report error objects
            for node_error in node_metadata.findall('error'):
                error               = ReportError()
                error.error         = node_error.text
                error.report        = report
                try:
                    error.save()
                except Exception, e:
                    msg  = "Could not save error for report '%s': %s" % (report.report_id, e)
                    logger.warning(msg)

            # Create record objects
            for node_record in root.findall('record'):
                record                   = Record()
                record.report            = report

                node_row                 = node_record.find('row')
                ip_element               = node_row.find('source_ip')

                # Assign IP and ISO country code (ISO 3166 Alpha-2)
                try:
                    # Univie special case for anonymised IP addresses
                    if (ip_element.attrib.get('anonymised_ip', '0') == '1'):
                        record.country_iso_code  = ip_element.attrib.get('geoip', '')
                    else:
                        record.source_ip         = ip_element.text
                        response                 = geoip_reader.city(record.source_ip)
                        record.country_iso_code  = response.country.iso_code
                except Exception, e:
                    msg  = "Could not find ISO country code for IP '%s': %s" % (record.source_ip, e)
                    logger.warning(msg)


                # Assign record info
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
                    msg = "Could not save record for report '%s': %s" % (report.report_id, e)
                    logger.warning(msg)

                # Create policy override reason objects
                for node_reason in node_policy_evaluated.findall('reason'):
                    reason          = PolicyOverrideReason()
                    reason.record   = record
                    reason.type     = choices.convert(choices.POLICY_REASON_TYPE,
                                        node_reason.findtext('type'))
                    reason.comment  = node_reason.findtext('comment')
                    try:
                        reason.save()
                    except Exception, e:
                        msg = "Could not save policy override reason for report '%s': %s" % (report.report_id, e)
                        logger.warning(msg)

                # Find authentication results
                node_auth_results = node_record.find('auth_results')


                # DKIM result counter (performance boost for data analysis)
                dkim_count = 0
                # Create DKIM authentication result objects
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
                        msg = "Could not save DKIM auth_result for report '%s': %s" % (report.report_id, e)
                        logger.warning(msg)

                # Create SPF authentication result objects
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
                        msg = "Could not save SPF auth_result for report '%s': %s" % (report.report_id, e)
                        logger.warning(msg)

                # Assign DKIM results counter to report and re-save
                try:
                    record.auth_result_dkim_count = dkim_count
                    record.save()
                except Exception, e:
                    msg = "Could not save DMARC record for for report '%s': %s" % (report.report_id, e)
                    logger.warning(msg)

        except Exception, e:
            msg = "Something went wrong while parsing '%s': %s" % (file_name, e)
            logger.error(msg)
