from django.urls import path
from .views import SearchWordView, index

urlpatterns = [
    path('', index, name='index'),
    path('search/', SearchWordView.as_view(), name='search_word'),
    #path('history/', SearchHistoryView.as_view(), name='search_history'),
]

