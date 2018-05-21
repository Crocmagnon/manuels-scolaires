from django import forms

from manuels.models import Book, Teacher


class AddBookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = '__all__'

    add_another = forms.BooleanField(label='Ajouter un autre livre', required=False)
