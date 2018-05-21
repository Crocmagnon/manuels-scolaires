from django.shortcuts import get_object_or_404
from django.views.generic import CreateView, FormView, TemplateView

from manuels.forms import AddBookForm
from manuels.models import Teacher, Book


class HomePageView(CreateView):
    model = Teacher
    fields = ['first_name', 'last_name', 'phone_number']
    template_name = 'manuels/home_page.html'


class AddBookView(CreateView):
    model = Book
    template_name = 'manuels/add_book.html'
    form_class = AddBookForm
    teacher = None

    def dispatch(self, request, *args, **kwargs):
        self.teacher = get_object_or_404(Teacher, pk=self.kwargs['id'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['teacher'] = self.teacher

        return context

    def get_initial(self):
        return {
            'teacher': self.teacher
        }

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['teacher'].queryset = Teacher.objects.filter(pk=self.teacher.pk)
        return form
