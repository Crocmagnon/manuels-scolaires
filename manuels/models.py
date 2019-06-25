import os
import re

import uuid as uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.db import models
from django.template.loader import render_to_string
from django.urls import reverse


class BaseModel(models.Model):
    class Meta:
        abstract = True

    created_at = models.DateTimeField('créé le', auto_now_add=True)
    updated_at = models.DateTimeField('mis à jour le', auto_now=True)


def phone_validator(value):
    regex = re.compile(r'^\d{10}$')
    if not regex.match(value):
        raise ValidationError(
            "%(value)s n'est pas un numéro de téléphone valide. Format attendu : 10 chiffres.",
            params={'value': value}
        )


class Teacher(BaseModel):
    class Meta:
        verbose_name = 'coordonnateur'
        verbose_name_plural = 'coordonnateurs'
        ordering = ['first_name']

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField('prénom', max_length=100)
    last_name = models.CharField('nom', max_length=100)
    phone_number = models.CharField(
        'numéro de téléphone',
        help_text="En cas d'urgence, 10 chiffres.",
        max_length=10,
        validators=[phone_validator]
    )
    email = models.EmailField(
        'adresse email',
        help_text='Utilisée pour vous transmettre votre lien personnel',
        unique=True
    )
    has_confirmed_list = models.BooleanField(
        'a confirmé les listes',
        default=False,
        blank=True
    )

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('list_books', kwargs={'pk': str(self.pk)})

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def __str__(self):
        return self.full_name

    def send_link(self, request):
        dest = self.email
        link = request.build_absolute_uri(reverse('list_books', args=[str(self.pk)]))
        msg = EmailMultiAlternatives(
            subject='Gestion des manuels scolaires',
            body=f'Bonjour {self.first_name},\n'
                 f'Voici votre lien pour la gestion des manuels scolaires : {link}',
            from_email=settings.SERVER_EMAIL,
            to=[dest],
        )
        reply_to = [os.getenv('REPLY_TO')]
        if reply_to:
            msg.reply_to = reply_to
        msg.attach_alternative(
            render_to_string('manuels/emails_link.html', {'link': link, 'teacher': self}), "text/html"
        )
        msg.send()

    def send_confirmation(self, request):
        dest = settings.LIBRARIAN_EMAILS
        link = request.build_absolute_uri(reverse('home_page'))
        msg = EmailMultiAlternatives(
            subject="Gestion des manuels scolaires - Confirmation d'un coordonnateur",
            body=f'Bonjour,\n'
                 f'{self.first_name} a confirmé ses listes sur {link}',
            from_email=settings.SERVER_EMAIL,
            to=dest,
        )
        reply_to = [os.getenv('REPLY_TO')]
        if reply_to:
            msg.reply_to = reply_to
        msg.attach_alternative(
            render_to_string('manuels/emails_confirmation.html', {'link': link, 'teacher': self}), "text/html"
        )
        msg.send()


class Level(BaseModel):
    class Meta:
        verbose_name = 'classe'
        verbose_name_plural = 'classes'
        ordering = ['order', 'name']

    name = models.CharField('nom', max_length=50)
    order = models.IntegerField('ordre', default=0)

    def __str__(self):
        return self.name


class Editor(BaseModel):
    class Meta:
        verbose_name = 'éditeur'
        verbose_name_plural = 'éditeurs'
        ordering = ['name']

    name = models.CharField('nom', max_length=100)

    def __str__(self):
        return self.name


def isbn_validator(value):
    regex = re.compile(r'(\d-?){10,13}X?')
    if not regex.match(value):
        raise ValidationError("%(value)s n'est pas un ISBN valide.", params={'value': value})


def positive_float_validator(value):
    try:
        value = float(value)
    except ValueError:
        raise ValidationError("%(value)s doit être un nombre décimal")

    if value < 0:
        raise ValidationError("%(value)s doit être un nombre positif")


class Book(BaseModel):
    class Meta:
        verbose_name = 'livre'
        verbose_name_plural = 'livres'

    teacher = models.ForeignKey(verbose_name='coordonnateur', to=Teacher, on_delete=models.PROTECT, null=True)
    level = models.ForeignKey(verbose_name='classe', to=Level, on_delete=models.PROTECT, null=True)
    field = models.CharField('discipline', max_length=200)
    title = models.TextField('titre')
    authors = models.TextField('auteurs')
    editor = models.ForeignKey(verbose_name='éditeur', to=Editor, on_delete=models.PROTECT, null=True)
    other_editor = models.CharField(verbose_name='préciser', max_length=100, blank=True)
    publication_year = models.PositiveIntegerField('année de publication')
    isbn = models.CharField(
        'ISBN/EAN',
        max_length=20,
        help_text="Format attendu : 10 ou 13 chiffres, éventuellement séparés par des tirets et éventuellement "
                  "suivis de la lettre <code>X</code>. La recherche sur Decitre ne fonctionnera qu'avec un code ISBN à "
                  "13 chiffres (ou EAN)",
        validators=[isbn_validator]
    )
    price = models.FloatField('prix', validators=[positive_float_validator])
    YES_NO_CHOICE = (
        (None, '------------'),
        (False, 'Non'),
        (True, 'Oui'),
    )
    previously_acquired = models.BooleanField(
        "manuel acquis précédemment par l'élève",
        choices=YES_NO_CHOICE,
        blank=False,
        default=None,
    )
    done = models.BooleanField(
        'Traité',
        blank=True,
        default=False
    )
    comments = models.TextField(
        'commentaires',
        blank=True,
        help_text="Ce message sera visible par la documentaliste."
    )
    consumable = models.BooleanField(
        'consommable',
        help_text="Exemple : un cahier d'exercices est un consommable",
        choices=YES_NO_CHOICE,
        blank=False,
        default=None,
    )

    @property
    def previously_acquired_text(self):
        if self.previously_acquired:
            return 'Oui'
        else:
            return 'Non'

    @property
    def consumable_text(self):
        if self.consumable:
            return 'Oui'
        else:
            return 'Non'

    def __str__(self):
        return f'{self.title} ({self.authors}) - {self.isbn}'

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('edit_book', kwargs={'teacher_pk': str(self.teacher.pk), 'pk': str(self.pk)})


class SuppliesRequirement(BaseModel):
    class Meta:
        verbose_name = 'demande de fournitures'
        verbose_name_plural = 'demandes de fournitures'

    teacher = models.ForeignKey(verbose_name='coordonnateur', to=Teacher, on_delete=models.PROTECT, null=True)
    level = models.ForeignKey(verbose_name='classe', to=Level, on_delete=models.PROTECT, null=True)
    field = models.CharField('discipline', max_length=50)
    supplies = models.TextField('fournitures')
    done = models.BooleanField(
        'Traité',
        blank=True,
        default=False
    )

    def __str__(self):
        return f'{self.supplies} pour {self.level} ({self.teacher})'


class CommonSupply(BaseModel):
    class Meta:
        verbose_name = 'fourniture commune'
        verbose_name_plural = 'fournitures communes'
        ordering = ('order', 'name',)

    name = models.CharField('nom', max_length=200)
    order = models.IntegerField('ordre')

    def __str__(self):
        return self.name
