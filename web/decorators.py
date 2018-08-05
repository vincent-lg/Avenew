"""Additional decorators just for Evennia."""

from django.contrib.auth.decorators import user_passes_test

def ensure_perm(function=None, permission="admin"):
    """Check that the user, if not anonymous, has the corresponding permission.

    If the user is anonymous, or she doesn't have the proper permission,
    redirect to the login URL.

    Args:
        permission (str): the permission to check.

    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and u.check_permstring(permission),
        login_url="/authenticatelogin",
    )
    if function:
        return actual_decorator(function)
    return actual_decorator
