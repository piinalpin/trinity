import json
from django.conf import settings
from event_consumer import message_handler

@message_handler(settings.RABBITMQ_ROUTING_KEY)
def listen_queue(body):
    print(body)
    # CREATE PAYLOAD FROM BODY
    payload = json.loads(body)
    print("==================================");
    # PRINT PAYLOADS
    print(payload)
    # CALL FUNCTION SENDER FROM VIEWS
    from .views import sender
    sender(payload)