from django import forms
from django.core.exceptions import ValidationError

from manuels.models import Book, SuppliesRequirement, Level


class EditBookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['teacher', 'level', 'field', 'no_book', 'see_later', 'title', 'authors', 'editor', 'other_editor',
                  'publication_year', 'isbn', 'price', 'previously_acquired', 'comments', 'consumable']

    no_book = forms.BooleanField(label='Pas de livre pour cette classe/matière', required=False, initial=False)
    see_later = forms.BooleanField(
        label='Voir à la rentrée', help_text="Notamment en cas de désaccord sur l'adoption ou non d'un manuel",
        required=False, initial=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget = forms.TextInput()
        self.fields['authors'].widget = forms.TextInput()
        self.fields['comments'].widget.attrs.update(rows=3)
        self.fields['teacher'].widget.attrs.update({'class': 'custom-select'})
        self.fields['editor'].widget.attrs.update({'class': 'custom-select'})
        self.fields['previously_acquired'].widget.attrs.update({'class': 'custom-select'})
        self.fields['consumable'].widget.attrs.update({'class': 'custom-select'})
        if 'level' in self.fields:
            self.fields['level'].widget.attrs.update({'class': 'custom-select'})

    def clean(self):
        editor = self.cleaned_data['editor']
        other_editor = self.cleaned_data['other_editor']
        title = self.cleaned_data['title']

        if (editor
                and 'autre' in editor.name.lower()
                and not other_editor
                and title not in ['PAS DE LIVRE POUR CETTE CLASSE', 'VOIR À LA RENTRÉE']):
            self.add_error(
                'other_editor',
                ValidationError(
                    "Vous devez préciser l'éditeur si vous n'en choisissez pas un parmi la liste.",
                    code='missing'
                )
            )

    def clean_previously_acquired(self):
        data = self.cleaned_data['previously_acquired']
        if data is None or data == '':
            raise ValidationError('Vous devez choisir une valeur')

        return data


class AddBookForm(EditBookForm):
    class Meta(EditBookForm.Meta):
        fields = ['teacher', 'levels', 'field', 'no_book', 'see_later', 'title', 'authors', 'editor', 'other_editor',
                  'publication_year', 'isbn', 'price', 'previously_acquired', 'comments', 'add_another', 'consumable']

    add_another = forms.BooleanField(label='Ajouter un autre livre', required=False, initial=True)
    levels = forms.ModelMultipleChoiceField(
        queryset=Level.objects.all(),
        label='Classes',
        required=True,
        help_text='Maintenez la touche Ctrl (ou Cmd) enfoncée pour en sélectionner plusieurs.'
    )


class EditSuppliesForm(forms.ModelForm):
    class Meta:
        model = SuppliesRequirement
        fields = ['teacher', 'level', 'fields', 'supplies']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fields'].widget.attrs.update(rows=3)
        self.fields['supplies'].widget.attrs.update(rows=3)
        self.fields['teacher'].widget.attrs.update({'class': 'custom-select'})
        if 'level' in self.fields:
            self.fields['level'].widget.attrs.update({'class': 'custom-select'})


class AddSuppliesForm(EditSuppliesForm):
    class Meta(EditSuppliesForm.Meta):
        fields = ['teacher', 'levels', 'fields', 'supplies']

    add_another = forms.BooleanField(label="Ajouter d'autres fournitures", required=False, initial=True)
    levels = forms.ModelMultipleChoiceField(
        queryset=Level.objects.all(),
        label='Classes',
        required=True,
        help_text='Maintenez la touche Ctrl (ou Cmd) enfoncée pour en sélectionner plusieurs.'
    )
