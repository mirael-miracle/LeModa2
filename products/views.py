from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.views.generic import ListView, TemplateView

from common.views import CommonMixin
from users.models import User

from .models import *


# Create your views here.
class IndexView(CommonMixin, TemplateView):
    template_name = 'products/index.html'
    title = 'Store'


class ProductsView(CommonMixin, ListView):
    model = Product
    template_name = 'products/products.html'
    title = 'Store - Catalog'
    context_object_name = 'products'
    paginate_by = 6

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(ProductsView, self).get_context_data(**kwargs)
        context['categories'] = ProductCategory.objects.all()
        context['current_sort_by'] = self.request.GET.get('sort_by', 'name')
        context['category_id'] = self.kwargs.get('category_id')
        return context

    def get_queryset(self):
        queryset = super(ProductsView, self).get_queryset()
        category_id = self.kwargs.get('category_id')
        sort_by = self.request.GET.get('sort_by', 'name')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        valid_sort_fields = ['name', '-name', 'price', '-price', 'category__name', '-category__name']

        if sort_by in valid_sort_fields:
            queryset = queryset.order_by(sort_by)
        else:
             queryset = queryset.order_by('name')
             
        return queryset

@login_required
def basket_add(request, product_id):
    product = Product.objects.get(id=product_id)
    baskets = Basket.objects.filter(user=request.user, product=product)
    if not baskets.exists():
        Basket.objects.create(user=request.user, product=product, quantity=1)
    else:
        basket = baskets.first()
        basket.quantity += 1
        basket.save()
    return HttpResponseRedirect(
        request.META['HTTP_REFERER'])  # we define on what page user is and redirect to this page


@login_required
def basket_remove(request, basket_id):
    basket = Basket.objects.get(id=basket_id)
    basket.delete()
    return redirect(request.META['HTTP_REFERER'])
