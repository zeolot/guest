from django.urls import path
from sign import view_if

urlpatterns = [
    # sign system interface
    # ex: /api/add_event/
    path('add_event/', view_if.add_event, name='add_event'),
    # ex: /api/add_guest/
    path('add_guest/', view_if.add_guest, name='add_guest'),
    # ex: /api/get_event_list/
    path('get_event_list/', view_if.get_event_list, name='get_event_list'),
    # ex: /api/get_guest_list/
    # path('get_guest_list/', view_if.get_guest_list, name='get_guest_list'),
    # ex: /api/user_sign/
    path('user_sign/', view_if.user_sign, name='user_sign'),
]
