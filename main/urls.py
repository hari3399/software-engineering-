from . import views
from . import views_client
from django.urls import path

urlpatterns = [
    path('', views.index, name='index'),
    path('add_client', views.add_client, name='add_client'),
    path('assign_property', views.assign_property, name='assign_property'),
    path('add_announcement', views.add_announcement, name='add_announcement'),
    path('announcement', views.announcement, name='announcement'),
    path('change_property_features', views.change_property_features, name='change_property_features'),
    path('reply_to_complaint/<int:pk>', views.reply_to_complaint, name='reply_to_complaint'),
    path('complaints', views.complaints, name='complaints'),
    path('track_payment', views.track_payment, name='track_payment'),
    path('profile', views.profile, name='profile'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('property_detail/<int:pk>', views.property_detail, name='property_detail'),
    path('show_clients',views.show_clients,name='show_clients'),
    path('show_clients/<int:pk>',views.client_details,name='client_details'),
    path('delete_agreement/<int:pk>',views.delete_agreement,name='delete_agreement'),
    path('add_package',views.add_package,name='add_package'),
    path('payments',views.payments,name='payments'),
    path('admin_info',views.admin_info,name='admin_info'),


    # client views
    path('user', views_client.index_user , name='index_user'),
    path('user/profile', views_client.profile_user, name='profile_user'),
    path('user/login', views_client.login_user, name='login_user'),
    path('user/logout', views_client.logout_user, name='logout_user'),
    path('user/login', views_client.rent_details, name='rent_details'),
    path('user/complaints', views_client.complaints, name='complaints_user'),
    path('user/add_complaint', views_client.add_complaint, name='add_complaint'),
    path('user/property_detail', views_client.property_detail, name='client_property_detail'),
    path('user/show_package', views_client.show_package, name='show_package'),
    path('user/subscribe_package', views_client.subscribe_package, name='subscribe_package'),
    path('user/pickup_package/<int:pk>', views_client.pickup_package, name='pickup_package'),
    path('user/make_payment', views_client.make_payment, name='make_payment'),
    path('user/payment_history', views_client.payment_history, name='payment_history'),
    path('user/download_agreement/<int:pk>', views_client.download_agreement, name='download_agreement'),
    path('user/contact_us', views_client.contact_us, name='contact_us'),
    path('user/update_password', views_client.update_password, name='update_password'),
]