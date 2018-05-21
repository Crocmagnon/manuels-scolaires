import re

from django.core.exceptions import ValidationError
from django.db import models


class Teacher(models.Model):
    class Meta:
        verbose_name = 'enseignant'
        verbose_name_plural = 'enseignants'
    first_name = models.CharField('prénom', max_length=100)
    last_name = models.CharField('nom', max_length=100)
    phone_number = models.CharField('numéro de téléphone', max_length=10)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('add_book', args=[str(self.id)])

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def __str__(self):
        return self.full_name


class Level(models.Model):
    class Meta:
        verbose_name = 'classe'
        verbose_name_plural = 'classes'
    name = models.CharField('nom', max_length=10)

    def __str__(self):
        return self.name


def isbn_validator(value):
    regex = re.compile(r'(\d-?){10,13}X?')
    if not regex.match(value):
        raise ValidationError("%(value)s n'est pas un ISBN valide.", params={'value': value})


class Book(models.Model):
    class Meta:
        verbose_name = 'livre'
        verbose_name_plural = 'livres'

    teacher = models.ForeignKey(verbose_name='enseignant', to=Teacher, on_delete=models.SET_NULL, null=True)
    level = models.ForeignKey(verbose_name='classe', to=Level, on_delete=models.SET_NULL, null=True)
    field = models.CharField('matière', max_length=100)
    title = models.TextField('titre')
    authors = models.TextField('auteurs')
    editor = models.CharField('éditeur', max_length=200)
    collection = models.CharField('collection', max_length=200, blank=True)
    publication_year = models.PositiveIntegerField('année de publication')
    isbn = models.CharField('ISBN/EAN', max_length=20, validators=[isbn_validator])
    price = models.PositiveIntegerField('prix')
    YES_NO_CHOICE = (
        (True, 'Oui'),
        (False, 'Non'),
    )
    previously_acquired = models.BooleanField("manuel acquis précédemment par l'élève", choices=YES_NO_CHOICE, blank=False)

    @property
    def previously_acquired_emoji(self):
        if self.previously_acquired:
            return '✅'
        else:
            return '🚫'

    def __str__(self):
        return f'{self.title} ({self.authors}) - {self.isbn}'
