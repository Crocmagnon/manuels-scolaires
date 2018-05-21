from django.urls import path

from manuels.views import AddBookView, ListBooksView, clear_teacher_view

urlpatterns = [
    path('teacher/<uuid:pk>/add', AddBookView.as_view(), name='add_book'),
    path('teacher/<uuid:pk>', ListBooksView.as_view(), name='list_books'),
    path('clear', clear_teacher_view, name='clear_teacher'),
]
