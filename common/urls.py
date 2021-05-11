from django.urls import path, include
from django.views.decorators.cache import cache_page
from common.views import ThreadView, DialogView

app_name = "common"


urlpatterns = [
    path('/', cache_page(10)(DialogView.as_view()), name='dialog'),
    path('chat/<str:username>/', cache_page(5)(ThreadView.as_view()), name='chat'),
]