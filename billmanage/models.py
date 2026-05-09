from django.db import models
from django.db.models.fields.json import CaseInsensitiveMixin
from django.utils import timezone
from django.contrib.auth.models import User


class CompanyProfile(models.Model):
    company_name = models.CharField(max_length=200, default='N.K Graphics')
    description = models.TextField(max_length=500, blank=True, default='')
    gst_number = models.CharField(max_length=15, blank=True, default='')
    address = models.TextField(max_length=300, blank=True, default='')
    mobile = models.CharField(max_length=15, blank=True, default='')
    email = models.EmailField(blank=True, default='')
    sidebar_logo = models.ImageField(upload_to='logos/', blank=True, null=True)
    invoice_logo = models.ImageField(upload_to='logos/', blank=True, null=True)
    bank_name = models.CharField(max_length=200, blank=True, default='')
    bank_account_no = models.CharField(max_length=30, blank=True, default='')
    ifsc_code = models.CharField(max_length=20, blank=True, default='')
    bank_branch = models.CharField(max_length=200, blank=True, default='')
    pan_no = models.CharField(max_length=20, blank=True, default='')
    terms_conditions = models.TextField(max_length=500, blank=True, default='Please pay by A/C payee Cheques/Draft only. All Disputes subject to local jurisdiction only.')
    show_profile_tab = models.BooleanField(
        default=True,
        help_text='Toggle to show or hide the Profile tab in the sidebar for users'
    )

    class Meta:
        verbose_name = 'Company Profile'
        verbose_name_plural = 'Company Profile'

    def __str__(self):
        return self.company_name

    def save(self, *args, **kwargs):
        # Enforce singleton — only one profile allowed
        self.pk = 1
        super().save(*args, **kwargs)

# Create your models here.
class bill(models.Model):
    billno = models.IntegerField(primary_key= True, null=False, blank=False)
    date = models.DateField(default=timezone.now, null=False, blank=False)
    recipient = models.TextField(null=False, blank=False, max_length=100)
    address = models.TextField(null=False, blank=False, max_length=200)
    GSTno = models.CharField(null=False, blank=False, max_length=15)
    cgst = models.DecimalField(null=False, blank=False, max_digits=10, decimal_places=2)
    sgst = models.DecimalField(null=False, blank=False, max_digits=10, decimal_places=2)
    total = models.DecimalField(null=False, blank=False, max_digits=12, decimal_places=2)
    grandtotal = models.DecimalField(null=False, blank=False, max_digits=12, decimal_places=2)

class item(models.Model): 
    itemno = models.AutoField(primary_key= True, null=False, blank=False)
    billno = models.ForeignKey(bill, null=False, blank=False, unique=False, on_delete=models.CASCADE)
    itemname = models.TextField(null=False, blank=False, max_length=200)
    hsncode = models.IntegerField(null=False, blank=False)
    qty = models.IntegerField(null=False, blank=False)
    rate = models.DecimalField(null=False, blank=False, max_digits=10, decimal_places=4)
    amount = models.DecimalField(null=False, blank=False, max_digits=10, decimal_places=2)