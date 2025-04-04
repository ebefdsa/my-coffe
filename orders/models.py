from django.db import models
from django.core.validators import MinLengthValidator, MaxLengthValidator, RegexValidator
from django.core.exceptions import ValidationError
from decimal import Decimal
from django.contrib.auth.models import User
from products.models import Product

# دالة للتحقق من صحة تاريخ انتهاء البطاقة (MM/YY)
def validate_expire_date(value):
    if len(value) != 5 or value[2] != '/' or not value[:2].isdigit() or not value[3:].isdigit():
        raise ValidationError("تاريخ الانتهاء يجب أن يكون بالصيغة MM/YY.")

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_date = models.DateTimeField()
    details = models.ManyToManyField(Product, through='OrderDetails')
    is_finished = models.BooleanField()
    total = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.00'))
    items_count = models.IntegerField(default=0)

    def update_order(self):
        total = 0
        items_count = 0
        for detail in self.orderdetails_set.all():
            total += detail.price * detail.quantity
            items_count += detail.quantity
        self.total = total
        self.items_count = items_count
        self.save()

    def __str__(self):
        return 'User: ' + self.user.username + ', order id: ' + str(self.id)


class OrderDetails(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    quantity = models.IntegerField()

    def __str__(self):
        return 'User: ' + self.order.user.username + ', Product: ' + self.product.name + ', Order id: ' + str(self.order.id)

    class Meta:
        ordering = ['-id']


class Payment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    shipment_address = models.CharField(max_length=150)
    shipment_phone = models.CharField(max_length=50)
    card_number = models.CharField(
        max_length=16,
        validators=[
            MinLengthValidator(16),
            MaxLengthValidator(16),
            RegexValidator(r'^\d{16}$', message="رقم البطاقة يجب أن يكون 16 رقمًا.")
        ]
    )
    expire = models.CharField(
        max_length=5,
        validators=[
            RegexValidator(
                r'^(0[1-9]|1[0-2])\/([0-9]{2})$',
                message='يجب أن يكون تاريخ الانتهاء بتنسيق MM/YY'
            )
        ]
    )
    security_code = models.CharField(
        max_length=3,
        validators=[
            MinLengthValidator(3),
            MaxLengthValidator(3),
            RegexValidator(r'^\d{3}$', message="رمز الأمان يجب أن يكون 3 أرقام.")
        ]
    )
    payment_date = models.DateTimeField(auto_now_add=True)

    def clean(self):
        # تحقق من صحة تاريخ الانتهاء
        if self.expire:
            try:
                month, year = self.expire.split('/')
                if not (1 <= int(month) <= 12):
                    raise ValidationError({'expire': 'Month must be between 01 and 12'})
                if len(year) != 2:
                    raise ValidationError({'expire': 'Year must be 2 digits'})
            except ValueError:
                raise ValidationError({'expire': 'Use MM/YY format'})

    def __str__(self):
        return f"Payment for Order #{self.order.id} on {self.payment_date}"