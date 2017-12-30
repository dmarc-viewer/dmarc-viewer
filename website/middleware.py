"""
<Program Name>
    middleware.py

<Author>
    Lukas Puehringer <luk.puehringer@gmail.com>

<Started>
    Nov 13, 2015

<Copyright>
    See LICENSE for licensing information.

<Purpose>
    Hooks into Django's response processing to inject a bootstrap3
    message block into ajax responses containing messages from djangos
    message services.

    Requires a client side script to display the message block.


    More info at
    https://docs.djangoproject.com/en/1.8/topics/http/middleware/
"""

import json
from django.contrib import messages
from django.template import Template, Context

class BootstrapAjaxMessage(object):
    def process_response(self, request, response):
        if request.is_ajax() and response["Content-Type"] in \
                ["application/javascript", "application/json"]:

            try:
                content = json.loads(response.content)
            except Exception as e:
                return response

            content["ajax_message_block"] = Template(
                    "{% load bootstrap3 %}"
                    "{% bootstrap_messages messages %}").render(
                        Context({
                            "messages": messages.get_messages(request)
                            }
                        )
                    )

            response.content = json.dumps(content)
        return response
