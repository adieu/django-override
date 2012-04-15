from django.conf import settings
from django.template.loaders.filesystem import Loader as DjangoFileSystemLoader
from django.template.loaders.app_directories import Loader as DjangoAppDirectoriesLoader
from django.template.loader import make_origin, get_template_from_string
from django.template.base import TemplateDoesNotExist


class OverrideLoaderMixin(object):
    """docstring for OverrideLoaderMixin"""
    def __call__(self, template_name, template_dirs=None, override_level=1):
        return self.load_template(template_name, template_dirs, override_level)

    def load_template(self, template_name, template_dirs=None, override_level=1):
        source, display_name = self.load_template_source(template_name, template_dirs, override_level)
        origin = make_origin(display_name, self.load_template_source, template_name, template_dirs)
        try:
            template = get_template_from_string(source, origin, template_name)
            return template, None
        except TemplateDoesNotExist:
            # If compiling the template we found raises TemplateDoesNotExist, back off to
            # returning the source and display name for the template we were asked to load.
            # This allows for correct identification (later) of the actual template that does
            # not exist.
            return source, display_name
        

class FileSystemLoader(OverrideLoaderMixin, DjangoFileSystemLoader):
    def load_template_source(self, template_name, template_dirs=None, override_level=1):
        tried = []
        for filepath in self.get_template_sources(template_name, template_dirs):
            try:
                file = open(filepath)
                try:
                    result = (file.read().decode(settings.FILE_CHARSET), filepath)
                finally:
                    file.close()
                if override_level == 1:
                    return result
                else:
                    override_level -= 1
            except IOError:
                tried.append(filepath)
        if tried:
            error_msg = "Tried %s" % tried
        else:
            error_msg = "Your TEMPLATE_DIRS setting is empty. Change it to point to at least one template directory."
        raise TemplateDoesNotExist(error_msg)


class AppDirectoriesLoader(OverrideLoaderMixin, DjangoAppDirectoriesLoader):
    def load_template_source(self, template_name, template_dirs=None, override_level=1):
        for filepath in self.get_template_sources(template_name, template_dirs):
            try:
                file = open(filepath)
                try:
                    result = (file.read().decode(settings.FILE_CHARSET), filepath)
                finally:
                    file.close()
                if override_level == 1:
                    return result
                else:
                    override_level -= 1
            except IOError:
                pass
        raise TemplateDoesNotExist(template_name)
