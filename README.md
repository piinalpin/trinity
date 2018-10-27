Django Mail Sender
====================

This project name is Trinity 

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

* Text Editor
* Terminal, Commnand Prompt or Windows PowerShell

### Dependencies

* [Erlang (Open Telecom Platform)](https://www.erlang.org/)
* [RabbitMQ (Message Broker)](https://www.rabbitmq.com/)
* [Pyhton 3.6 (Base Compiler)](https://www.python.org/)
* Virtualenv (Virtual Environtment)

- - -

Steps
================================

A step by step series of examples that tell you how to get a development env running.

### Install Django 2.1

~~~~
> pip install Django==2.1.2
~~~~

### Create project and application in Django

~~~~
> django-admin startproject your_project
> django-admin startapp your_apps
~~~~

### Create virtual environtment in root directory on your project

~~~~
> virtualenv env
~~~~

It will be automatically create virtual environtment (env) on your project.

### Install library celery and celery-message-consumer

~~~~
> pip install celery
> pip install celery-message-consumer
~~~~

Virtualenv will install automatically AMQP from celery to connect with RabbitMQ.

### Edit django base settings

##### Change DEBUG to False and ALLOWED_HOST to localhost

```
#!python
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['localhost']
```

##### Add email setup

```
#!python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_HOST_USER = <Your_Username>
EMAIL_HOST_PASSWORD = <Your_Password>
EMAIL_PORT = 587
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = "Info KS-Linux UAD <info@kslinux.tif.uad.ac.id>"
```

##### Add rabbitmq setup

```
#!python
# RabbitMQ Setup
RABBIT_HOST = "localhost"
RABBIT_PORT = "5672"
RABBIT_VIRTUAL_HOST = "/"
RABBITMQ_ROUTING_KEY = "mail_consumer"
# RabbitMQ Credentials
RABBIT_USERNAME = "guest"
RABBIT_PASSWORD = "guest"
```

##### Add installed application

```
#!python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django',
    'mail_consumer',
]
```

##### Create logging

```
#!python
# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue'
        }
    },
    'formatters': {
        'main_formatter': {
            'format': '%(levelname)s:%(name)s: %(message)s '
                      '(%(asctime)s; %(filename)s:%(lineno)d)',
            'datefmt': "%Y-%m-%d %H:%M:%S",
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'level': 'DEBUG',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'main_formatter',
        },
        'production_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/main.log',
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 7,
            'formatter': 'main_formatter',
            'filters': ['require_debug_false'],
        },
        'debug_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/main_debug.log',
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 7,
            'formatter': 'main_formatter',
            'filters': ['require_debug_true'],
        },
        'null': {
            "class": 'logging.NullHandler',
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins', 'console'],
            'level': 'ERROR',
            'propagate': True,
        },
        'django': {
            'handlers': ['null', ],
        },
        'py.warnings': {
            'handlers': ['null', ],
        },
        '': {
            'handlers': ['console', 'production_file', 'debug_file'],
            'level': "DEBUG",
        },
    }
}
]
```

##### Create queue to rabbitmq and celery bypass log

```
#!python
# ADD CELERY BYPASS LOG
CELERYD_HIJACK_ROOT_LOGGER = False

# CREATE QUEUE TO RABBITMQ
EXCHANGES = {
    # a reference name for this config, used when attaching handlers
    'default': {
        'name': 'data',  # actual name of exchange in RabbitMQ
        'type': 'mail_consumer',  # an AMQP exchange type
    },
}
```

### Create function send in views

```
#!python
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
```

### Create task listener to rabbitmq queue

```
#!python
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
```

### Create celery worker

```
#!python
# IMPORT LIBRARY TO CONNECT WITH RABBITMQ
from __future__ import absolute_import
import os
from celery import Celery
from celery.signals import setup_logging
from event_consumer.handlers import AMQPRetryConsumerStep

from trinity.settings import LOGGING
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trinity.settings')

# CREATE APP CELERY
app = Celery('trinity')
app.steps['consumer'].add(AMQPRetryConsumerStep)

# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')
# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

# CREATE TASKS
@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))

@setup_logging.connect()
def configure_logging(sender=None, **kwargs):
    import logging.config
    logging.config.dictConfig(LOGGING)
```

### Create test send message to broker with pika
#### Create file outside the project
#### Create virtual environtment
#### Install library pika to create connection with broker

~~~~
> pip install pika
~~~~

#### Create file wihich is send message to the broker

```
#!python
import pika
import sys

# GET CONNECTION TO RABBITMQ
connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue='mail_consumer', durable=True)

message = """
{
    "subject": "Registration of Training Asynchronous Programming",
    "text": "Congratulations you have registered as participants of asynchronous programming. We have attached a ticket registration, please download.",
    "html":"<h2>Congratulations you have registered as participants of asynchronous programming. We have attached a ticket registration, please download.</h2>",
    "to": ["<Your_Destination_Email>"],
    "file": "<Attachment>"
}
"""
# PUSH MESSAGE TO QUEUE MAIL_CONSUMER
channel.basic_publish(exchange='',
                      routing_key='mail_consumer', # This is routing key which must be the same as celery routing key
                      body=message,
                      properties=pika.BasicProperties(
                         delivery_mode = 2, # make message persistent
                      ))
print(" [x] Sent %r" % message)
connection.close()
```

### Run the test send message

~~~~
> python filename_testSender.py
~~~~

### Run celery project

~~~~
> pip celery worker -A your_project.celery.app
~~~~

	
[lexers]: http://pygments.org/docs/lexers/
[fireball]: http://daringfireball.net/projects/markdown/ 
[Pygments]: http://pygments.org/ 
[Extra]: http://michelf.ca/projects/php-markdown/extra/
[id]: http://example.com/  "Optional Title Here"
[BBmarkup]: https://confluence.atlassian.com/x/xTAvEw