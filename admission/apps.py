from django.apps import AppConfig
from frontoffice import queue

def callback(ch, method, properties, body):
    print(" [x] Received hello1 %r" % body)

def callback2(ch, method, properties, body):
    print(" [x] Received hello2 %r" % body)

class AdmissionConfig(AppConfig):
    name = 'admission'

    def ready(self):
        queue.listen_queue('hello', callback)
        queue.listen_queue('hello2', callback2)
