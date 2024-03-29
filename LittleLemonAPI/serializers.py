from rest_framework import serializers
from .models import Category, MenuItem, Cart, Order, OrderItem
import bleach


class CategorySerializer(serializers.ModelSerializer):
  class Meta:  
    model = Category
    fields = ['slug', 'title']
    
    
class MenuItemSerializer(serializers.ModelSerializer):
  def validate_title(self, value):
    return bleach.clean(value)
  class Meta:
    model = MenuItem
    fields = ['title', 'price', 'featured', 'category']
    extra_kwargs = {
      'price': {'min_value': 1},
    }
    
    
class CartSerializer(serializers.ModelSerializer):
  class Meta:
    model = Cart
    fields = ['user', 'menuitem', 'quantity', 'unit_price', 'price']
    extra_kwargs = {
      'unit_price': {'min_value': 1},
    }
    
class OrderSerializer(serializers.ModelSerializer):
  class Meta:
    model = Order
    fields = ['user', 'delivery_crew', 'status', 'total', 'date']
    

class OrderItemSerializer(serializers.ModelSerializer):
  class Meta:
    model = OrderItem
    fields = ['order', 'menuitem', 'quantity', 'unit_price', 'price']
    extra_kwargs = {
      'unit_price': {'min_value': 1},
    }