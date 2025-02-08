from django import forms
from django.db.models import Count, Q
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from foodcartapp.models import Product, Restaurant, Order
from location.utils import get_or_create_location, calculate_distances_to_restaurants, \
    sort_restaurants_by_distance


class Login(forms.Form):
    username = forms.CharField(
        label="Логин",
        max_length=75,
        required=True,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Укажите имя пользователя"
        })
    )
    password = forms.CharField(
        label="Пароль",
        max_length=75,
        required=True,
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Введите пароль"
        })
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={"form": form})

    def post(self, request):
        form = Login(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")
        return render(request, "login.html", context={"form": form, "ivalid": True})


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy("restaurateur:login")


def is_manager(user):
    return user.is_staff


@user_passes_test(is_manager, login_url="restaurateur:login")
def view_products(request):
    restaurants = list(Restaurant.objects.order_by("name"))
    products = list(Product.objects.prefetch_related("menu_items"))
    products_with_restaurant_availability = [
        (
            product,
            [item.availability for item in product.menu_items.all()]
        )
        for product in products
    ]
    return render(
        request,
        template_name="products_list.html",
        context={
            "products_with_restaurant_availability": products_with_restaurant_availability,
            "restaurants": restaurants,
        },
    )


@user_passes_test(is_manager, login_url="restaurateur:login")
def view_restaurants(request):
    return render(
        request,
        template_name="restaurants_list.html",
        context={"restaurants": Restaurant.objects.all()},
    )


def get_available_restaurants(order_items):
    product_ids = [item.product_id for item in order_items]
    if not product_ids:
        return []
    restaurants = Restaurant.objects.filter(
        menu_items__product_id__in=product_ids,
        menu_items__availability=True
    ).annotate(
        num_products=Count('menu_items', filter=Q(menu_items__product_id__in=product_ids))
    ).filter(num_products=len(product_ids)).distinct()

    return list(restaurants)


@user_passes_test(is_manager, login_url="restaurateur:login")
def view_orders(request):
    orders = Order.objects.with_total_cost().prefetch_related('items__product')
    for order in orders:
        order_items = order.items.all()
        if not order_items:
            order.restaurants = []
            continue
        order.restaurants = get_available_restaurants(order_items)
        delivery_coords = get_or_create_location(order.address)
        if not delivery_coords:
            continue
        calculate_distances_to_restaurants(delivery_coords, order.restaurants)
        order.restaurants = sort_restaurants_by_distance(order.restaurants)

    return render(request, 'order_items.html', context={'orders': orders})
