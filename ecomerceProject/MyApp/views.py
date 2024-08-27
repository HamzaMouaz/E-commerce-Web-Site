import base64
import io
import json
import pandas as pd
import plotly.express as px
from django.db import transaction
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import auth, messages
from matplotlib import pyplot as plt
from .forms import LoginForm, ProduitForm, ShippingInformationForm, SignUpForm
from django.contrib.auth import authenticate
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
import paypalrestsdk
from paypalrestsdk import Payment
from django.conf import settings
from .models import Cart, CartItem, Order
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .models import Userr
from .models import Cart, CartItem, Produit, Seller
# admin_dashboard/views.py
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import redirect
from functools import wraps
from django.contrib.auth import authenticate, login
from datetime import date



def seller_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        user=request.user
        if Seller.objects.filter(user=user).exists():
            return view_func(request, *args, **kwargs)
        return redirect('seller_dashboard')  # Redirige vers la page d'accueil si l'utilisateur n'est pas un vendeur
    return _wrapped_view

from django.contrib.auth.decorators import login_required

@seller_required
@login_required
def seller_dashboard(request):
    # Récupère les produits du vendeur actuel
    seller = request.user
    products = Produit.objects.all()
    return render(request, 'seller_dashboard.html', {'products': products})

def admin_login(request):
    user= request.user
        
    if user is not None:
        # Vérifie si l'utilisateur est un vendeur/admin
        if Seller.objects.filter(user=user).exists():  # Supposons que `is_seller` soit un champ dans votre modèle User
            #login(request, user)
            return redirect('seller_dashboard')  # Redirige vers le tableau de bord vendeur
        else:
            #return render(request, 'index.html', {'error': 'Vous n\'êtes pas autorisé à accéder à cette section.'})
            return redirect('index')
    else:
        #return render(request, 'index.html', {'error': 'Nom d\'utilisateur ou mot de passe incorrect.'})
        return redirect('index')
    

# Configurez le SDK PayPal avec vos informations d'identification
paypalrestsdk.configure({
    "mode": settings.PAYPAL_MODE,
    "client_id": settings.PAYPAL_CLIENT_ID,
    "client_secret": settings.PAYPAL_CLIENT_SECRET
})


def add_to_cart(request, product_id):
    product = get_object_or_404(Produit, id=product_id)
    product.sales+=1
    product.save()
    cart, created = Cart.objects.get_or_create(user=request.user)

    # Vérifier si le produit est déjà dans le panier
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += 1
    cart_item.save()

    return redirect('cart_detail')  # Rediriger vers la page de détail du panier


def cart_detail(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)
    total = sum(item.total_price for item in cart_items)

    return render(request, 'cart_detail.html', {'cart_items': cart_items, 'total': total})


def place_order(request):
    cart = Cart.objects.get(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)

    if request.method == 'POST':
        form = ShippingInformationForm(request.POST)
        if form.is_valid():
            shipping_info = form.save(commit=False)
            shipping_info.user = request.user
            shipping_info.save()

            total_price = sum(item.total_price for item in cart_items)
            seller = Seller.objects.get()  # Logique pour associer au vendeur

            with transaction.atomic():
                order = Order.objects.create(
                    user=request.user,
                    seller=seller,
                    shipping_info=shipping_info,
                    total_price=total_price,
                )
                order.products.set(cart_items)

                order.save()
            

            # Vider le panier après la commande
            cart_items.delete()
            #cart.save()
            return render(request, 'command_success.html')
    else:
        form = ShippingInformationForm()

    return render(request, 'place_order.html', {'form': form, 'cart_items': cart_items})



@login_required
def checkout(request):
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)

    if request.method == 'POST':
        total = sum(item.total_price for item in cart_items)

        # Créer un paiement PayPal
        payment = Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"},
            "redirect_urls": {
                "return_url": "http://localhost:8000/payment/execute",  # URL pour exécuter le paiement
                "cancel_url": "http://localhost:8000/payment/cancel"},  # URL pour annuler le paiement
            "transactions": [{
                "item_list": {
                    "items": [{
                        "name": "Total Purchase",
                        "sku": "001",
                        "price": str(total),
                        "currency": "USD",
                        "quantity": 1}]},
                "amount": {
                    "total": str(total),
                    "currency": "USD"},
                "description": "Payment for items in cart"}]})

        if payment.create():
            # Rediriger l'utilisateur vers PayPal pour le paiement
            for link in payment.links:
                if link.rel == "approval_url":
                    approval_url = link.href
                    return redirect(approval_url)
        else:
            messages.error(request, "Une erreur est survenue avec PayPal. Veuillez réessayer.")
            return redirect('checkout')

    total = sum(item.total_price for item in cart_items)
    return render(request, 'checkout.html', {'total': total})


@login_required
def execute_payment(request):
    payment_id = request.GET.get('paymentId')
    payer_id = request.GET.get('PayerID')

    payment = Payment.find(payment_id)

    if payment.execute({"payer_id": payer_id}):
        cart = get_object_or_404(Cart, user=request.user)
        cart.cartitem_set.all().delete()  # Vider le panier après un paiement réussi
        messages.success(request, "Paiement réussi ! Merci pour votre achat.")
        return redirect('order_confirmation')
    else:
        messages.error(request, "Le paiement a échoué. Veuillez réessayer.")
        return redirect('checkout')


