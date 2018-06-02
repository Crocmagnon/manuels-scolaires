from django import forms

from manuels.models import Book, SuppliesRequirement


class EditBookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['teacher', 'level', 'field', 'no_book', 'title', 'authors', 'editor', 'publication_year',
                  'isbn', 'price', 'previously_acquired', 'comments']

    no_book = forms.BooleanField(label='Pas de livre pour cette classe/matière', required=False, initial=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget = forms.TextInput()
        self.fields['authors'].widget = forms.TextInput()
        self.fields['comments'].widget.attrs.update(rows=3)


class AddBookForm(EditBookForm):
    class Meta(EditBookForm.Meta):
        fields = ['teacher', 'level', 'field', 'no_book', 'title', 'authors', 'editor', 'publication_year',
                  'isbn', 'price', 'previously_acquired', 'comments', 'add_another']

    add_another = forms.BooleanField(label='Ajouter un autre livre', required=False, initial=True)


class EditSuppliesForm(forms.ModelForm):
    class Meta:
        model = SuppliesRequirement
        fields = ['teacher', 'level', 'fields', 'supplies']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fields'].widget.attrs.update(rows=3)
        self.fields['supplies'].widget.attrs.update(rows=3)


class AddSuppliesForm(EditSuppliesForm):
    class Meta(EditSuppliesForm.Meta):
        pass

    add_another = forms.BooleanField(label="Ajouter d'autres fournitures", required=False, initial=True)
