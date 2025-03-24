from django.contrib import admin
from django.utils.safestring import mark_safe

from products.admin import BasketAdmin
from users.models import EmailVerification, User


# Register your models here.

class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'get_html_photo')
    list_display_links = ('username',)
    search_fields = ('username', 'email')
    inlines = (BasketAdmin,)

    def get_html_photo(self, object):  # object refers to an object of the women class
        if object.image:
            return mark_safe(f'<img src="{object.image.url}" width=60 height = 60>')

    get_html_photo.short_description = 'Image'


admin.site.register(User, UserAdmin)


class EmailVerificationAdmin(admin.ModelAdmin):
    list_display = ('code', 'user', 'expiration')
    fields = ('code', 'user', 'expiration', 'created')
    readonly_fields = ('created',)


admin.site.register(EmailVerification, EmailVerificationAdmin)