@login_required
def chatbot_view(request):
    user_id = request.user.id
    user = Userr.objects.get(id=user_id)
    user_name = Userr.objects.get(id=user_id).username
    user_conversations = Produit.objects.filter(user=user)
    return render(request, 'chat.html', {'user_name': user_name, 'user_conversations':user_conversations})



def index(request):
    products = Produit.objects.all()
    user = request.user.username
    return render(request, 'index.html', { 'products':products, 'user':user})


def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('index')
        else:
            messages.error(request, 'Invalid login details')
            #return redirect('non')
    return render(request, 'login1.html', {'form': LoginForm})


def logout(request):
    auth.logout(request)
    messages.info(request, 'You have been logged out!!')
    return render(request, 'login1.html')



def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            #view_login(request,user)
            return redirect('login')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})


def charts(request):
    # Récupérer les données des produits
    produits = Produit.objects.all()
    product_names = [produit.name for produit in produits]
    sales_data = [produit.sales for produit in produits]

    # Créer le graphique interactif avec Plotly
    fig = px.pie(names=product_names, values=sales_data, labels={'names': 'Produits', 'values': 'Nombre de ventes'})
    fig.update_layout(title='Nombre de ventes par produit')

    # Convertir le graphique en HTML
    graph_html = fig.to_html(full_html=False)

    # Préparer les données pour le graphique
    data = {
        'product_names': [produit.name for produit in produits],
        'sales_data': [produit.sales for produit in produits],
    }
    # Convertir les données en DataFrame
    df = pd.DataFrame(data)
    
    # Créer le graphique à barres avec Plotly
    fig = px.bar(df, x='product_names', y='sales_data',
                 labels={'product_names': 'Produits', 'sales_data': 'Nombre de ventes'},
                 title='Nombre de ventes par produit')

    # Convertir le graphique en HTML
    graph_html3 = fig.to_html(full_html=False)
    # Récupérer toutes les ventes
    ventes = CartItem.objects.all()

    # Préparer les données pour le graphique
    data = []
    for vente in ventes:
        data.append({
            'product_name': vente.product.name,
            'date': vente.date_vente,
            'quantity': vente.quantity
        })

    # Convertir les données en DataFrame
    df = pd.DataFrame(data)
    
    # Créer le graphique avec Plotly
    fig = px.line(df, x='date', y='quantity', color='product_name', 
                  title='Nombre de ventes par produit au fil du temps',
                  labels={'date': 'date', 'quantity': 'Quantité vendue', 'product_name': 'Produit'})
    fig.update_layout(xaxis_title='date', yaxis_title='Quantité vendue')

    # Convertir le graphique en HTML
    graph_html2 = fig.to_html(full_html=False)

    # Passer le graphique au template
    return render(request, 'charts.html', {'graph_html': graph_html, 'graph_html2': graph_html3})


def manage_users(request):
    users = Userr.objects.all()
    return render(request, 'manage_users.html', {'users': users})


def edit_user(request, user_id):
    user = get_object_or_404(Userr, id=user_id)
    
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')

        # Mettre à jour l'utilisateur
        user.username = username
        user.email = email
        user.save()

        messages.success(request, 'User updated successfully.')
        return redirect('manage_users')

    return render(request, 'edit_user.html', {'user': user})

def delete_user(request, user_id):
    user = get_object_or_404(Userr, id=user_id)
    
    # Supprimer l'utilisateur
    user.delete()

    messages.success(request, 'User deleted successfully.')
    return redirect('manage_users')



def manage_product(request):
    products = Produit.objects.all()
    return render(request, 'produits.html', {'products': products})


def edit_product(request, product_id):
    product = get_object_or_404(Produit,id=product_id)
    
    if request.method == 'POST':
        image = request.POST.get('image')
        name = request.POST.get('name')
        sales = request.POST.get('sales')
        old_price = request.POST.get('old_price')
        price = request.POST.get('price')

        # Mettre à jour l'utilisateur
        product.image = image
        product.name= name
        product.sales=sales
        product.old_price=old_price
        product.price=price
        product.save()

        messages.success(request, 'Product updated successfully.')
        return redirect('manage_products')

    return render(request, 'edit_product.html', {'product': product})


def add_product(request):    
    if request.method == 'POST':
        form = ProduitForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()  # Sauvegarde le produit dans la base de données
            return redirect('manage_products')  # Redirige vers une liste de produits ou une autre page après l'ajout
    else:
        form = ProduitForm()
    
    return render(request, 'add_product.html', {'form': form})


def delete_product(request, product_id):
    product = get_object_or_404(Produit, id=product_id)
    
    # Supprimer l'utilisateur
    product.delete()

    messages.success(request, 'Product deleted successfully.')
    return redirect('manage_products')

def seller_orders(request):
    seller = Seller.objects.get(user=request.user)
    orders = Order.objects.filter(seller=seller)

    return render(request, 'seller_orders.html', {'orders': orders})

def update_order_status(request, order_id):
    if request.method == 'POST':
        order = get_object_or_404(Order, id=order_id)
        new_status = request.POST.get('status')
        order.status = new_status
        order.save()
        messages.success(request, f"L'état de la commande {order_id} a été mis à jour avec succès.")
    return redirect('seller_orders')


    