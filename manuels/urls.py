from django.urls import path

from manuels.views import AddBookView, ListBooksView, clear_teacher_view, AddSuppliesView, EditBookView,\
    EditSuppliesView

urlpatterns = [
    path('teacher/<uuid:pk>/add_book', AddBookView.as_view(), name='add_book'),
    path('teacher/<uuid:pk>/add_supplies', AddSuppliesView.as_view(), name='add_supplies'),
    path('teacher/<uuid:pk>', ListBooksView.as_view(), name='list_books'),
    path('teacher/<uuid:teacher_pk>/book/<int:pk>', EditBookView.as_view(), name='edit_book'),
    path('teacher/<uuid:teacher_pk>/supplies/<int:pk>', EditSuppliesView.as_view(), name='edit_supplies'),
    path('clear', clear_teacher_view, name='clear_teacher'),
]
