from django.shortcuts import get_object_or_404
from .models import MenuItem, Cart, Order, OrderItem
from .serializers import MenuItemSerializer, OrderSerializer, OrderItemSerializer
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.contrib.auth.models import User, Group
import datetime
from django.core.paginator import Paginator, EmptyPage
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle



@api_view(['GET', 'POST'])
@throttle_classes([UserRateThrottle, AnonRateThrottle])
def menu_items(request):
  if request.method == 'GET':
    menu_items = MenuItem.objects.select_related('category').all()
    category_name = request.query_params.get('category')
    to_price = request.query_params.get('to_price')
    search = request.query_params.get('search')
    ordering = request.query_params.get('ordering')
    perpage = request.query_params.get('perpage', default=2)
    if int(perpage) > 10:
      return Response({"message": "You are limited to 10 results per page"}, status=status.HTTP_400_BAD_REQUEST)
    
    page = request.query_params.get('page', default=1)
    if category_name:
      menu_items = menu_items.filter(category__title=category_name)
    if to_price:
      menu_items = menu_items.filter(price__lte=to_price)
    if search:
      menu_items = menu_items.filter(title__icontains=search)
    if ordering:
      ordering_fields = ordering.split(',')
      menu_items = menu_items.order_by(*ordering_fields)
    paginator = Paginator(menu_items, per_page=perpage)
    try:
      menu_items = paginator.page(number=page)
    except EmptyPage:
      menu_items = []
    serialized_items = MenuItemSerializer(menu_items, many=True)
    return Response(serialized_items.data, status=status.HTTP_200_OK)
  
  if not request.user.groups.filter(name='Manager').exists():
    return Response({"message": "You do not have permission to do this."}, status=status.HTTP_403_FORBIDDEN)
  
  if request.method == 'POST':
    serialized_item = MenuItemSerializer(data=request.data)
    serialized_item.is_valid(raise_exception=True)
    serialized_item.save()
    return Response(serialized_item.data, status=status.HTTP_201_CREATED)
  
  
