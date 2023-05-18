from django.shortcuts import render
from .models import (
    Client,
    Property,
    Announcement,
    LeaseAgreement,
    Manager,
    Complaint,
    Package,
    PackageSubscription,
    Payment,
)
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import datetime,timedelta
from django.shortcuts import render, get_object_or_404
from .forms import AnnouncementForm,CustomPasswordChangeForm
from django.contrib.auth import authenticate, login, logout
from .forms_client import ComplaintForm
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.http import HttpResponse
from django.db.models import Sum
from django.contrib.auth import update_session_auth_hash


def index_user(request):
    if request.user.is_authenticated:

        week_ago = datetime.now() - timedelta(days=7)
        announcements = Announcement.objects.filter(date_created__gte=week_ago).order_by("-date_created")
        return render(
            request, "client1/dashboard-home.html", {"announcements": announcements}
        )
    else:
        return redirect("login_user")
        # Client is not authenticated, redirect to login page or show login form


@login_required
def profile_user(request):
    client = get_object_or_404(Client, user=request.user)
    lease_agreement = (
        client.leaseagreement_set.first()
    )  # assuming client has only one lease agreement
    return render(
        request,
        "client1/dashboard-profile.html",
        {"client": client, "lease_agreement": lease_agreement},
    )


def login_user(request):
    if not request.user.is_authenticated:

        if request.method == "POST":
            username = request.POST["username"]
            password = request.POST["password"]
            user = Client.authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("index_user")
            else:
                messages.error(request, "Invalid username or password.")
        return render(request, "client1/login.html")
    else:
        return redirect("index_user")


@login_required
def logout_user(request):
    logout(request)
    return redirect("index_user")


@login_required
def property_detail(request):
    client = Client.objects.get(user=request.user)
    property = Property.objects.filter
    lease_agreement = (
        LeaseAgreement.objects.filter(client=client).order_by("-start_date").first()
    )
    agreement_file = lease_agreement.agreement
    download =False
    if agreement_file:
        download = True
    return render(request, 'client1/dashboard-property-detail.html', {'lease_agreement': lease_agreement,'download':download})

