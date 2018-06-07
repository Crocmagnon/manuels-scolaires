from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
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
    template_name = 'manuels/add_item.html'
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
        messages.success(self.request, f'"{self.object}" a été ajouté.')
        if self.add_another:
            return reverse(self.success_target, args=[str(self.teacher.pk)])
        else:
            return reverse('list_books', args=[str(self.teacher.pk)])

    def form_valid(self, form):
        self.add_another = form.cleaned_data['add_another']
        return super().form_valid(form)


class BookView:
    model = Book
    success_target = 'add_book'
    item_text = 'un livre'
    item_text_plural = 'livres'


class AddBookView(BookView, AddItemView):
    form_class = AddBookForm


class SuppliesView:
    model = SuppliesRequirement
    success_target = 'add_supplies'
    item_text = 'des fournitures'
    item_text_plural = 'fournitures'


class AddSuppliesView(SuppliesView, AddItemView):
    form_class = AddSuppliesForm
    message_template = 'manuels/supplies_message.html'


class EditItemView(ItemView, UpdateView):
    template_name = 'manuels/add_item.html'
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


class EditSuppliesView(SuppliesView, EditItemView):
    form_class = EditSuppliesForm


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
