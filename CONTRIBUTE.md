# Contribute
The `DMARC viewer` backend is implemented using Python
[`Django`](https://docs.djangoproject.com/en/1.11/) and frontend code is
written in vanilla JavaScript using convenience libraries like
[`jQuery`](https://jquery.com/) and [`d3.js`](https://d3js.org/) and the CSS
pre-processor [`SCSS`](https://sass-lang.com/guide).

This document provides instructions on how to set up your development machine
to contribute code to the `DMARC viewer` project.

## Install & Set Up Backend
Please refer to the [deployment instructions](DEPLOYMENT.md) for information on
how to install and set up the `DMARC viewer` backend. The parts that are
relevant for deployment only are marked as *`(deployment only)`*.

The best way to start learning about Django development is by walking through
the excellent [*Writing your first Django
app*](https://docs.djangoproject.com/en/1.11/intro/tutorial01/) tutorial.

During development you might want to enable debug mode, either by flipping
[`settings.DEBUG`](dmarc_viewer/settings.py#L28) to `True` or using an
environment variable, i.e. `export DMARC_VIEWER_DEBUG=True`.

## Use Development Server
Once you have installed and configured the `DMARC viewer` backend and set up
the database you can use Django's development server to serve the web app.
```shell
# In the project root
python manage.py runserver
```

## Static Files
When using Django's development server all frontend code is served from
[`website/static`](website/static). You should set
[`settings.TEMPLATE_SETTINGS.use_dist`](dmarc_viewer/settings.py#L69) to
`False`, in order to serve the original instead of the minified and
concatenated sources. This allows you to work with your browser's [developer
tools](https://developers.google.com/web/tools/chrome-devtools/).

## Frontend Management

`DMARC viewer` uses [`npm`](https://www.npmjs.com/get-npm) for frontend
management. Make sure it's installed on your system.

If you want to make changes to frontend code, take a look at
[`package.json`](package.json), where 3rd party dependencies are defined and
[`Gulpfile.js`](Gulpfile.js), which provides task runners to compile and build
frontend code.

### Install Dependencies
Download and install frontend dependencies defined in `package.json` to
`node_modules`.
```shell
# In the project root
npm install
```

### Compile SCSS
Custom styles should be written to
[`website/static/sass/`](website/static/sass). This command watches the file for
changes and automatically writes corresponding CSS and map files to
[`website/static/css/`](website/static/css).
```shell
# In the project root
gulp watch-scss
```

### Create Dist Files
When modifying frontend code or adding/removing 3rd party dependencies, you
have to create new minified and concatenated dist files.

*Note that you should not modify 3rd party code directly, but rather add,
remove or update it via `package.json`.*
```shell
# In the project root
# Optionally compile the latest DMARC viewer stylesheets
gulp compile-scss

# Create minified and concatenated JS/CSS dist
gulp create-dist
```

