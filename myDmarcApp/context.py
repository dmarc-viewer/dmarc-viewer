from django.conf import settings as settings

def options(request):
    """
    Returns TEMPLATE_SETTINGS from settings to make them available in template.
    """
    return { "TEMPLATE_SETTINGS": settings.TEMPLATE_SETTINGS}