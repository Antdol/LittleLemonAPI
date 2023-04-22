from django.shortcuts import get_object_or_404
from .models import MenuItem
from .serializers import MenuItemSerializer
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User, Group
from django.core.serializers import serialize
import json



@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def menu_items(request):
  if request.method == 'GET':
    menu_items = MenuItem.objects.all().values()
    return Response(list(menu_items), status=status.HTTP_200_OK)
  
  if not request.user.groups.filter(name='Manager').exists():
    return Response({"message": "You do not have permission to do this."}, status=status.HTTP_403_FORBIDDEN)
  
  if request.method == 'POST':
    serialized_item = MenuItemSerializer(data=request.data)
    serialized_item.is_valid(raise_exception=True)
    serialized_item.save()
    return Response(serialized_item.data, status=status.HTTP_201_CREATED)
  
  
@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
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
@permission_classes([IsAuthenticated])
def managers(request):
  """Allows managers to list users of the manager group and to add users to the group""" 
  
  if not request.user.groups.filter(name='Manager').exists():
    return Response({"message": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)
  
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
@permission_classes([IsAuthenticated])
def remove_manager(request, id):
  """Allows managers to remove a user from the manager group"""
  
  if not request.user.groups.filter(name='Manager').exists():
    return Response({"message": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)
  
  manager = get_object_or_404(User, pk=id)
  
  if manager.groups.filter(name='Manager').exists():
    managers = Group.objects.get(name='Manager') 
    managers.user_set.remove(manager)
    return Response({"message": "User removed from manager group"}, status=status.HTTP_200_OK)
  
  return Response({"message": "This user is not a manager."}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
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