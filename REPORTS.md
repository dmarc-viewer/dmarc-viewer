# DMARC Aggregate Reports

This document explains how to import DMARC aggregate reports into the `DMARC
viewer` database.

## Install Maxmind GeoLite2
`DMARC viewer`'s report parser uses the [Maxmind's GeoLite2
City](http://geolite.maxmind.com/download/geoip/database) database to retrieve
geo information for IP addresses. Download [`GeoLite2-City.mmdb.gz`](http://geo
lite.maxmind.com/download/geoip/database/GeoLite2-City.mmdb.gz) to the project
root (keep it up to date), in order to retrieve geo information when parsing
your DMARC reports.
```shell
# In the project root
wget http://geolite.maxmind.com/download/geoip/database/GeoLite2-City.mmdb.gz
gunzip GeoLite2-City.mmdb.gz
```
You can also point [`settings.GEO_LITE2_CITY_DB`](dmarc_viewer/settings.py#L30)
to an existing `GeoLite2-City` db on your system.


## Import Reports
`DMARC viewer` distinguishes between **incoming** and **outgoing** reports.
Incoming reports you receive from foreign domains *(reporters)*, based on
e-mail messages the reporters received purportedly from you. Outgoing reports
on the other hand you send to foreign domains *(reportees)*, based on e-mail
messages that you received purportedly from them.

To analyze reports you need to use the provided parser management command and
parse your reports into your database, specifying whether you are importing
incoming our outgoing reports.
```shell
# In the project root
python manage.py parse [--type (in|out)] (<dmarc-aggregate-report>.xml | dir/to/reports) ...
```


## Demo Reports
If you don't have DMARC aggregate reports at hand but can't wait to try out
`DMARC viewer`, use the following snippet to generate demo DMARC aggregate
reports and import them into the `DMARC viewer` database.

Reports are generated for three domains, i.e. *your* domain and two
*foreign* domains, which makes four daily report exchanges, i.e. two that you
send (outgoing) and two that you receive (incoming) per day, over a whole year
(2017).
```shell
# In the project root

# Install DMARC demo data scripts
git clone https://github.com/lukpueh/dmarc-demo-data
pip install -r dmarc-demo-data/requirements.txt

# Generate demo data
(cd dmarc-demo-data && python demo_reports.py)

# Import demo data into DB
python manage.py parse --type in dmarc-demo-data/reports/incoming
python manage.py parse --type out dmarc-demo-data/reports/outgoing
```