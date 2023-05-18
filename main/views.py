from django.shortcuts import render
from .models import (
    Client,
    Property,
    Announcement,
    LeaseAgreement,
    Manager,
    Complaint,
    PackageSubscription,
    Package,
    Payment,
)
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import datetime
from django.shortcuts import render, get_object_or_404
from .forms import AnnouncementForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

from .views_client import calculate_rent


def index(request):
    if request.user.is_authenticated:

        properties = Property.objects.all()
        payments = Payment.objects.filter(date_paid__gte=timezone.now()-timezone.timedelta(days=7))
        complaints = Complaint.objects.filter(date_created__gte=timezone.now()-timezone.timedelta(days=7))
        announcements = Announcement.objects.filter(date_created__gte=timezone.now()-timezone.timedelta(days=7))
        activities = []
        for payment in payments:
            activities.append(f"Payment made by {payment.client.user.first_name} for {payment.lease_agreement.property.property_id}")
        for complaint in complaints:
            activities.append(f"Complaint made by {complaint.leaseAgreement.client.user.first_name} for {complaint.leaseAgreement.property.property_id}")
        for announcement in announcements:
            activities.append(f"Announcement: {announcement.title}")
        context = {
            'properties': properties,
            'activities': activities,
        }
        return render(request, 'manager1/dashboard-home.html', context)
    return render(request, "login.html")


@login_required
def add_client(request):
    if request.method == "POST":
        client_id = request.POST.get("client_id")
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        password = request.POST.get("password")
        address = request.POST.get("address")
        manager = request.user

        # Create User object
        user = User.objects.create_user(client_id, email, password)
        user.first_name = name
        user.save()
        if manager:
            client = Client.objects.create(user=user, phone=phone, pastAddress=address)
            messages.success(request, "Client added successfully!")
            return redirect("index")
        else:
            messages.error(request, "You are not authorized to add a client!")
            return redirect("login")

    return render(request, "manager1/dashboard-add-client.html")


@login_required
def assign_property(request):
    print("files",request.FILES)
    if request.method == "POST":
        
        client_id = request.POST["client_id"]
        property_id = request.POST["property_id"]
        start_date = request.POST["start_date"]
        end_date = request.POST["end_date"]
        agreement = request.FILES["agreement"]
        user = request.user
        manager = Manager.objects.get(user=user)
        print(manager)
        # Check if client exists
        try:
            user = get_object_or_404(User, username=client_id)
            client = get_object_or_404(Client, user=user)
        except Client.DoesNotExist:
            messages.error(
                request, "Client with ID {} does not exist".format(client_id)
            )
            return redirect("assign_property")

        # Check if property exists and is available
        try:
            property = Property.objects.get(property_id=property_id, is_available=True)

        except Property.DoesNotExist:
            messages.error(
                request, "Property with ID {} is not available".format(property_id)
            )
            return redirect("assign_property")

        existing_lease_agreement = LeaseAgreement.objects.filter(
            client=client, property=property
        ).exists()

        if existing_lease_agreement:
            messages.warning(
                request, "This property has already been assigned to the client."
            )
            return redirect("assign_property")

        # Create new lease agreement and assign property to client
        lease_agreement = LeaseAgreement(
            property=property,
            client=client,
            manager=manager,
            start_date=datetime.strptime(start_date, "%Y-%m-%d").date(),
            end_date=datetime.strptime(end_date, "%Y-%m-%d").date(),
            agreement = agreement
        )
        lease_agreement.save()
        property.is_available = False
        property.save()

        messages.success(
            request,
            "Property {} has been assigned to client {}.".format(
                property.property_id, client.user.first_name
            ),
        )
        return redirect("assign_property")

    # Get all available properties
    available_properties = Property.objects.filter(is_available=True)
    available_clients = Client.objects.exclude(
        id__in=LeaseAgreement.objects.values_list("client_id", flat=True)
    )
    print(available_clients)

    context = {
        "available_clients": available_clients,
        "available_properties": available_properties,
    }

    return render(request, "manager1/dashboard-assign-property.html", context)

@login_required
def show_clients(request):
    clients = Client.objects.all()
    context = {"clients": clients}
    return render(request, "manager1/dashboard-clients.html", context)


def announcement(request):
    announcements = Announcement.objects.all()
    context = {"announcements": announcements}
    return render(request, "manager1/dashboard-announcement.html", context)


