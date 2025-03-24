from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt


class CommonMixin:
    title = None

    def get_context_data(self, **kwargs):
        context = super(CommonMixin, self).get_context_data(**kwargs)
        context['title'] = self.title
        return context


class CSRFExemptMixin(object):
    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(CSRFExemptMixin, self).dispatch(*args, **kwargs)
