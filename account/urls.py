from django.conf.urls import url
from django.conf import settings
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from . import views
from django.contrib.auth import views as auth_views

# from . import forms

urlpatterns = [
  url(r'^password_reset/$', views.PasswordReset.as_view(), name="password_reset"),
  url(r'^password_reset/sent/$', views.PasswordResetDone.as_view(), name="password_reset_done"),
  url(r'^password_reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', views.PasswordResetConfirm.as_view(), name="password_reset_confirm"),
  url(r'^password_reset/done/$', views.PasswordResetComplete.as_view(), name="password_reset_complete"),
  url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
      views.activate, name='activate'),
  url(r'^logout/$', views.logout_user, name='logout_user'),
  url(r'^login/$', views.login_user, name='login_user'),
  url(r'^register/$', views.register_user, name='register_user'),
  # url(r'^profile/$', views.edit_customer, name='customer_edit'),
]
