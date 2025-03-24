import stripe
from django.conf import settings
from django.db import models

from users.models import User

stripe.api_key = settings.STRIPE_SECRET_KEY


class ProductCategory(models.Model):
    name = models.CharField(max_length=128, unique=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Product_Categories'


class Product(models.Model):
    name = models.CharField(max_length=256)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    stripe_product_price_id = models.CharField(max_length=128, blank=True, null=True)
    quantity = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='product_images')
    category = models.ForeignKey(to='ProductCategory', on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if not self.stripe_product_price_id:
            stripe_product_price = self.create_stripe_product_price()
            self.stripe_product_price_id = stripe_product_price['id']
        super(Product, self).save(force_insert=False, force_update=False, using=None, update_fields=None)

    def create_stripe_product_price(self):
        stripe_product = stripe.Product.create(name=self.name)
        stripe_product_price = stripe.Price.create(
            product=stripe_product['id'],
            unit_amount=round(self.price * 100),
            currency='eur'
        )
        return stripe_product_price

    class Meta:
        verbose_name_plural = 'Products'
        verbose_name = 'Product'


class BasketQuerySet(models.QuerySet):
    def total_sum(self):
        return sum(x.sum() for x in self)

    def total_quantity(self):
        return sum(x.quantity for x in self)

    def stripe_products(self):
        line_items = []
        for basket in self:
            item = {
                'price_data': {
                    'currency': 'eur',
                    'product_data': {
                        'name': basket.product.name,
                    },
                    'unit_amount': round(basket.product.price*100)
                },
                'quantity': basket.quantity,
            }
            line_items.append(item)
        return line_items


class Basket(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    product = models.ForeignKey(to=Product, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField(default=0)
    created_timestamp = models.DateTimeField(auto_now_add=True)

    objects = BasketQuerySet.as_manager()  # we chose what queryset we want to use

    # in default - QuerySet

    def __str__(self):
        return f'Корзина для {self.user.username} | Продукт {self.product.name}'

    def sum(self):
        return int(self.quantity * self.product.price)

    def de_json(self):
        basket_item = {
            'product_name': self.product.name,
            'quantity': self.quantity,
            'price': float(self.product.price),
            'sum': float(self.sum())
        }
        return basket_item