def download_agreement(request,pk):
    lease_agreement = (
        LeaseAgreement.objects.get(pk =pk)
    )
    with open(lease_agreement.agreement.path, 'rb') as f:
        response = HttpResponse(f.read(), content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename=' + lease_agreement.agreement.name
        return response


def rent_details():
    pass


def subscribe_package(request):
    client = Client.objects.get(user=request.user)
    lease_agreement = LeaseAgreement.objects.filter(client=client).first()
    end_date = lease_agreement.end_date
    subscribed_package = PackageSubscription.objects.create(
        client=client, end_date=end_date
    )

    return redirect("show_package")


def show_package(request):
    client = Client.objects.get(user=request.user)
    lease_agreement = LeaseAgreement.objects.filter(client=client).first()
    subscribed_package = PackageSubscription.objects.filter(client=client).first()
    if subscribed_package:
        packages = Package.objects.filter(delivered=False, leaseAgreement= lease_agreement)
        return render(request, "client1/dashboard-package.html", {"packages": packages,"subscribe": True})
    else:
        return render(request, "client1/dashboard-package.html", {"subscribe": False})


def complaints(request):
    # or not request.user.is_manager
    if not request.user.is_authenticated:
        return redirect("login")

    client = Client.objects.get(user=request.user)
    leaseAgreement = LeaseAgreement.objects.get(client=client)
    complaints = (
        Complaint.objects.filter(leaseAgreement=leaseAgreement)
        .order_by("-date_created")
        .all()
    )

    return render(
        request, "client1/dashboard-complaints.html", {"complaints": complaints}
    )


def add_complaint(request):
    if request.method == "POST":
        form = ComplaintForm(request.POST, request.FILES)
        if form.is_valid():
            client = Client.objects.get(user=request.user)
            complaint = form.save(commit=False)
            leaseAgreement = LeaseAgreement.objects.get(client=client)
            complaint.leaseAgreement = leaseAgreement
            complaint.save()
            messages.success(request, "Complaint added successfully.")
            return redirect("index_user")
    else:
        form = ComplaintForm()
    return render(request, "client1/dashboard-add-complaint.html", {"form": form})


@login_required
def pickup_package(request, pk):
    package = Package.objects.get(pk=pk)
    if package.delivered == False:
        package.delivered = True
        package.save()
    return redirect("show_package")


@login_required
def make_payment(request):
    client = Client.objects.get(user=request.user)
    lease_agreement = get_object_or_404(LeaseAgreement, client=client)
    if request.method == "POST":
        amount = request.POST.get("amount")
        method = request.POST.get("method")
        card_number = request.POST.get("card_number")
        card_name = request.POST.get("cardholder_name")
        card_date = request.POST.get("expiry_month_year")
        card_cvv = request.POST.get("cvv")
        if not amount:
            messages.error(request, "Please enter the payment amount.")

        elif method in ["credit_card", "debit_card"] and (not card_number or not card_name or not card_date or not card_cvv):
            messages.error(request, "Please fill in all the card details.")
        
        elif len(card_number) != 16:
            messages.error(request, "Invalid card number. Please enter a 16 digit card number.")
        
        elif len(card_cvv) != 3:
            messages.error(request, "Invalid CVV. Please enter a 3 digit CVV.")
        
        elif card_date:
            card_date = card_date.split('/')
            print(card_date)
            if len(card_date) == 2:
                expiry_month, expiry_year = card_date[0], card_date[1]
                if int(expiry_month) not in range(1, 13):
                    messages.error(request, "Invalid expiry month. Please enter a valid month.")
                elif int(expiry_year) < datetime.now().year:
                    messages.error(request, "Card has already expired.")
                elif int(expiry_year) == datetime.now().year and int(expiry_month) < datetime.now().month:
                    messages.error(request, "Card has already expired.")

        elif(calculate_rent(lease_agreement)<float(amount)):
            messages.success(request, "Entered amount is higher then pending payment")
            return HttpResponseRedirect(reverse("make_payment"))
        
        Payment.objects.create(
            client=lease_agreement.client,
            lease_agreement=lease_agreement,
            amount=amount,
            method=method,
        )
        messages.success(request, "Payment made successfully.")
        return HttpResponseRedirect(reverse("make_payment"))
    
    remaining_amount = calculate_rent(lease_agreement)
    context = {
        "lease_agreement": lease_agreement,
        "remaining_amount": remaining_amount,
        "payment_methods": Payment.PAYMENT_METHODS,
    }
    return render(request, "client1/dashboard-make-payment.html", context)


def payment_history(request):
    client = Client.objects.get(user=request.user)
    lease_agreement = get_object_or_404(LeaseAgreement, client=client)

    paid_payments = Payment.objects.filter(
        client=client, lease_agreement=lease_agreement
    ).all()
    context = {
        "lease_agreement": lease_agreement,
        "paid_payments": paid_payments,
    }
    return render(request, "client1/dashboard-payment-history.html", context)


def calculate_rent(lease):
    rent = lease.property.rent
    start_date = lease.start_date
    end_date = lease.end_date
    paid_payments = Payment.objects.filter(
       lease_agreement=lease
    ).all()

    paid_amount = 0
    for i in paid_payments:
        paid_amount += i.amount
    
    # calculate the number of months between the start date and the current month's 5th date
    now = datetime.now()
    current_month = now.month
    current_year = now.year
    current_day = now.day
    if current_day < 5:
        current_month -= 1
        if current_month == 0:
            current_month = 12
            current_year -= 1
    months_diff = (current_year - start_date.year) * 12 + (current_month - start_date.month)
    
    rent_due = (months_diff * rent) - paid_amount
    rent_due = max(0, rent_due) # make sure rent_due is non-negative

    return rent_due


def contact_us(request):
    client = Client.objects.get(user=request.user)
    lease_agreement = get_object_or_404(LeaseAgreement, client=client)

    manager = lease_agreement.manager
    return render(request, "client1/deshboard-manager-profile.html", {'manager':manager})




@login_required
def update_password(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Update the session hash to keep the user logged in after password change
            messages.success(request, 'Your password was successfully updated!')
            return redirect('profile_user')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomPasswordChangeForm(request.user)
    return render(request, 'client1/deshboard-change-password.html', {'form': form})


