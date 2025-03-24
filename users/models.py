from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.mail import send_mail
from django.db import models
from django.urls import reverse
from django.utils.timezone import now


class User(AbstractUser):  # we extend base user model and add user image
    image = models.ImageField(upload_to='user_images', null=True, blank=True)
    is_verified_email = models.BooleanField(default=False)

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        unique_together = ('email',)  # email have to be unique


class EmailVerification(models.Model):
    code = models.UUIDField(unique=True)
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    expiration = models.DateTimeField()

    def __str__(self):
        return f'EmailVerification object for {self.user.email}'

    def send_verification_email(self):
        link = reverse('users:email_verification', kwargs={'email': self.user.email, 'code': self.code})
        verification_link = f'{settings.DOMAIN_NAME}{link}'
        subject = f'Account confirmation for {self.user.username}'
        message = 'To confirm the account {}, follow the link: {}'.format(
            self.user.email,
            verification_link
        )
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[self.user.email],
        )

    def is_expired(self):
        return now() >= self.expiration
