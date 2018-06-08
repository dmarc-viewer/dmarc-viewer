# Quickly deploy DMARC viewer with docker

Make sure that you have [docker installed](https://www.docker.com/get-docker)
on you system and use `docker-compose` to build and run two containers, one for
the Django web app and one for the PostgreSQL database. If you prefer an *old
school* setup, take a look at [`DEPLOYMENT.md`](DEPLOYMENT.md).

## Variables
On your host system, export these environment variables. They will be passed
through to the docker containers to set passwords and
[Django allowed hosts](https://docs.djangoproject.com/en/1.11/ref/settings/#std:setting-ALLOWED_HOSTS).
Don't forget to **replace the values**.

```shell
export DMARC_VIEWER_DB_KEY="**** REPLACE WITH DATABSE PASSWORD ****"
export DMARC_VIEWER_SECRET_KEY="**** REPLACE WITH LARGE RANDOM STRING ****"
export DMARC_VIEWER_ALLOWED_HOSTS="**** REPLACE WITH YOUR DOMAIN OR IP ****"
```

## Docker compose
The following command will create and spin up docker services for the `DMARC
viewer` Django web app and corresponding database. Take a look at
[`docker-compose.yml`](docker-compose.yml), where both services are defined and
[`Dockerfile`](Dockerfile) which lists the specific instructions for the web
app setup.

```shell
# In the root of the project
docker-compose up --build --detach
```
`DMARC viewer` should now be available at
[`http://<your domain or IP>:8000`](http://localhost:8000).

*NOTE: Both services will mount a volume to share files with your host system.
This is useful to persist your database across re-starts of your containers
and to make DMARC aggregate reports on your host system available to the
containers.*


## Import reports and default views
Use `docker exec` to execute commands in your running containers, in order to
parse DMARC aggregate reports into your database and/or import analysis views.


### Analysis Views
The following command creates three default analysis views. Take a look at
[`ANALYSIS_VIEWS.md`](ANALYSIS_VIEWS.md) for more infos.
```shell
docker exec -it dmarc-viewer-app \
    python manage.py loadviews demo/views.json
```

### Parse DMARC aggregate reports
Move your reports to the `.docker-volumes/app` directory. It is mounted inside
the web app's container `WORKDIR/shared` directory. Then run the following
commands to download the required
[`Maxmind GeoLite2 City`](http://geolite.maxmind.com/download/geoip/database)
and parse your DMARC aggregate reports. Don't forget to **choose** the correct
report `--type` and subdirectory. Take a look at [`REPORTS.md`](REPORTS.md) for
more infos.

```shell
# Download and unzip Maxmind Geo IP database
docker exec -it dmarc-viewer-app /bin/ash -c \
    'wget http://geolite.maxmind.com/download/geoip/database/GeoLite2-City.mmdb.gz \
    && gunzip GeoLite2-City.mmdb.gz'

docker exec -it dmarc-viewer-app \
     python manage.py parse --type [in | out] shared/<incoming | outgoing report subdir>
```
*NOTE: You can also mount a directory from your host system that already
contains your DMARC aggregate reports. Take a look at
[`docker volumes`](https://docs.docker.com/storage/volumes/) for further
instructions.*

## Stop and remove containers
The following command stops and removes all running docker containers that have
`dmarc-viewer` in their name, e.g. `dmarc-viewer-db` and `dmarc-viewer-app`.
```shell
docker rm $(docker stop $(docker ps -q -f "name=dmarc-viewer"))
```

## Troubleshooting
Since you specified the `--detach` flag in the `docker-compose up` command
above, logs won't be shown in your host terminal. Use the following command on
your host system to see logs for both or one of the running containers.

```shell
 docker-compose logs [dmarc-viewer-app | dmarc-viewer-db]
```