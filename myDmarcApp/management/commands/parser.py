#----------------------------------------------------------------------
# Insipred by Alan Hicks
# https://github.com/alan-hicks/django-dmarc/blob/master/dmarc/management/commands/importdmarcreport.py
#
#----------------------------------------------------------------------

from django.core.management.base import BaseCommand, CommandError
import xml.etree.ElementTree as ET
import .choices as choices

import logging
tree = ET.parse('test.xml')


class Command(BaseCommand):
    help = 'Parses DMARC aggregate reports'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('file_name', nargs='+', type=str)

        parser.add_argument('--type',
            action='store',
            dest='type',
            default=choices.INCOMING,
            help='Incoming ('+choices.INCOMING+') or outgoing('+choices.OUTGOING+') Report')

    def handle(self, *args, **options):

        logger = logging.getLogger(__name__)
        logger.info("Importing DMARC Aggregate Reports")

        for file_name in options['file_name']:

            if os.path.exists(file_name):
                msg = "Found %s" % file_name
                logger.debug(msg)
            else:
                msg = "Unable to find DMARC file: %s" % file_name
                logger.error(msg)
                raise CommandError(msg)

            tree = ET.parse(file_name)
            root = tree.getroot()

            report                      = Report()
            report.report_type          = options['type'] #Check if this is one of choices.INCOMING or choices.OUTGOING
            report.version              = root.find('version').text

            node_metadata               = root.find('report_metadata')
            org_name                    = node_metadata.find('org_name').text
            email                       = node_metadata.find('email').text
            extra_contact_info          = node_metadata.find('extra_contact_info').text
            report.report_id            = node_metadata.find('report_id').text # Check if ID is unique
            report.report_begin         = datetime.fromtimestamp(float(node_metadata.find('date_range').find('begin').text))
            report.report_end           = datetime.fromtimestamp(float(node_metadata.find('date_range').find('end').text))

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
                    msg = "Unable to create DMARC report for %s: $s" % (org_name, e)
                    logger.error(msg)
                    raise CommandError(msg)

            node_policy_published   = root.find('policy_published')

            report.policy_published_domain = node_policy_published.find('domain').text
            report.policy_published_adkim  = node_policy_published.find('adkim').text
            report.policy_published_aspf   = node_policy_published.find('aspf').text
            report.policy_published_p      = node_policy_published.find('p').text
            report.policy_published_sp     = node_policy_published.find('sp').text
            report.policy_published_pct    = node_policy_published.find('pct').text
            report.policy_published_fo     = node_policy_published.find('fo').text

            try:
                report.save()
            except Exception, e:
                msg = "Unable to save the DMARC report header %s: %s" % (report_id, e)
                logger.error(msg)
                raise CommandError(msg)

            # Save report errors these can be 
            for node_error in node_metadata.findall('error'):
                error           = ReportError()
                error.error     = node_error.text
                error.report    = report
                try:
                    error.save()
                except Exception, e:
                    msg  = "Unable to save error message"
                    logger.error(msg)
                    raise CommandError(msg)


            for node_record in root.findall('record'):
                record                  = Record()
                record.report           = report

                node_row                = node_record.find('row')
                record.source_ip        = node_row.find('source_ip').text
                record.count            = int(node_row.find('count').text)

                node_policy_evaluated   = node_row.find('policy_evaluated')
                record.disposition      = node_policy_evaluated.find('disposition').text
                record.dkim             = node_policy_evaluated.find('dkim').text
                record.spf              = node_policy_evaluated.find('spf').text

                node_identifiers        = node_row.find('identifiers')
                record.envelope_to      = node_identifiers.find('envelope_to').text
                record.envelope_from    = node_identifiers.find('envelope_from').text
                record.header_from      = node_identifiers.find('header_from').text

                try:
                    record.save()
                except Exception, e:
                    msg = "Unable to save the DMARC report record: %s" % e
                    logger.error(msg)
                    raise CommandError(msg)

                for node_reason in node_policy_evaluated.findall('reason'):
                    reason          = PolicyOverrideReason()
                    reason.record   = record
                    reason.type     = node_reason.find('type').text
                    reason.comment  = node_reason.find('comment').text
                    try:
                        reason.save()
                    except Exception, e:
                        msg = "Could not save reason"
                        logger.error(msg)
                        raise CommandError(msg)

                node_auth_results = node_record.find('auth_results')
                for node_dkim_result in node_auth_results.findall('dkim'):
                    result_dkim                 = AuthResultDKIM()
                    result_dkim.record          = record
                    result_dkim.domain          = node_dkim_result.find('domain').text
                    result_dkim.selector        = node_dkim_result.find('selector').text
                    result_dkim.result          = node_dkim_result.find('result').text
                    result_dkim.human_result    = node_dkim_result.find('human_result').text
                    try:
                        result_dkim.save()
                    except Exception, e:
                        msg = "Blaaa"
                        logger.error(msg)
                        raise CommandError(msg)

                for node_spf_result in node_auth_results.findall('spf')
                    result_spf          = AuthResultSPF()
                    result_spf.record   = record
                    result_spf.domain   = node_spf_result.find('domain').text
                    result_spf.scope    = node_spf_result.find('scope').text
                    result_spf.result   = node_spf_result.find('result').text
                    try:
                        result_spf.save()
                    except Exception, e:
                        msg = "Blaaa"
                        logger.error(msg)
                        raise CommandError(msg)
