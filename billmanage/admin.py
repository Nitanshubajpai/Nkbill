from django.contrib import admin
from .models import bill, item, CompanyProfile


class billadmin(admin.ModelAdmin):
    list_display = ('billno', 'recipient', 'date', 'address', 'GSTno', 'cgst', 'sgst', 'total', 'grandtotal')

admin.site.register(bill, billadmin)


class itemadmin(admin.ModelAdmin):
    list_display = ('itemno', 'billno', 'itemname', 'hsncode', 'qty', 'rate', 'amount')

admin.site.register(item, itemadmin)


class CompanyProfileAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'gst_number', 'mobile', 'email', 'show_profile_tab')
    fieldsets = (
        ('Company Details', {
            'fields': ('company_name', 'description', 'gst_number', 'address', 'mobile', 'email')
        }),
        ('Bank & Payment Details', {
            'fields': ('bank_name', 'bank_account_no', 'ifsc_code', 'bank_branch', 'pan_no', 'terms_conditions')
        }),
        ('Visibility Settings', {
            'fields': ('show_profile_tab',),
            'description': 'Toggle whether the Profile tab appears in the sidebar for users.'
        }),
    )

    def has_add_permission(self, request):
        return not CompanyProfile.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

admin.site.register(CompanyProfile, CompanyProfileAdmin)