import logging
import os
import re
import uuid as uuid

import bs4
import requests
from django.conf import settings
from django.contrib.postgres.fields import CIEmailField
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.db import models
from django.db.models import Sum
from django.template.loader import render_to_string
from django.urls import reverse

from manuels.utils import validate_isbn

logger = logging.getLogger(__name__)


class ISBNError(Exception):
    def __init__(self, data):
        self.data = data


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
    email = CIEmailField(
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

    @property
    def non_acquired_consumables(self):
        if hasattr(self, "prefetched_books"):
            return filter(lambda book: book.consumable and not book.previously_acquired, self.prefetched_books)
        return self.book_set.filter(consumable=True, previously_acquired=False)

    @property
    def non_acquired_consumable_count(self):
        if hasattr(self, "prefetched_books"):
            return len(list(self.non_acquired_consumables))
        return self.non_acquired_consumables.count()

    @property
    def non_acquired_consumable_price(self):
        if hasattr(self, "prefetched_books"):
            return sum(map(lambda book: book.price, self.non_acquired_consumables))
        return self.non_acquired_consumables.aggregate(Sum('price')).get(
            'price__sum', 0)

    @property
    def non_acquired_books(self):
        if hasattr(self, "prefetched_books"):
            return filter(lambda book: not book.consumable and not book.previously_acquired, self.prefetched_books)
        return self.book_set.filter(consumable=False, previously_acquired=False)

    @property
    def non_acquired_book_count(self):
        if hasattr(self, "prefetched_books"):
            return len(list(self.non_acquired_books))
        return self.non_acquired_books.count()

    @property
    def non_acquired_book_price(self):
        if hasattr(self, "prefetched_books"):
            return sum(map(lambda book: book.price, self.non_acquired_books))
        return self.non_acquired_books.aggregate(Sum('price')).get(
            'price__sum', 0)

    @property
    def non_acquired_items(self):
        if hasattr(self, "prefetched_books"):
            return filter(lambda book: not book.previously_acquired, self.prefetched_books)
        return self.book_set.filter(previously_acquired=False)

    @property
    def non_acquired_total_price(self):
        if hasattr(self, "prefetched_books"):
            return sum(map(lambda book: book.price, self.non_acquired_items))
        return self.non_acquired_items.aggregate(Sum('price')).get(
            'price__sum', 0)


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
        'ISBN/EAN du manuel élève (hors specimen)',
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

    def update_from_decitre(self):
        decitre_data = self.fetch_from_decitre(self.isbn)
        self.title = decitre_data.get('title')
        self.authors = decitre_data.get('authors')
        self.price = decitre_data.get('price')
        self.publication_year = decitre_data.get('year')

        editor = decitre_data.get('editor')
        potential_editor = (
            Editor.objects.filter(name__iexact=editor).first()
            or Editor.objects.filter(name__icontains=editor).first()
        )
        if potential_editor:
            self.other_editor = ""
        else:
            potential_editor = Editor.objects.get(name__istartswith="autre")
            self.other_editor = editor

        self.editor = potential_editor
        self.save()

    @property
    def decitre_url(self):
        isbn = self.isbn.strip().replace('-', '')
        if not validate_isbn(isbn) or len(isbn) == 10:
            return ""
        return f'https://www.decitre.fr/livres/{isbn}.html'

    @staticmethod
    def fetch_from_decitre(isbn: str):
        isbn = isbn.strip().replace('-', '')

        if not validate_isbn(isbn):
            raise ISBNError({
                'error': "L'ISBN saisi n'est pas valide."
            })

        if len(isbn) == 10:
            raise ISBNError({
                'error': "La recherche sur Decitre ne fonctionne qu'avec un ISBN 13 (ou EAN)."
            })

        try:
            res = requests.get(f'https://www.decitre.fr/livres/{isbn}.html', timeout=10)
        except requests.exceptions.Timeout as exc:
            raise ISBNError({
                'error': "Decitre n'a pas répondu dans les temps. Message : {}".format(str(exc))
            })

        try:
            res.raise_for_status()
        except Exception as exc:
            message = (
                "Erreur lors de la recherche. Il se peut que le livre n'existe pas dans la base de connaissances "
                "de Decitre ou que vous ayez mal saisi l'ISBN. Vous pouvez toujours saisir "
                "les informations du livre à la main. Message : {}").format(str(exc))
            raise ISBNError({
                'error': message
            })

        decitre_soup = bs4.BeautifulSoup(res.text, "html.parser")
        title = decitre_soup.select('h1.product-title')
        if title:
            title = title[0]
            if title.span:
                title.span.extract()
            title = title.get_text(strip=True)

        authors = decitre_soup.select('.authors')
        if authors:
            authors = authors[0]
            authors = authors.get_text(strip=True)

        price = decitre_soup.select('.fp-top--add-to-cart div.price span.final-price')
        if price:
            price = price[0]
            price = price.get_text().replace('€', '').replace(',', '.').strip()

        year = None
        editor = None
        extra_info = decitre_soup.select('.informations-container')
        logger.debug('raw extra_info')
        logger.debug(extra_info)
        if not extra_info:
            logger.debug('#fiche-technique')
            extra_info = decitre_soup.select('#fiche-technique')
            logger.debug('raw extra_info fiche technique')
            logger.debug(extra_info)

        if extra_info:
            extra_info = extra_info[0].get_text(strip=True)
            logger.debug('extra_info')
            logger.debug(extra_info)
            matches = re.search(
                r'Date de parution(?: :)?\d{2}/\d{2}/(?P<year>\d{4})Editeur(?: :)?(?P<editor>.+?)(?:ISBN|Collection)',
                extra_info)
            if matches:
                groups = matches.groupdict()
                year = groups.get('year')
                editor = groups.get('editor').strip()

        return {
            'title': title,
            'authors': authors,
            'isbn': isbn,
            'price': float(price) if price else None,
            'year': year,
            'editor': editor,
        }


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
