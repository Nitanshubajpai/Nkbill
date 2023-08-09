from django.db import models
from django.db.models.fields.json import CaseInsensitiveMixin
from django.utils import timezone
from django.contrib.auth.models import User

# Create your models here.
class bill(models.Model):
    billno = models.IntegerField(primary_key= True, null=False, blank=False)
    date = models.DateField(default=timezone.now, null=False, blank=False)
    recipient = models.TextField(null=False, blank=False, max_length=100)
    address = models.TextField(null=False, blank=False, max_length=200)
    GSTno = models.CharField(null=False, blank=False, max_length=15)
    cgst = models.IntegerField(null=False, blank=False)
    sgst = models.IntegerField(null=False, blank=False)
    total = models.DecimalField(null=False, blank=False, max_digits=12, decimal_places=2)
    grandtotal = models.DecimalField(null=False, blank=False, max_digits=12, decimal_places=2)

class item(models.Model): 
    itemno = models.AutoField(primary_key= True, null=False, blank=False)
    billno = models.ForeignKey(bill, null=False, blank=False, unique=False, on_delete=models.CASCADE)
    itemname = models.TextField(null=False, blank=False, max_length=200)
    hsncode = models.IntegerField(null=False, blank=False)
    qty = models.IntegerField(null=False, blank=False)
    rate = models.DecimalField(null=False, blank=False, max_digits=10, decimal_places=2)
    amount = models.DecimalField(null=False, blank=False, max_digits=10, decimal_places=2)