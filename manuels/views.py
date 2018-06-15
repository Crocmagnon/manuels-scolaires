import re

import bs4
import requests
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.decorators.cache import cache_page
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, FormView, DetailView, TemplateView

from manuels.forms import AddBookForm, AddSuppliesForm, EditBookForm, EditSuppliesForm
from manuels.models import Teacher, Book, SuppliesRequirement

import logging

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

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        if self.teacher.has_confirmed_list:
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

    def get_success_url(self):
        if self.add_another:
            return reverse(self.success_target, args=[str(self.teacher.pk)])
        else:
            return reverse('list_books', args=[str(self.teacher.pk)])

    def form_valid(self, form):
        self.add_another = form.cleaned_data['add_another']
        response = super().form_valid(form)
        messages.success(self.request, f'"{self.object}" a été ajouté.')
        return response


class BookView:
    model = Book
    success_target = 'add_book'
    item_text = 'un livre'
    item_text_plural = 'livres'


class AddBookView(BookView, AddItemView):
    form_class = AddBookForm
    template_name = 'manuels/add_book.html'

    def form_valid(self, form: AddBookForm):
        self.add_another = form.cleaned_data['add_another']
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
            )
            messages.success(self.request, f'"{book}" a été ajouté.')

        return HttpResponseRedirect(self.get_success_url())


class SuppliesView:
    model = SuppliesRequirement
    success_target = 'add_supplies'
    item_text = 'des fournitures'
    item_text_plural = 'fournitures'


class AddSuppliesView(SuppliesView, AddItemView):
    form_class = AddSuppliesForm
    message_template = 'manuels/supplies_message.html'
    template_name = 'manuels/add_supplies.html'


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


@cache_page(None)
def isbn_api(request, isbn):
    res = requests.get(f'https://www.decitre.fr/livres/{isbn}.html')

    try:
        res.raise_for_status()
    except Exception as exc:
        return JsonResponse({
            'error': str(exc)
        })

    decitre_soup = bs4.BeautifulSoup(res.text, "html.parser")
    title = decitre_soup.select('h1.product-title')
    if title:
        title = title[0]
        title.span.extract()
        title = title.getText().strip()

    authors = decitre_soup.select('h2.authors')
    if authors:
        authors = authors[0]
        authors = authors.getText().strip()

    price = decitre_soup.select('.product-add-to-cart-wrapper div.price span.final-price')
    if price:
        price = price[0]
        price = price.getText().replace('€', '').replace(',', '.').strip()

    year = None
    editor = None
    extra_info = decitre_soup.select('ul.extra-infos.hide-on-responsive')
    if extra_info:
        extra_info = extra_info[0].getText().strip()
        matches = re.match('^(?P<editor>.+)\nParu le : \d{2}/\d{2}/(?P<year>\d{4})$', extra_info)
        groups = matches.groupdict()
        year = groups.get('year')
        editor = groups.get('editor')

    return JsonResponse({
        'title': title,
        'authors': authors,
        'isbn': isbn,
        'price': float(price),
        'year': year,
        'editor': editor,
    })
