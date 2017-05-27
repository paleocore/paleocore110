from django.conf.urls import url
from django.conf import settings
from django.contrib.auth.views import password_reset, password_reset_done, password_reset_confirm, password_reset_complete, password_change, password_change_done
from . import views
from django.contrib.auth import views as auth_views

# from . import forms

urlpatterns = [
  # url(r'^password/reset/$', password_reset,
  #       {'template_name': 'itt_web_django_account/recovery.html',
  #        'post_reset_redirect' : '/password/reset/done/',
  #        'email_template_name': 'itt_web_django_account/recovery_email.txt',
  #        'subject_template_name': 'itt_web_django_account/recovery_email_subject.txt',
  #        'from_email': 'password_reset@perx.com',
  #        'password_reset_form': forms.EmailValidationOnForgotPassword,
  #        'html_email_template_name': 'itt_web_django_account/recovery_email_html.txt'
  #        },
  #       name="local_password_reset"),
  # url(r'^password/reset/done/$', password_reset_done,
  #       {'template_name': 'itt_web_django_account/reset_sent.html'}),
  # url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', password_reset_confirm,
  #      {'post_reset_redirect' : '/password/done/',
  #       'template_name': 'itt_web_django_account/reset.html'},
  #      name='password_reset_reset'),
  # url(r'^password/done/$',
  #       password_reset_complete, {'template_name': 'itt_web_django_account/recovery_done.html'}),

  # url(r'^password_change/$',
  #       password_change,
  #       {'post_change_redirect' : '/password_change/done/',
  #        'template_name': 'itt_web_django_account/password_change.html'},
  #       name="password_change"),
  # url(r'^password_change/done/$',
  #       password_change_done,
  #       {'template_name': 'itt_web_django_account/recovery_done.html'},),


  # url(r'^login/$', views.login, name='customer_login'),
  # url(r'^restricted-login/$', views.login, name='customer_login'),
  url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
      views.activate, name='activate'),
  url(r'^logout/$', views.logout_user, name='logout_user'),
  url(r'^login/$', views.login_user, name='login_user'),
  url(r'^register/$', views.register_user, name='register_user'),
  # url(r'^register/finalize/$', views.create_customer, name='customer_create'),
  # url(r'^account/$', views.edit_customer, name='customer_edit'),
]
