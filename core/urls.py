from django.conf.urls import url, include
from django.conf import settings
from django.conf.urls.static import static
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    url(r'^$',views.home,name='home'),
    url(r'^register/$',views.signup_view,name='user_register'),
    url(r'^stud/(?P<pk>\d+)/logout/$',views.user_logout, name='user_logout'),
    url(r'^stud/$',views.stud_login,name='stud_login'),
    url(r'^stud/(?P<pk>\d+)/$',views.stud_home, name='stud_home'),
    url(r'^startup/(?P<pk>\d+)/(?P<path>((\w+?)/?([\w]+\.pdf)))$',views.pdf_view, name='pdf_view'),
    url(r'^startup/(?P<pk>\d+)/logout/$',views.user_logout, name='user_logout'),
    url(r'^startup/(?P<pk>\d+)/$',views.startup_home, name='startup_home'),
    url(r'^startup/$',views.stp_login,name='stp_login'),
]

