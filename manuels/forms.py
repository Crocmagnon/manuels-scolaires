from django import forms

from manuels.models import Book, SuppliesRequirement


class AddBookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = '__all__'

    add_another = forms.BooleanField(label='Ajouter un autre livre', required=False, initial=True)


class AddSuppliesForm(forms.ModelForm):
    class Meta:
        model = SuppliesRequirement
        fields = '__all__'

    add_another = forms.BooleanField(label="Ajouter d'autres fournitures", required=False, initial=True)
