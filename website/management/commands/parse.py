"""
<Program Name>
    parse.py

<Author>
    Lukas Puehringer <luk.puehringer@gmail.com>

<Started>
    June 17, 2015

<Copyright>
    See LICENSE for licensing information.

<Purpose>
    Parses DMARC aggregate reports and stores them into dmarc viewer database.
    The parser expects the DMARC aggregate report schema version 0.1 as defined
    in https://tools.ietf.org/html/rfc7489#appendix-C. However, strict schema
    validation is not performed.

    NOTE: Above schema differs slightly from the DMARC aggregate report schema
    version 0.1 as defined in https://dmarc.org/dmarc-xml/0.1/rua.xsd.

    dmarc-viewer differs between incoming and outgoing reports.

    Incoming reports you receive from foreign domains (reporter) based
    on e-mail messages, the reporter received, purportedly from you.

    Outgoing reports on the other hand you send to foreign domains based on
    e-mail messages that you received, purportedly by them.

    To better visualize the reports you have to specify the report type when
    using this parser. Default is incoming reports (in).

    Maxmind GeoLite2 City db is used to retrieve geo information for IP
    addresses.

    The parser generates and stores file hashes of the reports to skip reports
    that are already in the database.

<Usage>
    ```
    python manage.py parse \
      [--univie] [--type (in|out)] <dmarc-aggregate-report>.xml, ...

    ```

<Disclaimers>
    This product includes GeoLite2 data created by MaxMind, available from
    <a href="http://www.maxmind.com">http://www.maxmind.com</a>.

    Used ideas from Alan Hick's importdmarcreport.py
    https://github.com/alan-hicks/django-dmarc/

"""

import xml.etree.ElementTree

import os
import datetime

import logging
import pytz
import hashlib
import geoip2.database

from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

from website import choices
from website.models import (Report, Reporter, ReportError, Record,
        PolicyOverrideReason, AuthResultDKIM, AuthResultSPF)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("parse")

geoip_reader = geoip2.database.Reader(settings.GEO_LITE2_CITY_DB)

UNVIE = False
REPORT_TYPE = choices.INCOMING


