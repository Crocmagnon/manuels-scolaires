from django.conf import settings


def authorized_mails(request):
    return {'authorized_mails': settings.AUTHORIZED_EMAILS}
