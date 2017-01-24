import simplejson as json
from django.contrib import messages
from django.template import Template, Context

class BootstrapAjaxMessage(object):
    def process_response(self, request, response):
        if request.is_ajax():
            if response['Content-Type'] in ["application/javascript", "application/json"]:
                try:
                    content = json.loads(response.content)
                except Exception, e:
                    return response

                content['ajax_message_block'] = Template(
                            "{% load bootstrap3 %}{% bootstrap_messages messages %}"
                            ).render(Context({"messages": messages.get_messages(request)}))

                response.content = json.dumps(content)
        return response