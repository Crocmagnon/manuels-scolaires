from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import CreateView, ListView

from manuels.forms import AddBookForm
from manuels.models import Teacher, Book


class HomePageView(CreateView):
    model = Teacher
    fields = ['first_name', 'last_name', 'phone_number']
    template_name = 'manuels/home_page.html'


class BaseTeacherView:
    teacher = None

    def dispatch(self, request, *args, **kwargs):
        self.teacher = get_object_or_404(Teacher, pk=self.kwargs['pk'])
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
