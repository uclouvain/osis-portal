from django.apps import AppConfig
from frontoffice import queue

def callback(ch, method, properties, body):
    print(" [x] Received hello1 %r" % body)

def callback2(ch, method, properties, body):
    print(" [x] Received hello2 %r" % body)

class AdmissionConfig(AppConfig):
    name = 'admission'

    def ready(self):
        # if django.core.exceptions.AppRegistryNotReady: Apps aren't loaded yet.
        # ===> This exception says that there is an error in the implementation of method ready(self) !!
        queue.listen_queue("queue1")
        queue.listen_queue("queue2")
