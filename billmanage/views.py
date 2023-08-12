from django.shortcuts import render
from .models import bill, item
from datetime import datetime
import calendar
# Create your views here.
from django.core.paginator import Paginator, EmptyPage,PageNotAnInteger

def dashboard(request):    
    amount = 0.0
    today = datetime.today()
    month = calendar.month_name[int(today.month)]
    billobj = bill.objects.filter(date__month=today.month)
    for bills in billobj:
        amount = amount+float(bills.grandtotal)
    
    count = len(billobj)

    billobj = bill.objects.all().order_by('-date')[:10]

    return render(request, 'billmanage/dashboard.html', {'bills':billobj, 'count': count, 'amount': amount, 'month':month})


def addbill(request):
    bill_objs = bill.objects.all().order_by('-billno')
    billno = bill_objs.first().billno + 1
    reciept_names_dict = dict()
    
    for bill_obj in bill_objs:
        reciept_names_dict[f'{bill_obj.recipient} | {bill_obj.address}'] = {'address':bill_obj.address, 'gstno':bill_obj.GSTno, 'name':bill_obj.recipient}

    return render(request, 'billmanage/addbill.html', {'billno': billno, 'reciept_names_dict': reciept_names_dict})

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

        for i in range(len(rate)):
            amt = float(rate[i])*float(qty[i])
            total += amt
            gmt = amt+(amt*gst/100)
            grandtotal += gmt
            amount.append(amt)
            amountwithtax.append(gmt)

        billno = bill.objects.all().order_by('-billno').first().billno + 1
 
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
