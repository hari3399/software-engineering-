from django.db import models
from django.contrib.auth.models import User

class Property(models.Model):
    property_id = models.CharField(max_length=10, unique=True)
    address = models.CharField(max_length=200)
    description = models.TextField()
    is_available = models.BooleanField(default=True)
    manager = models.ForeignKey('Manager', on_delete=models.CASCADE, related_name='properties')
    rent = models.DecimalField(decimal_places=2,max_digits=10,default=10000)

    def __str__(self):
        return self.property_id


class Manager(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='manager_profile')

    def __str__(self):
        return self.user.username
    
    def authenticate(self, username=None, password=None, **kwargs):
        try:
            manager = Manager.objects.get(user__username=username)
            if manager.user.check_password(password):
                print("As manager")
                return manager.user
        except Manager.DoesNotExist:
            return None
    



class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_profile')
    phone = models.CharField(max_length=20)
    pastAddress = models.TextField(max_length=100)

    def __str__(self):
        return self.user.first_name
    
    def authenticate(self, username=None, password=None, **kwargs):
        try:
            client = Client.objects.get(user__username=username)
            if client.user.check_password(password):
                print("As user")
                return client.user
        except Client.DoesNotExist:
            return None


class LeaseAgreement(models.Model):
    client = models.ForeignKey(Client, on_delete=models.PROTECT)
    property = models.ForeignKey(Property, on_delete=models.PROTECT)
    manager = models.ForeignKey(Manager, on_delete=models.PROTECT, related_name='lease_agreements')
    start_date = models.DateField()
    end_date = models.DateField()
    agreement = models.FileField(upload_to='agreements/', blank=True)

    def __str__(self):
        return f"{self.client.user.username} - {self.property.property_id}"
    
class Payment(models.Model):
    PAYMENT_METHODS = (
    ('credit_card', 'Credit Card'),
    ('debit_card', 'Debit Card'),
    ('paypal', 'PayPal'),
    ('cash', 'Cash'),
    ('check', 'Check'),
    )
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='payments')
    lease_agreement = models.ForeignKey(LeaseAgreement, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    date_paid = models.DateTimeField(auto_now_add=True)
    method = models.CharField(max_length=50, choices=PAYMENT_METHODS)

    def __str__(self):
        return f"{self.client} paid {self.amount} on {self.date_paid}"

class Announcement(models.Model):
    title = models.CharField(max_length=200)
    message = models.TextField()
    manager = models.ForeignKey(Manager, on_delete=models.SET_NULL, related_name='announcement',null=True)
    date_created = models.DateTimeField(blank = True, auto_now_add=True)

    def __str__(self):
        return self.title

# anouncement reply

class Complaint(models.Model):
    title = models.CharField(max_length=20)
    description = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='complaints/', blank=True)
    leaseAgreement = models.ForeignKey(LeaseAgreement, on_delete=models.CASCADE, related_name='complaints')
   
    resolved = models.BooleanField(default=False)
    reply = models.TextField(null= True,blank=True)
    def __str__(self):
        return self.description


class Message(models.Model):
    message = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User,on_delete=models.CASCADE, related_name='message')
    def __str__(self):
        return self.user
    

class PackageSubscription(models.Model):
    client = models.OneToOneField(Client, on_delete=models.CASCADE, related_name='package_subscription')
    active = models.BooleanField(default=True)
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(blank=True,null =True)
    def __str__(self):
        return f"{self.client.user.first_name}'s Package Subscription"


class Package(models.Model):
    tracking_number = models.CharField(max_length=50)
    delivered = models.BooleanField(default=False)
    subscription = models.ForeignKey(PackageSubscription, on_delete=models.CASCADE, related_name='packages')
    leaseAgreement = models.ForeignKey(LeaseAgreement, on_delete=models.CASCADE, related_name='package_agreement')
    description = models.TextField(null=True,blank=True)
    def __str__(self):
        return self.tracking_number
