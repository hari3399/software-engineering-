from django.contrib import admin
from .models import Client,Complaint,Property,Package,PackageSubscription,Manager,Announcement,LeaseAgreement,Payment
# Register your models here.

admin.site.register(Client)
admin.site.register(Complaint)
admin.site.register(PackageSubscription)
admin.site.register(Property)
admin.site.register(Package)
admin.site.register(Manager)
admin.site.register(Announcement)
admin.site.register(LeaseAgreement)
admin.site.register(Payment)