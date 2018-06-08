# Installation & Deployment Instructions

The following instructions were tested on a fresh [Debian
*stretch*](https://wiki.debian.org/DebianStretch) machine.

Please make sure to replace passwords, etc. when copy-pasting.

Most of below instructions also apply when setting up a machine for `DMARC
viewer` development. Parts that are only relevant for deployment are marked with
*`(deployment only)`*.

## Install System Packages
```shell
# Update your package manager and packages
sudo apt-get update && sudo apt-get upgrade

# Install git (only used to fetch the `DMARC viewer` sources)
sudo apt-get install git

# Install Python 2.7 and Python package manager
sudo apt-get install python-dev python-pip

# Install PostgreSQL and bindings (see more notes on dbs below)
sudo apt-get install libpq-dev postgresql postgresql-contrib

# Install Apache2 (webserver)
# (deployment only)
sudo apt-get install apache2 libapache2-mod-wsgi

# Install Cairo2 (used to export graphs)
sudo apt-get install libcairo2-dev
```

## Install Python Virtualenv
[`Virtualenv`](https://virtualenv.pypa.io/en/stable/) and the handy
[`Virtualenvwrapper`](http://virtualenvwrapper.readthedocs.io/) provide a great
way to isolate Python applications and packages on your system. It's a good
idea to use them.
```shell
sudo pip install virtualenvwrapper
```

## Setup PostgreSQL DB
Note that `DMARC viewer` is completely database agnostic, that is you can use
any database that [seems right to you](http://howfuckedismydatabase.com/) and
is [supported by Django](https://docs.djangoproject.com/en/1.11/ref/databases/).

Here we create our db and db user with the names specified in
[`settings.py`](dmarc_viewer/settings.py#L115-L123) and then drop onto a `psql`
shell, where we grant the user the required permissions. You will be asked for
a password for your db user. Choose a strong one and remember it!
```shell
sudo -Hu postgres bash -c "createdb dmarc_viewer_db && createuser -P dmarc_viewer_db && psql"
```
```shell
GRANT ALL PRIVILEGES ON DATABASE dmarc_viewer_db TO dmarc_viewer_db;
\q
```

## Create Static Files Directory
*`(deployment only)`*

Django recommends serving static files from a different directory than the
source code repo. We create it here, **temporarily** giving it full
permissions. If you want to create it somewhere else, you have to change the
corresponding [`STATIC_ROOT` setting](dmarc_viewer/settings.py#L156).
```shell
sudo mkdir -p -m777 /var/www/dmarc_viewer/static/
```

## Create Unprivileged User (optional)
*`(deployment only)`*

You don't have to create a dedicated user, but users give you good permission
separation and they are easily added and removed. Also, some of the webserver
setup instructions assume that you have a user `dmarcviewer` with a home
directory `/home/dmarcviewer`.
```
sudo adduser dmarcviewer
sudo -iu dmarcviewer
```

## Setup Virtualenv
`virtualenvwrapper` needs some per-login setup before creating and working with
`virtualenvs`. So it's a good idea to store the commands in your bash
configuration file, which is done with the following snippet.
```shell
# Prepare setup
cat >> ~/.bashrc <<EOL
export WORKON_HOME=~/.virtualenvs
source /usr/local/bin/virtualenvwrapper.sh
EOL

# Perform setup
source ~/.bashrc

# Create virtualenv
mkvirtualenv dmarc-viewer-env
```

## Configure `DMARC viewer` Settings
You can use these environment variables to set your application secret key, db
key and to whitelist the host or IP address that is allowed to serve your
instance of `DMARC viewer`. The environment variables are loaded in
[`settings.py`](dmarc_viewer/settings.py), which if you prefer, can be patched
directly as well.
```shell
export DMARC_VIEWER_SECRET_KEY="**** REPLACE WITH LONG RANDOM STRING ****"
export DMARC_VIEWER_DB_KEY="**** REPLACE WITH DB PASSWORD CREATED ABOVE ****"
export DMARC_VIEWER_ALLOWED_HOSTS="**** REPLACE WITH YOUR DOMAIN OR IP ****"
```

## Install `DMARC viewer`
These commands will fetch the `DMARC viewer` source code repository, install
the required Python dependencies, populate the db model, and copy all static
files to the directory created above.
```
git clone https://github.com/dmarc-viewer/dmarc-viewer.git
cd dmarc-viewer
pip install -r requirements.txt
python manage.py makemigrations website
python manage.py migrate
python manage.py collectstatic
```

## Create WSGI Config File
*`(deployment only)`*

[`WSGI`](http://www.wsgi.org/) is the bridge between the webserver and the
Python/Django-based `DMARC viewer` application. This snippet will create the
required configuration file with above defined environment variables so that
the `DMARC viewer` application can access them from its
[`settings.py`](dmarc_viewer/settings.py).
```shell
cat > /home/dmarcviewer/dmarc-viewer/dmarc_viewer/wsgi_prod.py <<EOL
##############################################################################
# CAUTION: CONTAINS SENSITIVE DATA! DO NOT CHECK INTO YOUR VERSION CONTROL!
##############################################################################
import os
from django.core.wsgi import get_wsgi_application

os.environ["DJANGO_SETTINGS_MODULE"] = "dmarc_viewer.settings"
os.environ["DMARC_VIEWER_SECRET_KEY"] = "${DMARC_VIEWER_SECRET_KEY}"
os.environ["DMARC_VIEWER_DB_KEY"] = "${DMARC_VIEWER_DB_KEY}"
os.environ["DMARC_VIEWER_ALLOWED_HOSTS"] = "${DMARC_VIEWER_ALLOWED_HOSTS}"

application = get_wsgi_application()
EOL
```

## Log Out (optional)
*`(deployment only)`*

If you created an unprivileged user as recommended above you have to change
back to a privileged user now in order to configure the webserver.
```
exit
sudo -iu root
```

## Defuse Static Files Directory
*`(deployment only)`*

First of all we change ownership and remove some permissions from the static
files directory, which we needed only briefly so that the unprivileged
`dmarcviewer` user could copy over the static files.
```shell
chmod 755 /var/www/dmarc_viewer/static/
chown -R root:root /var/www/dmarc_viewer/static/
```

## Configure Webserver
*`(deployment only)`*

*Deploying Django with `Apache` and `mod_wsgi` is a tried and tested way to get
Django into production.* You can read more about it in the Django
[deployment howto](https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/modwsgi/)
and [deployment checklist](https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/).

Note that `DMARC viewer` has no built-in authorization model, hence you might
want to look elsewhere to make sure that only you can access your DMARC
aggregate report data. You can set up your instance in a private network or use
`Apache` [access control](https://httpd.apache.org/docs/2.4/howto/access.html),
[authentication and
authorization](https://httpd.apache.org/docs/2.4/howto/auth.html) and/or
[encryption](https://httpd.apache.org/docs/2.4/ssl/ssl_howto.html).

Below configuration sets up a vanilla `Apache virtual host` that will serve
`DMARC viewer` over non-encrypted `HTTP`.


### Define Server Name
First replace this string with the domain or IP address, where your instance
should be reached at and export the environment variable. It will be used below
to create you `virtual host` configuration file.
```shell
export DMARC_VIEWER_SERVER_NAME="**** REPLACE WITH YOUR DOMAIN ****"
```

### Create Virtual Host Config File
This snippet contains all the virtual host configuration you need to fire up
your `DMARC viewer` instance. If you didn't follow all of above instructions,
you might need to change the user name and/or some of the paths.
```shell
cat > /etc/apache2/sites-available/dmarc-viewer.conf <<EOL
<VirtualHost *:80>
    ServerName ${DMARC_VIEWER_SERVER_NAME}

    Alias /static/ /var/www/dmarc_viewer/static/
    <Directory /var/www/dmarc_viewer/static>
        Require all granted
    </Directory>

    WSGIDaemonProcess dmarcviewer user=dmarcviewer processes=5 threads=10 python-home=/home/dmarcviewer/.virtualenvs/dmarc-viewer-env python-path=/home/dmarcviewer/dmarc-viewer
    WSGIProcessGroup dmarcviewer

    WSGIScriptAlias / /home/dmarcviewer/dmarc-viewer/dmarc_viewer/wsgi_prod.py process-group=dmarcviewer
    <Directory /home/dmarcviewer/dmarc-viewer/dmarc_viewer>
        <Files wsgi_prod.py>
            Require all granted
        </Files>
    </Directory>
</VirtualHost>
EOL
```
### Load Config
Once you have enabled the configuration file and started apache, you should be
able to serve DMARC viewer at the server name specified above.
```shell
a2ensite dmarc-viewer.conf
# NOTE: Alternatively, if already running, use `systemctl reload apache2`
systemctl start apache2
```

## Troubleshooting
*`(deployment only)`*

If things don't work, `Apache`'s error log might help you to troubleshoot the
problem.
```shell
tail /var/log/apache2/error.log
```




