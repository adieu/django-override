from django.conf import settings

MAKE_OVERRIDE_TAGS_BUILT_IN = getattr(settings, 'MAKE_OVERRIDE_TAGS_BUILT_IN', True)
