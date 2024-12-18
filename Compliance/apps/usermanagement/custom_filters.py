
from django import template
register = template.Library()

# Your custom tags and filters go here


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)