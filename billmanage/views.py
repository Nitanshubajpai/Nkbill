from django.shortcuts import render, redirect
from .models import bill, item, CompanyProfile
from datetime import datetime
import calendar
import json
# Create your views here.
from django.core.paginator import Paginator, EmptyPage,PageNotAnInteger

def dashboard(request):    
    amount = 0.0
    today = datetime.today()
    month = calendar.month_name[int(today.month)]
    billobj = bill.objects.filter(date__month=today.month)
    for bills in billobj:
        amount = amount+float(bills.grandtotal)
    
    amount = round(amount,2)
    count = len(billobj)

    billobj = bill.objects.all().order_by('-date')[:10]

    return render(request, 'billmanage/dashboard.html', {'bills':billobj, 'count': count, 'amount': amount, 'month':month})


def _build_recipient_dict(bill_objs):
    d = {}
    for b in bill_objs:
        d[f'{b.recipient} | {b.address}'] = {'address': b.address, 'gstno': b.GSTno, 'name': b.recipient}
    return d

def _build_items_dict():
    d = {}
    for it in item.objects.all().order_by('-itemno'):
        if it.itemname not in d:
            d[it.itemname] = {'hsncode': str(it.hsncode), 'rate': str(it.rate)}
    return d

def addbill(request):
    bill_objs = bill.objects.all().order_by('-billno')
    billno = bill_objs.first().billno + 1 if bill_objs else 1
    reciept_names_dict = _build_recipient_dict(bill_objs)
    items_dict_json = json.dumps(_build_items_dict())
    return render(request, 'billmanage/addbill.html', {
        'billno': billno,
        'reciept_names_dict': reciept_names_dict,
        'items_dict_json': items_dict_json,
    })

def addbill_submitted(request):
    if request.method == "POST":
        amount = []
        amountwithtax = []
        total = 0
        grandtotal = 0
        gst =float(request.POST['CGST'])+float(request.POST['SGST'])
        rate = request.POST.getlist('rate[]',False)
        qty = request.POST.getlist('qty[]',False)
        itname = request.POST.getlist('ItemName[]',False)
        hsn = request.POST.getlist('hsn[]',False)
        billno = request.POST.get('invoice_no',False)

        for i in range(len(rate)):
            amt = float(rate[i])*float(qty[i])
            total += amt
            gmt = amt+(amt*gst/100)
            grandtotal += gmt
            amount.append(amt)
            amountwithtax.append(gmt)

        if not billno:
            try:
                billno = bill.objects.all().order_by('-billno').first().billno + 1
            except:
                billno = 1
 
        newbill = bill(
            recipient = request.POST['rname'],
            address = request.POST['address'],
            date = request.POST['date'],
            billno = request.POST.get('invoice_number',billno),
            GSTno = request.POST['gst'],
            cgst = float(request.POST['CGST']),
            sgst = float(request.POST['SGST']),
            total = total,
            grandtotal = grandtotal,
        )
        newbill.save()
        
        for i in range(len(rate)):
            newitem = item(
                itemname = itname[i],
                hsncode = hsn[i],
                qty = qty[i],
                rate = rate[i],
                amount = amount[i],
                billno = bill.objects.get(billno=billno),
            )
            newitem.save()
        return invoice(request, billno)
    else:
        return render(request, 'billmanage/addbill.html')
   
def records(request):
    if request.method=='POST':
        startingdate = request.POST['start']
        billno = request.POST['billno']
        enddate = request.POST.get('end') or datetime.now()
        if billno:
            billobj = bill.objects.filter(billno=billno)

        elif startingdate:
            
            billobj = bill.objects.filter(date__range=[startingdate, enddate]).order_by('-date')

        else:
            
            billobj = bill.objects.all().order_by('-billno')

        
    else:
        billobj = bill.objects.all().order_by('-billno')

    paginator = Paginator(billobj, 10)
    page_number = request.GET.get('page')
    try:
        bills = paginator.page(page_number)
    except PageNotAnInteger:
        bills = paginator.page(1)
    except EmptyPage:
        bills = paginator.page(paginator.num_pages)
    return render(request, 'billmanage/records.html', {'bills': bills})

def invoice(request, billno):
    billobj = bill.objects.get(billno=billno)
    itemobj = item.objects.filter(billno=billno)
    amount = billobj.grandtotal
    amountwithouttax = billobj.total
    amount = float(amount)
    amountwithouttax = float(amountwithouttax)
    gst = round((amount - amountwithouttax), 2)
    sgst = round(float(billobj.sgst)*amountwithouttax/100,2)
    cgst = round(float(billobj.cgst)*amountwithouttax/100,2)
    rs = str(amount).split(".")[0]
    absolute_amt = round(amount,0)
    round_off = "{:.2f}".format(round(absolute_amt-amount,2))
    if round(absolute_amt-amount,2)>0:
        round_off = f"+{round_off}"
    rs = num2words(int(absolute_amt))
    
    return render(request, 'billmanage/invoice.html', {'bill': billobj, 'items': itemobj, 'rs': rs, 'absolute_amt': absolute_amt,'round_off':round_off, 'gst': gst,'cgst':cgst,'sgst':sgst, 'range':6})


