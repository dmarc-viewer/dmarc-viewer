"""
<Program Name>
    choices.py

<Author>
    Lukas Puehringer <luk.puehringer@gmail.com>

<Started>
    June 10, 2015

<Copyright>
    See LICENSE for licensing information.

<Purpose>
    Defines tuples that contain possible values for aggregate DMARC report
    properties.
    dmarc_viewer db stores numeric values instead of the string representation
    of these properties.

    The tuples are used with Django choice form fields to restrict select
    widgets to the allowed values.

    This module also provides a helper function that converts the string values
    parsed from DMARC aggregate reports to the here defined numeric constants.

"""


def _string_to_numeric(choices, val):
    """Takes a choices tuple and a string and returns the numeric
    representation as defined in this module . """
    for choice in choices:
        if choice[1] == val:
            return choice[0]
    return None

INCOMING = 1
OUTGOING = 2
REPORT_TYPE = (
        (INCOMING, "incoming"),
        (OUTGOING, "outgoing")
    )

STRICT = 1
RELAXED = 2
ALIGNMENT_MODE = (
        (STRICT, "s"),
        (RELAXED, "r")
    )

NONE = 1
QUARANTINE = 2
REJECT = 3
DISPOSITION_TYPE = (
        (NONE, "none"),
        (QUARANTINE, "quarantine"),
        (REJECT, "reject")
    )

PASS = 1
FAIL = 2
DMARC_RESULT = (
        (PASS, "pass"),
        (FAIL, "fail")
    )

FORWARDED = 1
SAMPLED_OUT = 2
TRUSTED_FWD = 3
MAILING_LIST = 4
LOCAL_POLICY = 5
OTHER = 6
POLICY_REASON_TYPE =  (
        (FORWARDED, "forwarded"),
        (SAMPLED_OUT, "sampled_out"),
        (TRUSTED_FWD, "trusted_forwarder"),
        (MAILING_LIST, "mailing_list"),
        (LOCAL_POLICY, "local_policy"),
        (OTHER, "other")
    )

HELO = 1
MFROM = 2
SPF_SCOPE = (
        (HELO, "helo"),
        (MFROM, "mfrom")
    )

SPF_NONE = 1
SPF_NEUTRAL = 2
SPF_PASS = 3
SPF_FAIL = 4
SPF_SOFTFAIL = 5
SPF_TEMPERROR = 6
SPF_PERMERROR = 7
SPF_RESULT = (
        (SPF_NONE, "none"),
        (SPF_NEUTRAL, "neutral"),
        (SPF_PASS, "pass"),
        (SPF_FAIL, "fail"),
        (SPF_SOFTFAIL, "softfail"),
        (SPF_TEMPERROR, "temperror"),
        (SPF_PERMERROR, "permerror")
    )

DKIM_NONE = 1
DKIM_PASS = 2
DKIM_FAIL = 3
DKIM_POLICY = 4
DKIM_NEUTRAL = 5
DKIM_TEMPERROR = 6
DKIM_PERMERROR = 7
DKIM_RESULT = (
        (DKIM_NONE, "none"),
        (DKIM_PASS, "pass"),
        (DKIM_FAIL, "fail"),
        (DKIM_POLICY, "policy"),
        (DKIM_NEUTRAL, "neutral"),
        (DKIM_TEMPERROR, "temperror"),
        (DKIM_PERMERROR, "permerror")
    )

TIME_UNIT_DAY = 1
TIME_UNIT_WEEK = 2
TIME_UNIT_MONTH = 3
TIME_UNIT_YEAR = 4
TIME_UNIT = (
    (None, "-----"),
    (TIME_UNIT_DAY, "day(s)"),
    (TIME_UNIT_WEEK, "week(s)"),
    (TIME_UNIT_MONTH, "month(s)"),
    (TIME_UNIT_YEAR, "year(s)")
    )

DATE_RANGE_TYPE_FIXED = 1
DATE_RANGE_TYPE_VARIABLE = 2
DATE_RANGE_TYPE = (
    (DATE_RANGE_TYPE_FIXED, "from - to (absolute)"),
    (DATE_RANGE_TYPE_VARIABLE, "last x ... (dynamic)")
    )