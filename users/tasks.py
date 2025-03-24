import uuid
from datetime import timedelta

from django.core.mail import send_mail
from django.utils.timezone import now

from users.models import EmailVerification, User


def send_email_verification(username):
    send_mail(
        'Verify your email',
        'Click this link to verify...',
        'from@example.com',
        ['to@example.com'],
        fail_silently=False,
    )
