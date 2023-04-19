from django.shortcuts import render
from .models import MenuItem, Category
from .serializers import MenuItemSerializer
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.forms.models import model_to_dict


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