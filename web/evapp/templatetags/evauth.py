from django import template

register = template.Library()


@register.filter(name='has_perm')
def has_perm(user, permission):
    """Return whether the specified user has the specified permission."""
    return user.is_authenticated and user.check_permstring(permission)
