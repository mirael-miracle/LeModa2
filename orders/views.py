from http import HTTPStatus
import stripe

from django.conf import settings
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import DetailView, ListView, TemplateView
from django.views.generic.edit import CreateView

from common.views import CommonMixin, CSRFExemptMixin
from orders.forms import OrderForm
from orders.models import Order
from products.models import Basket

stripe.api_key = settings.STRIPE_SECRET_KEY


class SuccessTemplateView(CommonMixin, TemplateView):
    template_name = 'orders/success.html'
    title = 'Thanks for the order'


class CanceledTemplateView(CommonMixin, TemplateView):
    template_name = 'orders/cancel.html'


class OrderCreateView(CSRFExemptMixin, CommonMixin, CreateView):
    title = 'Store - Making an order'
    template_name = 'orders/order-create.html'
    form_class = OrderForm
    success_url = reverse_lazy('orders:order_create')

    def post(self, request, *args, **kwargs):
        super(OrderCreateView, self).post(request, *args, **kwargs)
        baskets = Basket.objects.filter(user=self.request.user)
        if not baskets.exists():
            return HttpResponse('Basket is empty', status=HTTPStatus.BAD_REQUEST)
        
        domain = f"{request.scheme}://{request.get_host()}"

        checkout_session = stripe.checkout.Session.create(
            line_items=baskets.stripe_products(),
            metadata={'order_id': self.object.id},
            mode='payment',
            success_url=f"{domain}{reverse('orders:order_success')}",
            cancel_url=f"{domain}{reverse('orders:order_canceled')}"
        )
        return HttpResponseRedirect(checkout_session.url, status=HTTPStatus.SEE_OTHER)

    def form_valid(self, form):
        form.instance.initiator = self.request.user
        return super(OrderCreateView, self).form_valid(form)


@csrf_exempt
def stripe_webhook_view(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        # Retrieve the session. If you require line items in the response, you may include them by expanding line_items.
        session = stripe.checkout.Session.retrieve(
            event['data']['object']['id'],
            expand=['line_items'],
        )

        line_items = session
        # Fulfill the purchase...
        fulfill_order(line_items)

    # Passed signature verification
    return HttpResponse(status=200)


def fulfill_order(session):
    order_id = int(session.metadata.order_id)
    order = Order.objects.get(id=order_id)
    order.update_after_payment()


class OrderListView(CommonMixin, ListView):
    template_name = 'orders/orders.html'
    title = 'Store - Orders'
    queryset = Order.objects.all()
    context_object_name = 'orders'
    ordering = ('-id',)

    def get_queryset(self):
        queryset = super(OrderListView, self).get_queryset()
        return queryset.filter(initiator=self.request.user)


class OrderDetailView(DetailView):
    template_name = 'orders/order.html'
    model = Order

    def get_context_data(self, **kwargs):
        context = super(OrderDetailView, self).get_context_data(**kwargs)
        context['title'] = f'Order - №{self.object.id}'
        return context
