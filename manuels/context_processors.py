import os


def authorized_mails(request):
    return {'authorized_mails': os.getenv('AUTHORIZED_MAILS', '').split(',')}
