# vim: expandtab
# -*- coding: utf-8 -*-
from django.dispatch import receiver
from django.db.models import Q
from django.conf import settings

from poleno.mail.signals import message_received
from poleno.utils.translation import translation

from models import Inforequest

@receiver(message_received)
def assign_email_on_message_received(sender, message, **kwargs):
    try:
        q = (Q(unique_email__iexact=r.mail) for r in message.recipient_set.all())
        q = reduce((lambda a, b: a | b), q, Q())
        inforequest = Inforequest.objects.get(q)
        inforequest.undecided_set.add(message)

        if not inforequest.closed:
            with translation(settings.LANGUAGE_CODE):
                inforequest.send_received_email_notification(message)

    except (Inforequest.DoesNotExist, Inforequest.MultipleObjectsReturned):
        pass
