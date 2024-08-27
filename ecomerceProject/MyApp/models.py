from django.db import models
from django.contrib.auth.models import User
from django.conf import settings


class Userr(User):
    pass

class Seller(models.Model):
    user = models.OneToOneField(Userr, on_delete=models.CASCADE)
    # Ajoute d'autres champs si nécessaire, comme le nom du magasin, le numéro de téléphone, etc.

    def __str__(self):
        return self.user.username

class Produit(models.Model):
    image = models.ImageField(upload_to='static/images/')
    name = models.TextField()
    sales = models.IntegerField(default=0)
    old_price = models.FloatField(blank=True)
    price = models.FloatField()

    def __str__(self):
        return self.name

class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    #user = models.OneToOneField(Userr, on_delete=models.CASCADE)  # Un panier par utilisateur
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Panier de {self.user.username}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)  # Chaque élément est lié à un panier
    product = models.ForeignKey(Produit, on_delete=models.CASCADE)
    date_vente = models.DateField(blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.product.name} (x{self.quantity})"

    @property
    def total_price(self):
        return self.product.price * self.quantity



# Nouveau modèle pour les informations d'expédition
class ShippingInformation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    wilaya = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    address = models.TextField()

    def __str__(self):
        return f"Informations d'expédition pour {self.full_name}"

# Nouveau modèle pour les commandes
class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE)
    shipping_info = models.ForeignKey(ShippingInformation, on_delete=models.CASCADE)
    products = models.ManyToManyField(CartItem)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Shipped', 'Shipped'), ('Delivered', 'Delivered')], default='Pending')

    def __str__(self):
        return f"Commande {self.id} par {self.user.username}"
# Create your models here.