def delete(request, billno):
    deletebill = bill.objects.get(billno=billno)
    deletebill.delete()
    return records(request)


def editbill(request, billno):
    bill_obj = bill.objects.get(billno=billno)
    items_obj = item.objects.filter(billno=billno)
    bill_objs = bill.objects.all().order_by('-billno')
    reciept_names_dict = _build_recipient_dict(bill_objs)
    items_dict_json = json.dumps(_build_items_dict())
    return render(request, 'billmanage/editbill.html', {
        'bill': bill_obj,
        'items': items_obj,
        'reciept_names_dict': reciept_names_dict,
        'items_dict_json': items_dict_json,
    })


def editbill_submitted(request, billno):
    if request.method == 'POST':
        bill_obj = bill.objects.get(billno=billno)
        item.objects.filter(billno=billno).delete()

        total = 0
        grandtotal = 0
        gst = float(request.POST['CGST']) + float(request.POST['SGST'])
        rate_list = request.POST.getlist('rate[]', [])
        qty_list = request.POST.getlist('qty[]', [])
        itname = request.POST.getlist('ItemName[]', [])
        hsn = request.POST.getlist('hsn[]', [])
        amounts = []

        for i in range(len(rate_list)):
            amt = float(rate_list[i]) * float(qty_list[i])
            total += amt
            grandtotal += amt + (amt * gst / 100)
            amounts.append(amt)

        bill_obj.recipient = request.POST['rname']
        bill_obj.address = request.POST['address']
        bill_obj.date = request.POST['date']
        bill_obj.GSTno = request.POST['gst']
        bill_obj.cgst = float(request.POST['CGST'])
        bill_obj.sgst = float(request.POST['SGST'])
        bill_obj.total = total
        bill_obj.grandtotal = grandtotal
        bill_obj.save()

        for i in range(len(rate_list)):
            item(
                itemname=itname[i],
                hsncode=hsn[i],
                qty=qty_list[i],
                rate=rate_list[i],
                amount=amounts[i],
                billno=bill_obj,
            ).save()

        return invoice(request, billno)
    return redirect('records')


def profile(request):
    profile_obj, _ = CompanyProfile.objects.get_or_create(pk=1)

    if request.method == 'POST':
        profile_obj.company_name = request.POST.get('company_name', profile_obj.company_name)
        profile_obj.description = request.POST.get('description', profile_obj.description)
        profile_obj.gst_number = request.POST.get('gst_number', profile_obj.gst_number)
        profile_obj.address = request.POST.get('address', profile_obj.address)
        profile_obj.mobile = request.POST.get('mobile', profile_obj.mobile)
        profile_obj.email = request.POST.get('email', profile_obj.email)
        profile_obj.bank_name = request.POST.get('bank_name', profile_obj.bank_name)
        profile_obj.bank_account_no = request.POST.get('bank_account_no', profile_obj.bank_account_no)
        profile_obj.ifsc_code = request.POST.get('ifsc_code', profile_obj.ifsc_code)
        profile_obj.bank_branch = request.POST.get('bank_branch', profile_obj.bank_branch)
        profile_obj.pan_no = request.POST.get('pan_no', profile_obj.pan_no)
        profile_obj.terms_conditions = request.POST.get('terms_conditions', profile_obj.terms_conditions)
        if 'sidebar_logo' in request.FILES:
            profile_obj.sidebar_logo = request.FILES['sidebar_logo']
        if 'invoice_logo' in request.FILES:
            profile_obj.invoice_logo = request.FILES['invoice_logo']
        profile_obj.save()
        return redirect('profile')

    return render(request, 'billmanage/profile.html', {'profile': profile_obj})

def num2words(num):
    under_20 = ['Zero','One','Two','Three','Four','Five','Six','Seven','Eight','Nine','Ten','Eleven','Twelve','Thirteen','Fourteen','Fifteen','Sixteen','Seventeen','Eighteen','Nineteen']
    tens = ['Twenty','Thirty','Forty','Fifty','Sixty','Seventy','Eighty','Ninety']
    above_100 = {100: 'Hundred',1000:'Thousand', 100000:'Lakhs', 10000000:'Crores'}

    if num < 20:
         return under_20[(int)(num)]

    if num < 100:
        return tens[(int)(num/10)-2] + ('' if num%10==0 else ' ' + under_20[(int)(num%10)])

    # find the appropriate pivot - 'Million' in 3,603,550, or 'Thousand' in 603,550
    pivot = max([key for key in above_100.keys() if key <= num])

    return num2words((int)(num/pivot)) + ' ' + above_100[pivot] + ('' if num%pivot==0 else ' ' + num2words(num%pivot))
