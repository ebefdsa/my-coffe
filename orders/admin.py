# admin.py
from django.contrib import admin
from .models import Order, OrderDetails, Payment

# تخصيص عرض طلبات العميل (Order)
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'order_date', 'is_finished', 'total', 'items_count')  # الأعمدة التي ستظهر في الجدول
    list_filter = ('is_finished', 'order_date')  # الفلاتر التي يمكن استخدامها مثل: الفلاتر حسب الحالة وتاريخ الطلب
    search_fields = ('user__username', 'user__email')  # البحث باستخدام اسم المستخدم أو البريد الإلكتروني
    ordering = ('-order_date',)  # ترتيب الطلبات حسب تاريخ الطلب من الأحدث إلى الأقدم

# تخصيص عرض تفاصيل الطلب (OrderDetails)
@admin.register(OrderDetails)
class OrderDetailsAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'price', 'quantity')  # الأعمدة التي ستظهر في الجدول
    search_fields = ('order__id', 'product__name')  # البحث باستخدام رقم الطلب أو اسم المنتج

# تخصيص عرض المدفوعات (Payment)
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order', 'shipment_address', 'shipment_phone', 'payment_date')  # الأعمدة التي ستظهر في الجدول
    search_fields = ('order__id', 'shipment_address')  # البحث باستخدام رقم الطلب أو عنوان الشحن
    ordering = ('-payment_date',)  # ترتيب المدفوعات حسب تاريخ الدفع من الأحدث إلى الأقدم
