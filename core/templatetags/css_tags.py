from django import template
from django.forms import BoundField
from django.utils.safestring import SafeString

register = template.Library()


@register.filter(name='add_classes')
def add_classes(obj: BoundField, arg: SafeString):
    """
    Add provided classes to form field
    """
    css_classes = obj.field.widget.attrs.get('class', '')
    # check if class is set or empty and split its content to list (or init list)
    if css_classes:
        css_classes = css_classes.split(' ')
    else:
        css_classes = []
    # prepare new classes to list
    args = arg.split(' ')
    for a in args:
        if a not in css_classes:
            css_classes.append(a)
    # join back to single string
    return obj.as_widget(attrs={'class': ' '.join(css_classes)})
