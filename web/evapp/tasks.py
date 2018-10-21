"""Background tasks, to be used with django-background-tasks.

This module contains callbacks that will be automatically called in a separate
process by Django, more specifically by running the `evennia process_tasks`
command.

"""

from django.core.mail import send_mail

from background_task import background
from background_task.tasks import logger

@background(schedule=5)
def send_email(subject, body, origin, recipients):
    """
    Send an email to the recipient, using Django `send_mail` utility.

    Args:
        subject (str): the email's subject.
        body (str): the email's body.
        origin (str): the origin of the email.
        recipients (str or list of str): the email's recipients.

    Example:
        from web.evapp.tasks import send_email
        send_email("Test subject", "Hi,\n\nThis is a test message.  Great!",
                "noreply@avenew.one", "somebody@gmail.com")

    """
    if isinstance(recipients, basestring):
        recipients = [recipients]

    logger.debug("Trying to send an email to {}.".format(", ".join(recipients)))
    num = send_mail(subject, body, origin, recipients)
    if num == len(recipients):
        logger.info("Email sent to {}.".format(", ".join(recipients)))
    else:
        logger.warning("Couldn't send an email to {}.".format(", ".join(recipients)))
