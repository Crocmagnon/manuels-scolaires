from django.views.generic import CreateView

from manuels.models import Teacher


class HomePageView(CreateView):
    model = Teacher
    fields = []
    template_name = 'manuels/home_page.html'
