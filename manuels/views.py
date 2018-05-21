from django.shortcuts import get_object_or_404
from django.views.generic import CreateView, FormView, TemplateView

from manuels.models import Teacher


class HomePageView(CreateView):
    model = Teacher
    fields = ['first_name', 'last_name', 'phone_number']
    template_name = 'manuels/home_page.html'


class AddBookView(TemplateView):
    template_name = 'manuels/add_book.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context['teacher'] = get_object_or_404(Teacher, pk=self.kwargs['id'])

        return context
