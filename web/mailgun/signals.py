from anymail.signals import inbound
from django.dispatch import receiver

from web.mailgun.models import EmailMessage

@receiver(inbound)  # add weak=False if inside some other function/class
def handle_inbound(sender, event, esp_name, **kwargs):
    """Store the message in the tiny help desk."""
    message = event.message
    from evennia import set_trace;set_trace()
    email = EmailMessage.objects.create_from_anymail(message)
