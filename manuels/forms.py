from django import forms

from manuels.models import Book, Teacher


class AddBookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = '__all__'