@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def single_menu_item(request, id):
  # Allows authenticated users to access one item's details
  try:
    item = MenuItem.objects.get(pk=id)
  except MenuItem.DoesNotExist:
    return Response({"message": "The item does not exist"}, status=status.HTTP_404_NOT_FOUND)
    
  if request.method == 'GET':
    item_serializer = MenuItemSerializer(item)
    print(item_serializer.data)
    return Response(item_serializer.data, status=status.HTTP_200_OK)
  
  # Ensures only managers can use PUT, PATCH and DELETE
  if not request.user.groups.filter(name='Manager').exists():
    return Response({"message": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)
  
  if request.method == 'PUT':
    serialized_item = MenuItemSerializer(item, data=request.data)
    if serialized_item.is_valid():
      serialized_item.save()
      return Response(serialized_item.data, status=status.HTTP_200_OK)
    return Response({"message": "Could not update the item."}, status=status.HTTP_400_BAD_REQUEST)
  
  if request.method == 'PATCH':
    serialized_item = MenuItemSerializer(item, data=request.data, partial=True)
    if serialized_item.is_valid():
      serialized_item.save()
      return Response(serialized_item.data, status=status.HTTP_200_OK)
    return Response({"message": "Could not update the item."}, status=status.HTTP_400_BAD_REQUEST)
  
  if request.method == 'DELETE':
    item.delete()
    return Response({"message": "Item deleted successfully."}, status=status.HTTP_200_OK)
  
  
@api_view(['GET', 'POST'])
@permission_classes([IsAdminUser])
def managers(request):
  """Allows admin to list users of the manager group and to add users to the group""" 
  
  if request.method == 'GET':
    managers = User.objects.filter(groups__name='Manager')
    manager_dict = {}
    for manager in managers:
      manager_dict[manager.pk] = manager.username
    return Response(manager_dict, status=status.HTTP_200_OK)
  
  if request.method == 'POST':
    username = request.data['username']
    if username:
      user = get_object_or_404(User, username=username)
      managers = Group.objects.get(name='Manager')
      managers.user_set.add(user)
      return Response({"message": "User added to manager group"}, status=status.HTTP_201_CREATED)
    
    return Response({"message": "error"}, status=status.HTTP_400_BAD_REQUEST)
  
  
@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def remove_manager(request, id):
  """Allows admin to remove a user from the manager group"""
  
  manager = get_object_or_404(User, pk=id)
  
  if manager.groups.filter(name='Manager').exists():
    managers = Group.objects.get(name='Manager') 
    managers.user_set.remove(manager)
    return Response({"message": "User removed from manager group"}, status=status.HTTP_200_OK)
  
  return Response({"message": "This user is not a manager."}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def delivery_crew(request):
  """Allows managers to list users from the delivery crew group and to add users to the group"""
  
  if not request.user.groups.filter(name='Manager').exists():
    return Response({"message": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)
  
  if request.method == 'GET':
    members = User.objects.filter(groups__name='Delivery Crew')
    delivery_crew_dict = {}
    for member in members:
      delivery_crew_dict[member.pk] = member.username
    return Response(delivery_crew_dict, status=status.HTTP_200_OK)
  
  if request.method == 'POST':
    username = request.data['username']
    if username:
      user = get_object_or_404(User, username=username)
      crew = Group.objects.get(name='Delivery Crew')
      crew.user_set.add(user)
      return Response({"message": "User added to delivery crew"}, status=status.HTTP_201_CREATED)
    
    return Response({"message": "error"}, status=status.HTTP_400_BAD_REQUEST)
  
  
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def remove_delivery_crew(request, id):
  """Allows managers to remove a user from the delivery crew"""
  if not request.user.groups.filter(name='Manager').exists():
    return Response({"message": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)
  
  delivery_person = get_object_or_404(User, pk=id)
  
  if delivery_person.groups.filter(name='Delivery Crew').exists():
    delivery_crew = Group.objects.get(name='Delivery Crew')
    delivery_crew.user_set.remove(delivery_person)
    return Response({"message": "User removed from delivery crew"}, status=status.HTTP_200_OK)
  
  return Response({"message": "This user is not part of the delivery crew"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def cart(request):
  """Allows customers to see, add and remove items in/from their cart"""
  
  user = request.user
  
  if request.method == 'GET':
    cart = Cart.objects.filter(user=user.id)
    cart_list = [{"menuitem": row.menuitem.title, "quantity": row.quantity, "unit price": row.unit_price, "price": row.price} for row in cart]
    return Response(cart_list, status=status.HTTP_200_OK)
    
  # 
  if request.method == 'POST':
    menu_item = MenuItem.objects.get(title=request.data['menu item'])
    quantity = float(request.data['quantity'])
    unit_price = float(menu_item.price)
    try:
      cart = Cart.objects.get(user=user.id, menuitem_id=menu_item.id)
      cart.menuitem = menu_item
      cart.quantity = quantity
      cart.unit_price = unit_price
      cart.price = quantity * unit_price
      cart.save()
    except Cart.DoesNotExist:
      cart = Cart.objects.create(user=user, menuitem=menu_item, quantity=quantity, unit_price=unit_price, price=quantity*unit_price)
      cart.save()
    
    return Response({"message": "Item added to cart successfully"}, status=status.HTTP_201_CREATED)
  
  if request.method == 'DELETE':
    cart = Cart.objects.filter(user=user.id)
    cart.delete()
    return Response({"message": "Your cart is now empty."}, status=status.HTTP_200_OK)
  
  
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def orders(request):
  """Allows managers to see every order, customer to see their order(s) and submit new orders, and delivery crew to see orders assigned to them"""
  
  if request.method == 'GET':
    # Manager view
    if request.user.groups.filter(name='Manager').exists():
      orders = Order.objects.all()
      serializer = OrderSerializer(orders, many=True)
      return Response(serializer.data, status=status.HTTP_200_OK)
    
    # Delivery crew view
    elif request.user.groups.filter(name='Delivery Crew').exists():
      orders = Order.objects.filter(delivery_crew=request.user)
      serializer = OrderSerializer(orders, many=True)
      return Response(serializer.data, status=status.HTTP_200_OK)
    
    # Customer view
    else:
      orders = Order.objects.filter(user=request.user)
      serializer = OrderSerializer(orders, many=True)
      return Response(serializer.data, status=status.HTTP_200_OK)
      
  # Customer submits an order
  if request.method == 'POST':
    cart = Cart.objects.filter(user=request.user)
    order = Order.objects.create(user=request.user, total=0, date=str(datetime.date.today()))
    for item in cart:
      data = {"order": order.id, "menuitem": item.menuitem.id, "quantity": item.quantity, "unit_price": item.unit_price, "price": item.price}
      print(data)
      order_item = OrderItemSerializer(data=data)
      order.total += item.price
      if order_item.is_valid():
        order_item.save()
      order.save()
    cart.delete()
    return Response({"message": "Order submitted"}, status=status.HTTP_201_CREATED)
  
  
@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def single_order(request, id):
  
  order = get_object_or_404(Order, pk=id)
  
  # Customers can see items in one of their orders
  if request.method == 'GET':
    if order.user != request.user:
      return Response({"message": "This order is not yours."}, status=status.HTTP_403_FORBIDDEN)
    
    order_items = OrderItem.objects.filter(order=order)
    serialized_items = OrderItemSerializer(order_items, many=True)
    return Response(serialized_items.data, status=status.HTTP_200_OK)
  
  # Only managers can update every parameter of an order
  if request.method == 'PUT':
    if not request.user.groups.filter(name='Manager').exists():
      return Response({"message": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)
    
    serialized_order = OrderItemSerializer(order, data=request.data)
    serialized_order.is_valid(raise_exception=True)
    serialized_order.save()
    return Response(serialized_order.data, status=status.HTTP_200_OK)
    
  # Managers can update one by one every parameter of an order
  if request.method == 'PATCH':
    if request.user.groups.filter(name='Manager').exists():
      serialized_order = OrderSerializer(order, data=request.data, partial=True)
      serialized_order.is_valid(raise_exception=True)
      serialized_order.save()
      return Response(serialized_order.data, status=status.HTTP_200_OK)
    
    # Delivery crew can update the status of orders assigned to them
    elif request.user.groups.filter(name='Delivery Crew').exists():
      if order.delivery_crew != request.user:
        return Response({"message": "This order is not assigned to you"}, status=status.HTTP_403_FORBIDDEN)
      
      if len(request.data) > 1 or 'status' not in request.data.keys():
        return Response({"message": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)
      
      serialized_order = OrderSerializer(order, data=request.data, partial=True)
      serialized_order.is_valid(raise_exception=True)
      serialized_order.save()
      return Response(serialized_order.data, status=status.HTTP_200_OK)
    
    else:
      return Response({"message": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)
    
  # Managers can delete an order
  if request.method == 'DELETE':
    order.delete()
    return Response({"message": "Order deleted"}, status=status.HTTP_200_OK)