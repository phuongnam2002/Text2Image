from django.db import models

# Create your models here.

class Log(models.Model):
    vi_text = models.CharField(max_length=10000, blank=True)
    en_text = models.CharField(max_length=10000, blank=True)
    image = models.ImageField(upload_to ='media/')

    def __str__(self) -> str:
        return self.vi_text