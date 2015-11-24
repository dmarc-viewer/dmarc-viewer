def convert(choices, val):
    for choice in choices:
        if choice[1] == val:
            return choice[0]
    return None

INCOMING = 1
OUTGOING = 2
REPORT_TYPE = (
        (INCOMING, 'incoming'),
        (OUTGOING, 'outgoing')
    )

STRICT = 1
RELAXED = 2
ALIGNMENT_MODE = (
        (STRICT, 's'),
        (RELAXED, 'r')
    )

NONE = 1
QUARANTINE = 2
REJECT = 3
DISPOSITION_TYPE = (
        (NONE, 'none'),
        (QUARANTINE, 'quarantine'),
        (REJECT, 'reject')
    )

PASS = 1
FAIL = 2
DMARC_RESULT = (
        (PASS, 'pass'),
        (FAIL, 'fail')
    )

FORWARDED = 1
SAMPLED_OUT = 2
TRUSTED_FWD = 3
MAILING_LIST = 4
LOCAL_POLICY = 5
OTHER = 6
POLICY_REASON_TYPE =  (
        (FORWARDED, 'forwarded'),
        (SAMPLED_OUT, 'sampled_out'),
        (TRUSTED_FWD, 'trusted_forwarder'),
        (MAILING_LIST, 'mailing_list'),
        (LOCAL_POLICY, 'local_policy'),
        (OTHER, 'other')
    )

HELO = 1
MFROM = 2
SPF_SCOPE = (
        (HELO, 'helo'),
        (MFROM, 'mfrom')
    )

SPF_NONE = 1
SPF_NEUTRAL = 2
SPF_PASS = 3
SPF_FAIL = 4
SPF_SOFTFAIL = 5
SPF_TEMPERROR = 6
SPF_PERMERROR = 7
SPF_RESULT = (
        (SPF_NONE, 'none'),
        (SPF_NEUTRAL, 'neutral'),
        (SPF_PASS, 'pass'),
        (SPF_FAIL, 'fail'),
        (SPF_SOFTFAIL, 'softfail'),
        (SPF_TEMPERROR, 'temperror'),
        (SPF_PERMERROR, 'permerror')
    )

DKIM_NONE = 1
DKIM_PASS = 2
DKIM_FAIL = 3
DKIM_POLICY = 4
DKIM_NEUTRAL = 5
DKIM_TEMPERROR = 6
DKIM_PERMERROR = 7
DKIM_RESULT = (
        (DKIM_NONE, 'none'),
        (DKIM_PASS, 'pass'),
        (DKIM_FAIL, 'fail'),
        (DKIM_POLICY, 'policy'),
        (DKIM_NEUTRAL, 'neutral'),
        (DKIM_TEMPERROR, 'temperror'),
        (DKIM_PERMERROR, 'permerror')
    )

TIME_UNIT_DAY = 1
TIME_UNIT_WEEK = 2
TIME_UNIT_MONTH = 3
TIME_UNIT_YEAR = 4
TIME_UNIT = (
    (None, '-----'),
    (TIME_UNIT_DAY, 'day(s)'),
    (TIME_UNIT_WEEK, 'week(s)'),
    (TIME_UNIT_MONTH, 'month(s)'),
    (TIME_UNIT_YEAR, 'year(s)')
    ) 

DATE_RANGE_TYPE_FIXED = 1
DATE_RANGE_TYPE_VARIABLE = 2
DATE_RANGE_TYPE = (
    (DATE_RANGE_TYPE_FIXED, "fixed"),
    (DATE_RANGE_TYPE_VARIABLE, "variable")
    )