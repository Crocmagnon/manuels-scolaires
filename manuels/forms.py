from django import forms

from manuels.models import Book, SuppliesRequirement


class AddBookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['teacher', 'level', 'field', 'no_book', 'title', 'authors', 'editor', 'publication_year',
                  'isbn', 'price', 'previously_acquired', 'comments', 'add_another']

    add_another = forms.BooleanField(label='Ajouter un autre livre', required=False, initial=True)
    no_book = forms.BooleanField(label='Pas de livre pour cette classe/matière', required=False, initial=False)


class AddSuppliesForm(forms.ModelForm):
    class Meta:
        model = SuppliesRequirement
        exclude = ['done']

    add_another = forms.BooleanField(label="Ajouter d'autres fournitures", required=False, initial=True)
