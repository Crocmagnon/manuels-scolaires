from django.urls import path

from manuels.views import AddBookView, ListBooksView

urlpatterns = [
    path('teacher/<uuid:pk>/add', AddBookView.as_view(), name='add_book'),
    path('teacher/<uuid:pk>/', ListBooksView.as_view(), name='list_books'),
]
