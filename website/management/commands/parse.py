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
  Parses DMARC aggregate reports and stores them into dmarc-viewer database
  See https://tools.ietf.org/html/rfc7489#section-7.2 for the exact format.

  dmarc-viewer differs between incoming and outgoing reports.
  Incoming reports you receive from foreign domains (reporter) based
  on e-mail messages, the reporter received, purportedly from you.
  Outgoing reports on the other hand you send to foreign domains based on
  e-mail messages that you received, purportedly by them.
  To better visualize the reports you have specify the report type when
  using this parser (default is in).

  Maxmind GeoLite2 City db is used to query geo information for IP addresses.

  The parser generates and stores file hashes of the reports to skip reports
  that are already in the database.

<Usage>
  ```
    python manage.py parse \
      [--type (in|out)] <dmarc-aggregate-report>.xml, ...

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

from django.core.management.base import BaseCommand, CommandError
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings

from website import choices
from website.models import (Report, Reporter, ReportError, Record,
    PolicyOverrideReason, AuthResultDKIM, AuthResultSPF)

logger = logging.getLogger("parse")

geoip_reader = geoip2.database.Reader(settings.GEO_LITE2_CITY_DB)

class Command(BaseCommand):

  help = "Parses DMARC aggregate reports and writes to DMARC VIEWER database."

  def add_arguments(self, parser):

    # One or more file/directory names for aggregate reports
    parser.add_argument("path", nargs="+", type=str,
        help="File or directory path(s) to DMARC aggregate report(s)")

    # Report type - default is "in"
    parser.add_argument("--type",
        action="store", dest="type", default="in", choices=("in", "out")
        help="Did you receive the report (in) or did you send it (out)?")

    def handle(self, *args, **options):
      """Entry point for parser. Iterates over file_name arguments."""

      if options["type"] == "in":
        report_type = choices.INCOMING

      elif options["type"] == "out":
        report_type = choices.OUTGOING

      # Iterate over files/directories
      for file_name in options["path"]:
          self.iterate(file_name, report_type)

    def walk(self, path, report_type):
      """Recursively walk over passed files. """

      if os.path.isfile(path):
        self.parse(path, report_type)

      elif os.path.isdir(path):
        for root, dirs, files in os.walk(path):
          for file in files:
            self.parse(os.path.join(root, file), report_type)

      else:
        logger.info("Could not find path '{}'.".format(path))

    def parse(self, path, report_type):
      """Parses single DMARC aggregate report and stores to db. """

      logger.info("Parsing '{}'".format(path))

      # Skip files that don't end with .xml
      if not path.endswith(".xml"):
        logger.info("Skipping '{}' - we only take *.xml files".format(path))
        return

      # Try parsing XML tree
      try:
        with open(path) as file:
          # Parse the file into XML Element Tree
          xml_tree = xml.etree.ElementTree.parse(file)
      except Exception as e:
        log.error("Could not parse XML tree of report '{0}': {1}"
            .format(path, e))
        return

      # We are good, do the md5 hash of the vanilla file too
      try:
        with open(path) as file:
          hasher = hashlib.md5()
          hasher.update(file.read())
          file_hash = hasher.hexdigest()
      except Exception as e:
        log.error("Could not hash contents of report '{0}': {1}"
            .format(path, e))
        return

      # FIXME: verify DMARC schema

      # Skip rest if the file already exists based on the hash
      if Report.objects.find(report_hash=file_hash):
        logger.info("Skipping duplicate '{}'... ".format(path))
        return

      ##############################################################
      # Translate DMARC aggregate report into dmarc-viewer model...
      xml_root = xml_tree.getroot()

      # Create report object
      report = Report()
      report.report_hash = report_hash

      # Assign report metadata
      report.report_type = report_type
      version = root.findtext("version")
      if version:
        report.version = float(version)

      node_metadata = root.find("report_metadata")
      report.report_id = node_metadata.findtext("report_id")
      report.date_range_begin = datetime.datetime.fromtimestamp(float(
          node_metadata.find("date_range").findtext("begin")), tz=pytz.utc)

      report.date_range_end = datetime.datetime.fromtimestamp(float(
          node_metadata.find("date_range").findtext("end")), tz=pytz.utc)

      # Create reporter (or retrieve existing from db)
      org_name = node_metadata.findtext("org_name")
      email = node_metadata.findtext("email")
      extra_contact_info = node_metadata.findtext("extra_contact_info")
      try:
        reporter = Reporter.objects.get(org_name=org_name, email=email,
          extra_contact_info=extra_contact_info)
      except ObjectDoesNotExist as e:
        reporter = Reporter()
        reporter.org_name = org_name
        reporter.email = email
        reporter.extra_contact_info = extra_contact_info

        # New reporter has to be stored to db to reference it in report
        try:
          reporter.save()
        except Exception as e:
          msg = logger.error("In report '{0}' could not save reporter '{1}': {2}"
              .format(path, org_name, e))
          return

      # Assign reporter
      report.reporter = reporter

      # Assign policy published
      node_policy_published = root.find('policy_published')
      report.domain = node_policy_published.findtext('domain')
      report.adkim = choices.convert(choices.ALIGNMENT_MODE,
          node_policy_published.findtext('adkim'))
      report.aspf = choices.convert(choices.ALIGNMENT_MODE,
          node_policy_published.findtext('aspf'))
      report.p = choices.convert(choices.DISPOSITION_TYPE,
          node_policy_published.findtext('p'))
      report.sp = choices.convert(choices.DISPOSITION_TYPE,
          node_policy_published.findtext('sp'))
      report.fo = node_policy_published.findtext('fo')
      pct = node_policy_published.findtext('pct')
      if pct:
        report.pct = int(pct)


      # Store report to db
      try:
        report.save()
      except Exception as e:
        logger.error("In report '{0}' could not save report"
            " (report id='{1}': {2}}".format(path, report.report_id, e))
        return

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
