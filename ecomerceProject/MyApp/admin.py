from django.contrib import admin
from .models import *

# Enregistrement des modèles auprès de l'interface d'administration
admin.site.register(Userr)
admin.site.register(Produit)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Seller)
admin.site.register(Order)
