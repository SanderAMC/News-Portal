from django.urls import path
from .views import UserView, upgrade_me, degrade_me, UserUpdate, sub_me, unsub_me

urlpatterns = [
    path('', UserView.as_view()),
    path('upgrade/', upgrade_me, name='user_upgrade'),
    path('degrade/', degrade_me, name='user_degrade'),
    path('edit/<int:pk>/', UserUpdate.as_view(), name='user_edit'),
    path('sub/<int:cat>/', sub_me, name='user_sub'),
    path('unsub/<int:cat>/', unsub_me, name='user_unsub'),
]
