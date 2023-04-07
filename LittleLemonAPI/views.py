from django.shortcuts import render
from .models import MenuItem
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated


@api_view(['GET'])
def menu_items(request):
  menu_items = MenuItem.objects.all().values()
  return Response(list(menu_items), status=status.HTTP_200_OK)


@api_view(['POST', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def menu_items(request):
  if not request.user.groups.filter(name='Manager').exists():
    return Response({"message": "You do not have permission to do this."}, status=status.HTTP_403_FORBIDDEN)
  if request.method == 'POST':
    return Response({"message": "You used the POST method"}, status=status.HTTP_201_CREATED)
  if request.method == 'PUT':
    return Response({"message": "You used the PUT method"}, status=status.HTTP_200_OK)
  if request.method == 'PATCH':
    return Response({"message": "You used the PATCH method"}, status=status.HTTP_200_OK)
  if request.method == 'DELETE':
    return Response({"message": "You used the DELETE method"}, status=status.HTTP_200_OK)
  
  
@api_view(['GET'])
def single_menu_item(request, id):
  pass