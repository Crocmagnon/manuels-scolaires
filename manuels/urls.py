from django.urls import path

from manuels.views import AddBookView, ListBooksView, clear_teacher_view, AddSuppliesView, EditBookView, \
    EditSuppliesView, DeleteBookView, DeleteSuppliesView, ConfirmTeacherView, isbn_api

urlpatterns = [
    path('teacher/<uuid:pk>/add_book', AddBookView.as_view(), name='add_book'),
    path('teacher/<uuid:pk>/add_supplies', AddSuppliesView.as_view(), name='add_supplies'),
    path('teacher/<uuid:pk>', ListBooksView.as_view(), name='list_books'),
    path('teacher/<uuid:teacher_pk>/book/<int:pk>', EditBookView.as_view(), name='edit_book'),
    path('teacher/<uuid:teacher_pk>/book/<int:pk>/delete', DeleteBookView.as_view(), name='delete_book'),
    path('teacher/<uuid:teacher_pk>/supplies/<int:pk>', EditSuppliesView.as_view(), name='edit_supplies'),
    path('teacher/<uuid:teacher_pk>/supplies/<int:pk>/delete', DeleteSuppliesView.as_view(), name='delete_supplies'),
    path('teacher/<uuid:pk>/confirm', ConfirmTeacherView.as_view(), name='confirm_teacher'),
    path('clear', clear_teacher_view, name='clear_teacher'),
    path('isbn_api/<str:isbn>', isbn_api, name='isbn_api'),
]
