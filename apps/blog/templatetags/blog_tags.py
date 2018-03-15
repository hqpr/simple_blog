from django.template import Library
from django.utils.safestring import mark_safe

register = Library()


@register.simple_tag
def category_list(qs):
    if qs:
        spippet_list = []
        for category in qs:
            snippet = """<a href="/blog/category/{id}/">{title}</a>""".format(id=category.id, title=category.title)
            spippet_list.append(snippet)
        return mark_safe(', '.join(spippet_list))
    else:
        return ''
