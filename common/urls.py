from django.urls import path, include

from common.views import ThreadView, DialogView

app_name = "common"


urlpatterns = [
    path('', DialogView.as_view(), name='dialog'),
    path('chat/<str:username>/', ThreadView.as_view(), name='chat'),
]