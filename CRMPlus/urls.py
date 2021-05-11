from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static

from django.contrib import admin
from django.urls import path, include

from django.contrib.auth import views as auth_views
from common.views import SignUpView, CustomLoginView


admin.site.site_header = "ITSM-Plus CRM"
admin.site.site_title = "ITSM-Plus CRM"


urlpatterns = [

    path('admin/', admin.site.urls),
    path('events/', include('events.urls', namespace="events")),
    path('account/', include('teams.urls', namespace="teams")),
    path('store/', include('store.urls', namespace="store")),
    path('', include('common.urls', namespace="common")),
    path('register/', SignUpView.as_view(), name='register'),
    # path('', HomeView.as_view(), name='dashboard'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(
        next_page='login'
    ), name='logout'),
    
    path(
        'change-password',
        auth_views.PasswordChangeView.as_view(
            template_name = 'registration/change_password.html',
            success_url = '/',
        ),
        name='change-password'
    ),
    #############################
    path('password-reset/',
         auth_views.PasswordResetView.as_view(
             template_name='registration/password_reset.html',
             subject_template_name='registration/password_reset_subject.txt',
             email_template_name='registration/password_reset_email.html',
         ),
         name='password_reset'),

    path('password-reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='registration/password_reset_done.html'
         ),
         name='password_reset_done'),

    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='registration/password_reset_confirm.html'
         ),

         name='password_reset_confirm'),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='registration/password_reset_complete.html'
         ),
         name='password_reset_complete'),

    #############################
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)