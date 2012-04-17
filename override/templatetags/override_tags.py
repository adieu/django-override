from django.template.base import TemplateSyntaxError, TemplateDoesNotExist
from django.template.base import Library, TextNode
from django.template.loader import get_template_from_string, find_template_loader, make_origin
from django.template.loader_tags import BlockContext, BlockNode, ExtendsNode, BLOCK_CONTEXT_KEY

from django.conf import settings
from override.settings import MAKE_OVERRIDE_TAGS_BUILT_IN


register = Library()


class OverrideError(Exception):
    pass


def find_template(name, dirs=None, override_level=1):
    # Calculate template_source_loaders the first time the function is executed
    # because putting this logic in the module-level namespace may cause
    # circular import errors. See Django ticket #1292.
    from django.template.loader import template_source_loaders
    origin_override_level = override_level
    if template_source_loaders is None:
        loaders = []
        for loader_name in settings.TEMPLATE_LOADERS:
            loader = find_template_loader(loader_name)
            if loader is not None:
                loaders.append(loader)
        template_source_loaders = tuple(loaders)
    for loader in template_source_loaders:
        try:
            times = 1
            while True:
                source, display_name = loader(name, dirs, override_level=times)
                if override_level == 1:
                    return (source, make_origin(display_name, loader, name, dirs))
                else:
                    override_level -= 1
                    times += 1
        except TemplateDoesNotExist:
            pass
    if origin_override_level > 1:
        raise OverrideError("Cannot find the override template")
    else:
        raise TemplateDoesNotExist(name)


def get_template(template_name, override_level=1):
    """
    Returns a compiled Template object for the given template name,
    handling template inheritance recursively.
    """
    template, origin = find_template(template_name, override_level=override_level)
    if not hasattr(template, 'render'):
        # template needs to be compiled
        template = get_template_from_string(template, origin, template_name)
    return template


class OverrideNode(ExtendsNode):
    must_be_first = MAKE_OVERRIDE_TAGS_BUILT_IN

    def __repr__(self):
        if self.parent_name_expr:
            return "<OverrideNode: override %s>" % self.parent_name_expr.token
        return '<OverrideNode: override "%s">' % self.parent_name

    def get_parent(self, context):
        if self.parent_name_expr:
            self.parent_name = self.parent_name_expr.resolve(context)
        parent = self.parent_name
        if not parent:
            error_msg = "Invalid template name in 'extends' tag: %r." % parent
            if self.parent_name_expr:
                error_msg += " Got this from the '%s' variable." % self.parent_name_expr.token
            raise TemplateSyntaxError(error_msg)
        if not getattr(self, 'override_level', None):
            self.override_level = 1
        if hasattr(parent, 'render'):
            return parent  # parent is a Template object
        return get_template(parent, self.override_level + 1)

    def render(self, context):
        compiled_parent = self.get_parent(context)

        if BLOCK_CONTEXT_KEY not in context.render_context:
            context.render_context[BLOCK_CONTEXT_KEY] = BlockContext()
        block_context = context.render_context[BLOCK_CONTEXT_KEY]

        # Add the block nodes from this node to the block context
        block_context.add_blocks(self.blocks)

        # If this block's parent doesn't have an extends node it is the root,
        # and its block nodes also need to be added to the block context.
        for node in compiled_parent.nodelist:
            # The ExtendsNode has to be the first non-text node.
            if not isinstance(node, TextNode):
                if isinstance(node, OverrideNode):
                    if node.parent_name != self.parent_name:
                        raise OverrideError("Parent template and current template overrides different template.")
                    node.override_level = self.override_level + 1
                if not isinstance(node, ExtendsNode):
                    blocks = dict([(n.name, n) for n in
                                   compiled_parent.nodelist.get_nodes_by_type(BlockNode)])
                    block_context.add_blocks(blocks)
                break

        # Call Template._render explicitly so the parser context stays
        # the same.
        return compiled_parent._render(context)


def do_override(parser, token):
    """
    Signal that this template overrides a parent template.

    This tag may be used in two ways: ``{% override "base" %}`` (with quotes)
    uses the literal value "base" as the name of the parent template to extend,
    or ``{% override variable %}`` uses the value of ``variable`` as either the
    name of the parent template to override (if it evaluates to a string) or as
    the parent tempate itelf (if it evaluates to a Template object).
    """
    bits = token.split_contents()
    if len(bits) != 2:
        raise TemplateSyntaxError("'%s' takes one argument" % bits[0])
    parent_name, parent_name_expr = None, None
    if bits[1][0] in ('"', "'") and bits[1][-1] == bits[1][0]:
        parent_name = bits[1][1:-1]
    else:
        parent_name_expr = parser.compile_filter(bits[1])
    nodelist = parser.parse()
    if nodelist.get_nodes_by_type(OverrideNode):
        raise TemplateSyntaxError("'%s' cannot appear more than once in the same template" % bits[0])
    return OverrideNode(nodelist, parent_name, parent_name_expr)


register.tag('override', do_override)
