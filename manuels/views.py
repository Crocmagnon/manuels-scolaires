import logging
import re

import bs4
import requests
from django.contrib import messages
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views.decorators.cache import cache_page
from django.views.generic import CreateView, UpdateView, DeleteView, TemplateView

from manuels.forms import AddBookForm, AddSuppliesForm, EditBookForm, EditSuppliesForm
from manuels.models import Teacher, Book, SuppliesRequirement, CommonSupply

logger = logging.getLogger(__name__)


class HomePageView(CreateView):
    model = Teacher
    fields = ['first_name', 'last_name', 'phone_number', 'email']
    template_name = 'manuels/home_page.html'

    def get(self, request, *args, **kwargs):
        teacher_pk = request.session.get('teacher_pk')
        if teacher_pk:
            return redirect('list_books', pk=teacher_pk)

        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        self.object.send_link(self.request)
        return response


class BaseTeacherView:
    teacher = None
    teacher_field = 'pk'

    def dispatch(self, request, *args, **kwargs):
        self.teacher = Teacher.objects.filter(pk=self.kwargs[self.teacher_field]).first()
        if not self.teacher:
            messages.warning(request, "Impossible de trouver le coordonnateur demandé. Si vous pensez que ceci est "
                                      "une erreur, merci de vous adresser à votre documentaliste.")
            return redirect('clear_teacher')
        request.session['teacher_pk'] = str(self.teacher.pk)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['teacher'] = self.teacher

        return context


class ListBooksView(BaseTeacherView, TemplateView):
    template_name = 'manuels/list_books_supplies.html'


class ItemView(BaseTeacherView):
    add_another = False
    item_text = None
    item_text_plural = None
    success_target = None
    message_template = None
    verb = None
    button_class = 'primary'
    button_icon = 'fas fa-check-circle'

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        if self.teacher and self.teacher.has_confirmed_list:
            messages.error(request, "Vous avez déjà confirmé vos listes. Il n'est plus possible de les modifier.")
            return redirect('list_books', pk=self.teacher.pk)
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['item'] = self.item_text
        context['item_plural'] = self.item_text_plural
        context['message_template'] = self.message_template
        context['verb'] = self.verb
        context['button_class'] = self.button_class
        context['button_icon'] = self.button_icon
        return context

    def get_initial(self):
        return {
            'teacher': self.teacher
        }

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['teacher'].queryset = Teacher.objects.filter(pk=self.teacher.pk)
        return form


class AddItemView(ItemView, CreateView):
    verb = 'Ajouter'
    button_icon = 'fas fa-plus-circle'

    def get_success_url(self):
        if self.add_another:
            return reverse(self.success_target, args=[str(self.teacher.pk)])
        else:
            return reverse('list_books', args=[str(self.teacher.pk)])

    def form_valid(self, form):
        self.add_another = form.cleaned_data['add_another']
        return HttpResponseRedirect(self.get_success_url())


class BookView:
    model = Book
    success_target = 'add_book'
    item_text = 'un livre'
    item_text_plural = 'livres'


class AddBookView(BookView, AddItemView):
    form_class = AddBookForm
    template_name = 'manuels/add_book.html'

    def form_valid(self, form: AddBookForm):
        for level in form.cleaned_data['levels']:
            book = Book.objects.create(
                teacher=form.cleaned_data['teacher'],
                level=level,
                field=form.cleaned_data['field'],
                title=form.cleaned_data['title'],
                authors=form.cleaned_data['authors'],
                editor=form.cleaned_data['editor'],
                other_editor=form.cleaned_data['other_editor'],
                publication_year=form.cleaned_data['publication_year'],
                isbn=form.cleaned_data['isbn'],
                price=form.cleaned_data['price'],
                previously_acquired=form.cleaned_data['previously_acquired'],
                comments=form.cleaned_data['comments'],
                consumable=form.cleaned_data['consumable'],
            )
            messages.success(self.request, f'"{book}" a été ajouté.')

        return super().form_valid(form)


class SuppliesView:
    model = SuppliesRequirement
    success_target = 'add_supplies'
    item_text = 'des fournitures'
    item_text_plural = 'fournitures'


class AddSuppliesView(SuppliesView, AddItemView):
    form_class = AddSuppliesForm
    message_template = 'manuels/supplies_message.html'
    template_name = 'manuels/add_supplies.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['common_supplies'] = CommonSupply.objects.all()
        return context

    def form_valid(self, form: AddBookForm):
        for level in form.cleaned_data['levels']:
            supplies = SuppliesRequirement.objects.create(
                teacher=form.cleaned_data['teacher'],
                level=level,
                field=form.cleaned_data['field'],
                supplies=form.cleaned_data['supplies'],
            )
            messages.success(self.request, f'"{supplies}" a été ajouté.')

        return super().form_valid(form)


