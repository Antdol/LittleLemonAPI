from rest_framework import serializers
from .models import Category, MenuItem, Cart, Order, OrderItem


class CategorySerializer(serializers.ModelSerializer):
  class Meta:  
    model = Category
    fields = ['slug', 'title']
    
    
class MenuItemSerializer(serializers.ModelSerializer):
  class Meta:
    model = MenuItem
    fields = ['title', 'price', 'featured', 'category']
    
    
class CartSerializer(serializers.ModelSerializer):
  class Meta:
    model = Cart
    fields = ['user', 'menuitem', 'quantity', 'unit_price', 'price']
    
    
class OrderSerializer(serializers.ModelSerializer):
  class Meta:
    model = Order
    fields = ['user', 'delivery_crew', 'status', 'total', 'date']
    

class OrderItemSerializer(serializers.ModelSerializer):
  class Meta:
    model = OrderItem
    fields = ['order', 'menuitem', 'quantity', 'unit_price', 'price']