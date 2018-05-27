"""
<Program Name>
    decorators.py

<Author>
    Lukas Puehringer <luk.puehringer@gmail.com>

<Started>
    May, 2018

<Copyright>
    See LICENSE for licensing information.

<Purpose>
    Module for view decorators (Python function wrappers).

    See https://docs.djangoproject.com/en/1.11/topics/http/decorators/
    for more information about view decorators in Django.

"""
import json
from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect
from django.http import HttpResponse

def disabled_in_demo(message):
    """View decorator to disable POST requests and two special cases of GET
    requests and instead show the passed message to the user using Django's
    `messages` framework. """
    def decorator(func):
        @wraps(func)
        def inner(request, *args, **kwargs):
            # Disable POST and two special cases of GET requests
            if (request.method == "POST" or  func.__name__ == "clone" or
                    func.__name__ == "delete"):

                messages.add_message(request, messages.WARNING, message)

                # If it was an ajax request we have to return an ajax response
                # otherwise we redirect to the page the request came from.
                if request.is_ajax():
                    return HttpResponse(json.dumps({}),
                            content_type="application/json")

                else:
                    return redirect(request.META['HTTP_REFERER'])

            return func(request, *args, **kwargs)
        return inner
    return decorator
