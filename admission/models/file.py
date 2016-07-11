from django.db import models


def rename(instance, filename):
    return '/'.join(['uploads', instance.name])


class File(models.Model):
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to=rename)

    def __str__(self):
        return self.name
