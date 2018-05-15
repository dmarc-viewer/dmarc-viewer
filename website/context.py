"""
<Program Name>
    context.py

<Author>
    Lukas Puehringer <luk.puehringer@gmail.com>

<Started>
    Nov 19, 2015

<Copyright>
    See LICENSE for licensing information.

<Purpose>
    A simple template context processor to add additional data to the template
    context.

    Once a context processor is registered in the settings file, e.g.:
    ```
    # in settings.py
    TEMPLATES = [
        {
        ...
            'OPTIONS': {
                'context_processors': [
                    ...,
                    'website.context.options'
                ],
            },
        },
    ]
    ```

    you can access the variable returned by the context processor function in
    a template, e.g.:

    ```
    <!-- in base.html -->
    {% if TEMPLATE_SETTINGS.use_minified %}
    ```

    More info at:
    https://docs.djangoproject.com/en/1.11/ref/templates/api/#writing-your-own-context-processors

"""
from django.conf import settings

def options(request):
    """Adds TEMPLATE_SETTINGS variable initialized in settings.py
    to the template context. """
    return { "TEMPLATE_SETTINGS" : settings.TEMPLATE_SETTINGS}