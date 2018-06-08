# DMARC Analysis Views

`DMARC viewer` provides a web editor to create custom `analysis views`.
Analysis views let you analyze particular aspects of your DMARC aggregate
report data, by applying filters that you configure.

Currently, three analysis types are supported. A **map**, showing where
messages came from, a **time line** chart, showing when messages came, and a
**table**, providing you with report details.

## Demo Views
You can also use this command to load some pre-generated `analysis views` to
jump right into analyzing your DMARC reports. The imported views can easily be
modified and extended via the web interface.

```shell
# In the project root
python manage.py loadviews demo/views.json
```

*Note that the demo `analysis views` are optimized for the `DMARC viewer` [demo
reports](REPORTS.md#demo-reports)*.

## Exchange Views (experimental)
Feel free to explore the `loadviews` management command to exchange
`analysis views` created on the web interface.

The following built-in Django management command exports `analysis views`
to a format that can be read by `loadviews`.

```shell
# In the project root
python manage.py dumpdata --indent 2 website.View website.FilterSet \
    website.ReportType website.DateRange website.ReportSender \
    website.ReportReceiverDomain website.SourceIP website.RawDkimDomain \
    website.RawDkimResult website.MultipleDkim website.RawSpfDomain \
    website.RawSpfResult website.AlignedDkimResult \
    website.AlignedSpfResult website.Disposition > path/to/views.json
```
