from django.urls import path

from manuels.views import AddBookView

urlpatterns = [
    path('teacher/<int:id>/', AddBookView.as_view(), name='add_book')
]