class EditItemView(ItemView, UpdateView):
    teacher_field = 'teacher_pk'
    item_text = None
    item_text_plural = None
    message_template = None
    verb = 'Modifier'

    def get_queryset(self):
        return self.model.objects.filter(teacher=self.teacher)

    def get_success_url(self):
        messages.success(self.request, f'"{self.object}" a été modifié.')
        return reverse('list_books', args=[str(self.teacher.pk)])


class EditBookView(BookView, EditItemView):
    form_class = EditBookForm
    template_name = 'manuels/add_book.html'


class EditSuppliesView(SuppliesView, EditItemView):
    form_class = EditSuppliesForm
    template_name = 'manuels/add_supplies.html'


class DeleteItemView(ItemView, DeleteView):
    teacher_field = 'teacher_pk'
    item_text = None
    item_text_plural = None
    message_template = 'manuels/confirm_delete.html'
    verb = 'Supprimer'
    button_class = 'danger'
    button_icon = 'fas fa-trash'
    template_name = 'manuels/add_supplies.html'

    def get_queryset(self):
        return self.model.objects.filter(teacher=self.teacher)

    def get_success_url(self):
        messages.success(self.request, f'"{self.object}" a été supprimé.')
        return reverse('list_books', args=[str(self.teacher.pk)])


class DeleteBookView(BookView, DeleteItemView):
    pass


class DeleteSuppliesView(SuppliesView, DeleteItemView):
    pass


def clear_teacher_view(request):
    if 'teacher_pk' in request.session:
        del request.session['teacher_pk']
    return redirect('home_page')


class ConfirmTeacherView(BaseTeacherView, UpdateView):
    model = Teacher
    fields = []
    template_name = 'manuels/confirm_teacher.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        self.object.has_confirmed_list = True
        self.object.save()
        self.object.send_confirmation(request=self.request)
        messages.success(self.request, "Vos listes ont été validées. Votre documentaliste a été notifiée par email.")
        return response


def validate_isbn(isbn):
    _sum = 0
    if len(isbn) == 10:
        for i, digit in enumerate(isbn):
            if digit == 'X':
                digit = 10
            else:
                digit = int(digit)
            _sum += digit * (i + 1)

        return _sum % 11 == 0

    elif len(isbn) == 13:
        for i, digit in enumerate(isbn):
            weight = 3 if i % 2 == 1 else 1
            digit = int(digit)
            _sum += digit * weight

        return _sum % 10 == 0

    return False


# We are able to cache the response because it's very unlikely that the details of a book will change through time
@cache_page(2 * 60 * 60)
def isbn_api(request, isbn):
    isbn = isbn.strip().replace('-', '')

    if not validate_isbn(isbn):
        return JsonResponse({
            'error': "L'ISBN saisi n'est pas valide."
        })

    if len(isbn) == 10:
        return JsonResponse({
            'error': "La recherche sur Decitre ne fonctionne qu'avec un ISBN 13 (ou EAN)."
        })

    try:
        res = requests.get(f'https://www.decitre.fr/livres/{isbn}.html', timeout=10)
    except requests.exceptions.Timeout as exc:
        return JsonResponse({
            'error': "Decitre n'a pas répondu dans les temps. Message : {}".format(str(exc))
        })

    try:
        res.raise_for_status()
    except Exception as exc:
        message = ("Erreur lors de la recherche. Il se peut que le livre n'existe pas dans la base de connaissances "
                   "de Decitre ou que vous ayez mal saisi l'ISBN. Vous pouvez toujours saisir "
                   "les informations du livre à la main. Message : {}").format(str(exc))
        return JsonResponse({
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

    price = decitre_soup.select('div.price span.final-price')
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
        matches = re.search(r'Date de parution(?: :)?\d{2}/\d{2}/(?P<year>\d{4})Editeur(?: :)?(?P<editor>.+?)(?:ISBN|Collection)', extra_info)
        if matches:
            groups = matches.groupdict()
            year = groups.get('year')
            editor = groups.get('editor').strip()

    return JsonResponse({
        'title': title,
        'authors': authors,
        'isbn': isbn,
        'price': float(price) if price else None,
        'year': year,
        'editor': editor,
    })
