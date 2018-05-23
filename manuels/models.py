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
        verbose_name = 'enseignant'
        verbose_name_plural = 'enseignants'
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
            render_to_string('manuels/email.html', {'link': link, 'teacher': self}), "text/html"
        )
        msg.send()


class Level(BaseModel):
    class Meta:
        verbose_name = 'classe'
        verbose_name_plural = 'classes'
    name = models.CharField('nom', max_length=10)

    def __str__(self):
        return self.name


class Editor(BaseModel):
    class Meta:
        verbose_name = 'éditeur'
        verbose_name_plural = 'éditeurs'
    name = models.CharField('nom', max_length=50)

    def __str__(self):
        return self.name


def isbn_validator(value):
    regex = re.compile(r'(\d-?){10,13}X?')
    if not regex.match(value):
        raise ValidationError("%(value)s n'est pas un ISBN valide.", params={'value': value})


class Book(BaseModel):
    class Meta:
        verbose_name = 'livre'
        verbose_name_plural = 'livres'

    teacher = models.ForeignKey(verbose_name='enseignant', to=Teacher, on_delete=models.PROTECT, null=True)
    level = models.ForeignKey(verbose_name='classe', to=Level, on_delete=models.PROTECT, null=True)
    field = models.CharField('matière', max_length=100)
    title = models.TextField('titre')
    authors = models.TextField('auteurs')
    editor = models.ForeignKey(verbose_name='éditeur', to=Editor, on_delete=models.PROTECT, null=True)
    publication_year = models.PositiveIntegerField('année de publication')
    isbn = models.CharField(
        'ISBN/EAN',
        max_length=20,
        help_text="Format attendu : 10 ou 13 chiffres, éventuellement séparés par des tirets et éventuellement "
                  "suivis de la lettre <code>X</code>",
        validators=[isbn_validator]
    )
    price = models.PositiveIntegerField('prix')
    YES_NO_CHOICE = (
        (False, 'Non'),
        (True, 'Oui'),
    )
    previously_acquired = models.BooleanField(
        "manuel acquis précédemment par l'élève",
        choices=YES_NO_CHOICE,
        blank=False,
        default=False,
    )

    @property
    def previously_acquired_emoji(self):
        if self.previously_acquired:
            return '✅'
        else:
            return '🚫'

    def __str__(self):
        return f'{self.title} ({self.authors}) - {self.isbn}'


class SuppliesRequirement(BaseModel):
    class Meta:
        verbose_name = 'demande de fournitures'
        verbose_name_plural = 'demandes de fournitures'

    teacher = models.ForeignKey(verbose_name='enseignant', to=Teacher, on_delete=models.PROTECT, null=True)
    level = models.ForeignKey(verbose_name='classe', to=Level, on_delete=models.PROTECT, null=True)
    field = models.CharField('matière', max_length=100)
    supplies = models.TextField('fournitures')

    def __str__(self):
        return f'{self.supplies} pour {self.level} ({self.teacher})'
