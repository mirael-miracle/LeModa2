from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView, UpdateView

from common.views import CommonMixin
from users.forms import *
from users.models import *

# Create your views here.
# def login(request):
#     if request.method == 'POST':
#         form = UserLoginForm(data=request.POST)
#         if form.is_valid():
#             username = request.POST['username']
#             password = request.POST['password']
#             user = auth.authenticate(username=username, password=password)
#             if user:
#                 auth.login(request, user)
#                 return HttpResponseRedirect(reverse('index'))
#     else:
#         form = UserLoginForm()
#     context = {'form': form}
#     return render(request, 'users/login.html', context)


class LoginUserView(CommonMixin, SuccessMessageMixin, LoginView):
    form_class = UserLoginForm
    template_name = 'users/login.html'
    success_message = 'Thanks for authorisation, %(username)s!'
    title = 'Store - Login'

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(cleaned_data, username=self.request.user)


class RegisterUserView(SuccessMessageMixin, CommonMixin, CreateView):
    form_class = UserRegistrationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:login')
    success_message = "%(username)s was created successfully"
    title = 'Store - Sign Up'

    def get_success_message(self, cleaned_data):
        return self.success_message % dict(cleaned_data, username=self.object)


class ProfileView(LoginRequiredMixin, CommonMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    template_name = 'users/profile.html'
    title = 'Store - Profile'

    # success_message = 'Information was updated successfully'

    def get_success_url(self):
        return reverse_lazy('users:profile', args=(self.object.id,))
        # we did it because UpdateView should understand for what user it works for, and we chose user_id


# @login_required
# def profile(request):
#     if request.method == "POST":
#         form = UserProfileForm(instance=request.user, data=request.POST,
#                                files=request.FILES)  # for saving files and updating user information
#         if form.is_valid():
#             form.save()
#             return redirect('users:profile')
#     else:
#         form = UserProfileForm(
#             instance=request.user)  # When making a get request, we pass an instance of the user to the form
#     baskets = Basket.objects.filter(user=request.user)
#     context = {
#         'title': 'Store - Profile',
#         'form': form,
#         'baskets': baskets,
#     }
#     return render(request, 'users/profile.html', context)

@login_required
def logoutuser(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))


class EmailVerificationView(CommonMixin, TemplateView, LoginRequiredMixin):
    title = 'Store - Email verification'
    template_name = 'users/email_verification.html'

    def get(self, request, *args, **kwargs):
        code = kwargs['code']
        user = User.objects.get(email=kwargs['email'])
        email_verifications = EmailVerification.objects.filter(user=user, code=code)
        if email_verifications.exists() and not email_verifications.first().is_expired():
            user.is_verified_email = True
            user.save()
            return super(EmailVerificationView, self).get(request, *args, **kwargs)
        else:
            HttpResponseRedirect(reverse('index'))
