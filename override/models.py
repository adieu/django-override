from override.settings import MAKE_OVERRIDE_TAGS_BUILT_IN


if MAKE_OVERRIDE_TAGS_BUILT_IN:
    from django.template.base import add_to_builtins
    add_to_builtins('override.templatetags.override_tags')
