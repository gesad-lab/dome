from django.db import models

class Entity01(models.Model):
    att_1_text = models.CharField(max_length=200, null=True, blank=True)
    att_2_text = models.CharField(max_length=200, null=True, blank=True)
    att_3_text = models.CharField(max_length=200, null=True, blank=True)
    att_4_text = models.CharField(max_length=200, null=True, blank=True)
    att_5_text = models.CharField(max_length=200, null=True, blank=True)