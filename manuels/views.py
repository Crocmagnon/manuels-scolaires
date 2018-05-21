import os

from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import get_object_or_404, redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.views.generic import CreateView, ListView

from manuels.forms import AddBookForm
from manuels.models import Teacher, Book


class HomePageView(CreateView):
    model = Teacher
    fields = '__all__'
    template_name = 'manuels/home_page.html'

    def get(self, request, *args, **kwargs):
        teacher_pk = request.session.get('teacher_pk')
        if teacher_pk:
            return redirect('list_books', pk=teacher_pk)

        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        dest = form.cleaned_data['email']
        link = self.request.build_absolute_uri(reverse('list_books', args=[str(self.object.pk)]))
        msg = EmailMultiAlternatives(
            subject='Gestion des manuels scolaires',
            body=f'Bonjour {self.object.first_name},\n'
                 f'Voici votre lien pour la gestion des manuels scolaires : {link}',
            from_email=settings.SERVER_EMAIL,
            to=[dest],
        )
        reply_to = [os.getenv('REPLY_TO')]
        if reply_to:
            msg.reply_to = reply_to
        msg.attach_alternative(
            render_to_string('manuels/email.html', {'link': link, 'teacher': self.object}), "text/html"
        )
        msg.send()
        return response


class BaseTeacherView:
    teacher = None

    def dispatch(self, request, *args, **kwargs):
        self.teacher = get_object_or_404(Teacher, pk=self.kwargs['pk'])
        request.session['teacher_pk'] = str(self.teacher.pk)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['teacher'] = self.teacher

        return context


class ListBooksView(BaseTeacherView, ListView):
    model = Book
    template_name = 'manuels/list_books.html'
    context_object_name = 'books'

    def get_queryset(self):
        return Book.objects.filter(teacher=self.teacher)


class AddBookView(BaseTeacherView, CreateView):
    model = Book
    template_name = 'manuels/add_book.html'
    form_class = AddBookForm
    add_another = False

    def get_initial(self):
        return {
            'teacher': self.teacher
        }

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['teacher'].queryset = Teacher.objects.filter(pk=self.teacher.pk)
        return form

    def form_valid(self, form):
        self.add_another = form.cleaned_data['add_another']
        return super().form_valid(form)

    def get_success_url(self):
        messages.success(self.request, f'"{self.object}" a été ajouté.')
        if self.add_another:
            return reverse('add_book', args=[str(self.teacher.pk)])
        else:
            return reverse('list_books', args=[str(self.teacher.pk)])


def clear_teacher_view(request):
    if request.session['teacher_pk']:
        del request.session['teacher_pk']
    return redirect('home_page')
