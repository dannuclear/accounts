from django.db import models

# Create your models here.

class Employee(models.Model):
    id = models.AutoField(primary_key=True)
    # name = models.CharField(max_length=100, blank=False)
    # params = JSONField(blank=True)
    # mark = models.CharField(max_length=100, blank=True)
    # sigma = models.CharField(max_length=50, blank=True)
    # hb = models.CharField(max_length=50, blank=True)
    # hrc = models.CharField(max_length=50, blank=True)
    # group_num = models.CharField(max_length=50, blank=True)

    class Meta:
        db_table = 'employee'