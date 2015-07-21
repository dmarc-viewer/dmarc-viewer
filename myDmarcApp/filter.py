"""
Filters:

report_type
    value choices
    field Report.report_type
time_range 
    from
    to
    field Report.date_range_begin
    field Report.date_range_end

last_range
    what    = choice  days | weeks | months | years
    field Report.date_range_begin1
    field Report.date_range_end

report_sender
    value all Report.reporter.org_name
    field Report.reporter.org_name

report_receiver_domain = one to many
    report
ip = one to many | ipv4, ipv6, cidr
raw_dkim_domain = one to many + choices
raw_dkim_result = one to many + choices
multiple_dkim_signatures = models.NullBooleanField()
raw_spf_domain = one to many
raw_spf_result = one to many + choices
aligned_dkim_result = one to many
aligned_spf_result = one to many
dmarc_disposition = one to many
"""