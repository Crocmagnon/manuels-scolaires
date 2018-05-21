from django.urls import path

from manuels.views import AddBookView, ListBooksView

urlpatterns = [
    path('teacher/<int:id>/add', AddBookView.as_view(), name='add_book'),
    path('teacher/<int:id>/', ListBooksView.as_view(), name='list_books'),
]
