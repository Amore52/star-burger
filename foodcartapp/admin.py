from django.contrib import admin
from django.shortcuts import reverse, redirect
from django.templatetags.static import static
from django.utils.html import format_html
from django.utils.http import url_has_allowed_host_and_scheme
from .models import Product, Order, OrderItem, ProductCategory, Restaurant, RestaurantMenuItem


class RestaurantMenuItemInline(admin.TabularInline):
    model = RestaurantMenuItem
    extra = 0


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ['product', 'quantity', 'price']


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    search_fields = ['name', 'address', 'contact_phone']
    list_display = ['name', 'address', 'contact_phone']
    inlines = [RestaurantMenuItemInline]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['get_image_list_preview', 'name', 'category', 'price']
    list_display_links = ['name']
    list_filter = ['category']
    search_fields = ['name', 'category__name']
    inlines = [RestaurantMenuItemInline]

    fieldsets = (
        ('Общее', {
            'fields': ['name', 'category', 'image', 'get_image_preview', 'price']
        }),
        ('Подробно', {
            'fields': ['special_status', 'description'],
            'classes': ['wide'],
        }),
    )

    readonly_fields = ['get_image_preview']

    class Media:
        css = {'all': (static('admin/foodcartapp.css'),)}

    def get_image_preview(self, obj):
        if not obj.image:
            return 'выберите картинку'
        return format_html('<img src="{}" style="max-height: 200px;"/>', obj.image.url)

    get_image_preview.short_description = 'превью'

    def get_image_list_preview(self, obj):
        if not obj.image or not obj.id:
            return 'нет картинки'
        edit_url = reverse('admin:foodcartapp_product_change', args=[obj.id])
        return format_html(
            '<a href="{}"><img src="{}" style="max-height: 50px;"/></a>',
            edit_url,
            obj.image.url
        )

    get_image_list_preview.short_description = 'превью'


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    pass


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['firstname', 'lastname', 'address', 'phonenumber']
    inlines = [OrderItemInline]

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for instance in instances:
            if isinstance(instance, OrderItem) and not instance.pk:
                instance.price = instance.product.price
            instance.save()
        formset.save_m2m()

    def response_post_save_change(self, request, obj):
        next_url = request.GET.get('next')
        if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts=None):
            return redirect(next_url)
        return super().response_post_save_change(request, obj)
