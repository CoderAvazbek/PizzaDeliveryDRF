from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from . import serializers
from .models import Order
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, IsAdminUser
from django.contrib.auth import get_user_model

# Create your views here.

User = get_user_model()

class HelloOrdersView(generics.GenericAPIView):
    def get(self, request):
        message = {
            "message": "Hello Orders"
        }
        return Response(message, status=status.HTTP_200_OK)


class OrderCreateListView(generics.GenericAPIView):
    serializer_class = serializers.OrderCreationSerializers
    queryset = Order.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.all()
        serializer = self.serializer_class(instance=orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        data = request.data
        serializer = self.serializer_class(data=data)
        user = request.user

        if serializer.is_valid():
            serializer.save(customer=user)
            return Response(data=serializer.data, status=status.HTTP_201_CREATED)

        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderDetailView(generics.GenericAPIView):
    serializer_class = serializers.OrderDetailSerializer
    permission_classes = [IsAdminUser]

    def get(self, request, order_id):
        order = get_object_or_404(Order, pk=order_id)
        serializer = self.serializer_class(instance=order)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def put(self, request, order_id):
        data = request.data
        order = get_object_or_404(Order, pk=order_id)
        serializer = self.serializer_class(data=data, instance=order)
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def delete(self, request, order_id):
        order = get_object_or_404(Order, pk=order_id)
        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    


class UpdateOrderStatus(generics.GenericAPIView):
    serializer_class = serializers.OrderStatusUpdateSerializer
    

    def put(self, request, order_id):
        order = get_object_or_404(Order, pk=order_id)

        data = request.data

        serializer = self.serializer_class(data=data, instance=order)

        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class UserOrdersView(generics.GenericAPIView):
    serializer_class = serializers.OrderDetailSerializer
    queryset = Order.objects.all()

    def get(self, request, user_id):
        user = User.objects.get(pk=user_id)
        orders = Order.objects.all().filter(customer=user)
        serializer = self.serializer_class(instance=orders, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)
    


class UserOrderDetail(generics.GenericAPIView):
    serializer_class = serializers.OrderDetailSerializer

    def get(self, request, user_id, order_id):
        try:
            user = User.objects.get(pk=user_id)
            order = Order.objects.filter(customer=user, pk=order_id).first()
            if not order:
                return Response(
                    {"detail": "Order not found."},
                    status=status.HTTP_404_NOT_FOUND
                )
            serializer = self.serializer_class(instance=order)
            return Response(data=serializer.data, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response(
                {"detail": "User not found."},
                status=status.HTTP_404_NOT_FOUND
            )