@login_required
def add_announcement(request):
    if request.method == "POST":
        form = AnnouncementForm(request.POST)
        if form.is_valid():
            announcement = form.save(commit=False)
            print("dfbfgnbfg", announcement)
            announcement.save()
            messages.success(request, "Announcement added successfully!")
            return redirect("announcement")
    else:
        form = AnnouncementForm()
    return render(request, "manager1/dashboard-add-announcement.html", {"form": form})


def change_property_features():
    pass


def complaints(request):
    # or not request.user.is_manager
    if not request.user.is_authenticated:
        return redirect("login")

    complaints = Complaint.objects.all()

    return render(
        request, "manager1/dashboard-complaints.html", {"complaints": complaints}
    )


@login_required
def reply_to_complaint(request, pk):
    if request.method == "POST":
        complaint = Complaint.objects.get(pk=pk)
        reply = request.POST.get("reply")
        complaint.reply = reply
        complaint.resolved = True
        complaint.save()

        return redirect("complaints")

    complaint = Complaint.objects.filter(pk=pk).first()
    print(complaint)

    return render(
        request, "manager1/dashboard-reply-complaint.html", {"complaint": complaint}
    )


def track_payment():
    pass


@login_required
def profile(request):
    user = request.user
    manager = Manager.objects.get(user=user)
    return render(request, "manager1/dashboard-profile.html", {"manager": manager})


def login_view(request):
    if not request.user.is_authenticated:
        if request.method == "POST":
            username = request.POST["username"]
            password = request.POST["password"]
            user = Manager.authenticate(request, username=username, password=password)
            print(user)
            if user is not None:
                login(request, user)
                return redirect("index")
            else:
                messages.error(request, "Invalid username or password.")
        return render(request, "manager1/login.html")
    else:
        return redirect("index")


@login_required
def logout_view(request):
    logout(request)
    return redirect("index")


@login_required
def property_detail(request, pk):
    property = get_object_or_404(Property, pk=pk)
    lease_agreement = LeaseAgreement.objects.filter(property=property).first()
    context = {"property": property, "lease_agreement": lease_agreement}
    return render(request, "manager1/dashboard-property-details.html", context)


@login_required
def add_package(request):
    subscriptions = PackageSubscription.objects.all()
    if request.method == "POST":
        username = request.POST["client"]
        tracking_number = request.POST["tracking_number"]
        description = request.POST["description"]

        user = User.objects.get(username=username)
        client = Client.objects.get(user=user)
        leaseAgreement = LeaseAgreement.objects.filter(client=client).first()
        subscription = PackageSubscription.objects.filter(client=client).first()
        package = Package.objects.create(
            tracking_number=tracking_number,
            description=description,
            leaseAgreement=leaseAgreement,
            subscription=subscription,
        )

        return redirect("add_package")
    else:
        packages = Package.objects.filter(delivered=False).all()
        return render(
            request,
            "manager1/dashboard-add-package.html",
            context={"subscriptions": subscriptions, "packages": packages},
        )



def client_details(request, pk):
    client = get_object_or_404(Client, user__id=pk)
    lease_agreement = LeaseAgreement.objects.filter(client=client).first()
    property = lease_agreement.property if lease_agreement else None
    payments = Payment.objects.filter(lease_agreement=lease_agreement) if lease_agreement else None
    print(payments)
    # Calculate the rent due for the lease agreement
    if lease_agreement:
        rent_due = calculate_rent(lease_agreement)
    else:
        rent_due = 0

    context = {
        'client': client,
        'lease_agreement': lease_agreement,
        'property': property,
        'payments': payments,
        'rent_due': rent_due,
    }
    return render(request, 'manager1/dashboard-client-details.html', context)


def delete_agreement(request,pk):
    print("in delete")
    lease = get_object_or_404(LeaseAgreement, id=pk)
    lease.property.is_available = True
    client_id = lease.client.user.id
    lease.property.save()
    lease.delete()
    return redirect('client_details', pk=client_id)


def payments(request):
    payments = Payment.objects.all().order_by('-date_paid')
    lease_agreements = LeaseAgreement.objects.all()
    pending_leases = []
    for i in lease_agreements:
        rent = calculate_rent(i)
        if(rent>0):
            pending_leases.append([i,rent])
            
    context = {
        'payments': payments,
        'lease_agreements': lease_agreements,
        'pending_leases':pending_leases
    }
    return render(request, 'manager1/dashboard-payment-history.html', context)


def admin_info(request):
    return render(request, "manager1/dashboard-admin-profile.html")
