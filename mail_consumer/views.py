from django.shortcuts import render
from trinity import settings
from django.core.mail import EmailMultiAlternatives

def sender(data):
    try:
        subject = data['subject']
        body = data['text']
        from_email = settings.DEFAULT_FROM_EMAIL
        to = data['to']
        html_body = data['html']
        messages = EmailMultiAlternatives(subject, body, from_email, to)
        messages.attach_alternative(html_body, "text/html")
        messages.attach_file(data['file'], 'image/jpg')
        messages.send()
        print("Email has been sent!")
    except:
        print("Can not sent email, something wrong!")