class Command(BaseCommand):
    help = "Parses DMARC aggregate reports into DMARC VIEWER db."

    def add_arguments(self, parser):

        # One or more file/directory names for aggregate reports
        parser.add_argument("path", nargs="+", type=str,
                help="File or directory path(s) to DMARC aggregate report(s)")

        # Report type - default is "in"
        parser.add_argument("--type", action="store", dest="type",
                default="in", choices=("in", "out"), help=("Did you receive"
                " the report (in) or did you send it (out)?"))

        parser.add_argument("--univie", dest="univie", default=False,
                action="store_true", help=("Parse special anonymized format "
                "used for University of Vienna's incoming reports"))

    def handle(self, *args, **options):
        """Entry point for parser. Iterates over file_name arguments."""

        global UNIVIE
        global REPORT_TYPE

        UNIVIE = options["univie"]

        if options["type"] == "in":
            REPORT_TYPE = choices.INCOMING

        elif options["type"] == "out":
            REPORT_TYPE = choices.OUTGOING

        # Iterate over files/directories
        for file_name in options["path"]:
            self.walk(file_name)

    def walk(self, path):
        """Recursively walk over passed files. """

        if os.path.isfile(path):
            self.parse(path)

        elif os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                for file in files:
                    self.parse(os.path.join(root, file))

        else:
            logger.info("Could not find path '{}'.".format(path))

    def parse(self, path):
        """Parses single DMARC aggregate report and stores to db. """

        logger.info("Parsing '{}'".format(path))
        log_prefix = "Report '{path}:'".format(path=path)
        # Skip files that don't end with ".xml"
        if not path.endswith(".xml"):
            logger.info("{0} Skipping non *.xml file names."
                    .format(log_prefix))
            return

        # Try parsing XML tree
        try:
            with open(path) as file:
                # Parse the file into XML Element Tree
                xml_tree = xml.etree.ElementTree.parse(file)
        except Exception as e:
            logger.error("{0} Could not parse XML tree.".format(log_prefix))
            return

        # We are good, do the md5 hash of the vanilla file too
        try:
            with open(path) as file:
                hasher = hashlib.md5()
                hasher.update(file.read())
                file_hash = hasher.hexdigest()
        except Exception as e:
            logger.error("{0} Could not hash file contents: {1}"
                .format(log_prefix, e))
            return

        # FIXME: verify DMARC schema

        # Skip rest if the file already exists based on the hash
        if Report.objects.filter(report_hash=file_hash):
            logger.info("{0} Skipping already stored report."
                    .format(log_prefix))
            return

        ##############################################################
        # Translate DMARC aggregate report into dmarc-viewer model...
        xml_root = xml_tree.getroot()

        # Create report object
        report = Report()
        report.report_hash = file_hash

        # Assign report metadata
        report.report_type = REPORT_TYPE
        version = xml_root.findtext("version")
        if version:
            report.version = float(version)

        node_metadata = xml_root.find("report_metadata")
        report.report_id = node_metadata.findtext("report_id")
        report.date_range_begin = datetime.datetime.fromtimestamp(float(
                node_metadata.find("date_range").findtext("begin")),
                tz=pytz.utc)

        report.date_range_end = datetime.datetime.fromtimestamp(float(
                node_metadata.find("date_range").findtext("end")), tz=pytz.utc)

        # Create reporter (or retrieve existing from db)
        org_name = node_metadata.findtext("org_name")
        email = node_metadata.findtext("email")
        extra_contact_info = node_metadata.findtext("extra_contact_info")
        try:
            reporter = Reporter.objects.get(org_name=org_name, email=email,
                    extra_contact_info=extra_contact_info)
            logger.info(
                    "{0} Re-using existing reporter '{1}'"
                    .format(log_prefix, org_name))
        except ObjectDoesNotExist as e:
            reporter = Reporter()
            reporter.org_name = org_name
            reporter.email = email
            reporter.extra_contact_info = extra_contact_info

            # New reporter has to be stored to db to reference it in report
            try:
                reporter.save()
            except Exception as e:
                logger.error(
                        "{0} Could not save reporter: {1}"
                        .format(log_prefix, e))
                return

        # Assign reporter
        report.reporter = reporter

        # Assign policy published
        node_policy_published = xml_root.find('policy_published')
        report.domain = node_policy_published.findtext('domain')
        report.adkim = choices._string_to_numeric(choices.ALIGNMENT_MODE,
                node_policy_published.findtext('adkim'))
        report.aspf = choices._string_to_numeric(choices.ALIGNMENT_MODE,
                node_policy_published.findtext('aspf'))
        report.p = choices._string_to_numeric(choices.DISPOSITION_TYPE,
                node_policy_published.findtext('p'))
        report.sp = choices._string_to_numeric(choices.DISPOSITION_TYPE,
                node_policy_published.findtext('sp'))
        # Field not in https://dmarc.org/dmarc-xml/0.1/rua.xsd
        report.fo = node_policy_published.findtext('fo')
        pct = node_policy_published.findtext('pct')
        if pct:
            report.pct = int(pct)

        # Store report to db
        try:
            report.save()
        except Exception as e:
            logger.error("{0} Could not save report: {1}"
                    .format(log_prefix, e))
            return

        # Create report error objects
        for node_error in node_metadata.findall('error'):
            error = ReportError()
            error.error = node_error.text
            error.report = report
            try:
                error.save()
            except Exception as e:
                logger.warning("{0} Could not save report error: {1}"
                        .format(log_prefix, e))

        # Create record objects
        for record_idx, node_record in enumerate(xml_root.findall('record')):
            record = Record()
            record.report = report

            node_row = node_record.find('row')
            ip_element = node_row.find('source_ip')

            # Assign IP and ISO country code (ISO 3166 Alpha-2)
            try:
                # University of Vienna special case for anonymized IP addresses
                if UNIVIE and REPORT_TYPE == choices.INCOMING:
                    record.country_iso_code = ip_element.attrib.get(
                            'geoip', '')
                else:
                    record.source_ip = ip_element.text
                    response = geoip_reader.city(record.source_ip)
                    record.country_iso_code = response.country.iso_code

            except Exception as e:
                logger.warning(
                        "{0} Could not find ISO country code for IP '{1}'"
                        " in record {2}: {3}"
                        .format(log_prefix, record.source_ip, record_idx, e))

            # Assign record info
            record.count = int(node_row.findtext('count'))
            node_policy_evaluated = node_row.find('policy_evaluated')
            record.disposition = choices._string_to_numeric(
                    choices.DISPOSITION_TYPE,
                    node_policy_evaluated.findtext('disposition'))
            record.dkim = choices._string_to_numeric(choices.DMARC_RESULT,
                    node_policy_evaluated.findtext('dkim'))
            record.spf = choices._string_to_numeric(choices.DMARC_RESULT,
                    node_policy_evaluated.findtext('spf'))

            node_identifiers = node_record.find('identifiers')
            if node_identifiers is not None:
                record.envelope_to = node_identifiers.findtext(
                        'envelope_to')
                # Field not in https://dmarc.org/dmarc-xml/0.1/rua.xsd
                record.envelope_from = node_identifiers.findtext(
                        'envelope_from')
                record.header_from = node_identifiers.findtext(
                        'header_from')

            try:
                record.save()
            except Exception as e:
                logger.warning("{0} Could not save record '{1}': {2}"
                        .format(log_prefix, record_idx, e))
                return

            # Create policy override reason objects
            for reason_idx, node_reason in enumerate(
                    node_policy_evaluated.findall('reason')):
                reason = PolicyOverrideReason()
                reason.record = record
                reason.type = choices._string_to_numeric(
                        choices.POLICY_REASON_TYPE,
                        node_reason.findtext('type'))
                reason.comment = node_reason.findtext('comment')

                try:
                    reason.save()
                except Exception as e:
                    logger.warning(
                            "{0} Could not save policy override reason '{1}'"
                            " for record '{2}': {3}"
                            .format(log_prefix, reason_idx, record_idx, e))

            # Find authentication results
            node_auth_results = node_record.find('auth_results')

            # DKIM result counter (performance boost for data analysis)
            dkim_count = 0

            # Create DKIM authentication result objects
            for dkim_result_idx, node_dkim_result in enumerate(
                    node_auth_results.findall('dkim')):
                result_dkim = AuthResultDKIM()
                result_dkim.record = record
                result_dkim.domain = node_dkim_result.findtext('domain')
                # Field not in https://dmarc.org/dmarc-xml/0.1/rua.xsd
                result_dkim.selector = node_dkim_result.findtext('selector')
                result_dkim.result = choices._string_to_numeric(
                        choices.DKIM_RESULT,
                        node_dkim_result.findtext('result'))
                result_dkim.human_result = node_dkim_result.findtext(
                        'human_result')
                try:
                    result_dkim.save()
                    dkim_count += 1
                except Exception as e:
                    logger.warning("{0} Could not save DKIM auth_result"
                            " '{1}' for record '{2}': {3}"
                            .format(log_prefix, dkim_result_idx,
                            record_idx, e))

            # Create SPF authentication result objects
            for spf_result_idx, node_spf_result in enumerate(
                    node_auth_results.findall('spf')):
                result_spf = AuthResultSPF()
                result_spf.record = record
                result_spf.domain = node_spf_result.findtext('domain')
                # Field not in https://dmarc.org/dmarc-xml/0.1/rua.xsd
                result_spf.scope = choices._string_to_numeric(
                        choices.SPF_SCOPE, node_spf_result.findtext('scope'))
                result_spf.result = choices._string_to_numeric(
                        choices.SPF_RESULT, node_spf_result.findtext('result'))

                try:
                    result_spf.save()
                except Exception as e:
                    logger.warning("{0} Could not save SPF auth_result"
                            " '{1}' for record '{2}': {3}"
                            .format(log_prefix, spf_result_idx,
                            record_idx, e))

            # Assign DKIM results counter to report and re-save
            try:
                record.auth_result_dkim_count = dkim_count
                record.save()
            except Exception as e:
                logger.warning("{0} Could not save record {1}: {2}"
                        .format(log_prefix, record_idx, e))
