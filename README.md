# DMARC viewer

`DMARC viewer` is a [Django](https://docs.djangoproject.com/en/1.11/)-based web
application that lets you visually analyze [DMARC aggregate
reports](https://dmarc.org/), providing unique insights into how your mailing
domains are used and abused. Moreover, with `DMARC viewer` you can create and
store custom `analysis views` that filter reports based on the criteria you are
interested in.


## Configure DNS
To **receive DMARC aggregate reports** for your domains all you need to do is
to add a DMARC entry to your DNS records. Read [*"Anatomy of a DMARC resource
record in the DNS"*](https://dmarc.org/overview/) for initial guidance.


## Start Analyzing!
To analyze your own DMARC aggregate reports you need to deploy an instance of
`DMARC viewer`. Follow these steps to get you started:

 1. [Deploy](DEPLOYMENT.md) your own instance of `DMARC viewer`,
 1. [import](REPORTS.md) DMARC aggregate reports,
 1. and [create `analysis views`](ANALYSIS_VIEWS.md).

Alternatively you can deploy [`DMARC viewer` using docker](DOCKER.md).

You'll find further usage instructions on the
[`DMARC viewer` help page](website/templates/website/help.html) and plenty of
contextual help throughout the website (look out for "**`?`**" symbols).

## Contribute
`DMARC viewer` is an open source project [*(MIT)*](LICENSE). If you want a new
feature, discover a bug or have some general feedback, feel free to file an
[*issue*](https://github.com/dmarc-viewer/dmarc-viewer/issues). You can also
[*fork*](https://help.github.com/articles/fork-a-repo/) this repository,
[**start coding**](CONTRIBUTE.md) and submit [*pull
requests*](https://github.com/dmarc-viewer/dmarc-viewer/pulls).
