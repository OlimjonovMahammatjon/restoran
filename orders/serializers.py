from rest_framework import serializers
from .models import Category, MenuItem, Table, Order, OrderItem


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'created_at']


class MenuItemSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = MenuItem
        fields = [
            'id', 'title', 'description', 'price', 'weight', 
            'image', 'category', 'category_name', 'qr_code', 
            'is_available', 'created_at'
        ]


class TableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = ['id', 'number', 'capacity', 'qr_code', 'is_active']


class OrderItemSerializer(serializers.ModelSerializer):
    menu_item_title = serializers.CharField(source='menu_item.title', read_only=True)
    menu_item_image = serializers.ImageField(source='menu_item.image', read_only=True)
    
    class Meta:
        model = OrderItem
        fields = [
            'id', 'menu_item', 'menu_item_title', 'menu_item_image',
            'quantity', 'price', 'subtotal', 'special_instructions'
        ]
        read_only_fields = ['price', 'subtotal']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    table_number = serializers.IntegerField(source='table.number', read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'table', 'table_number', 'customer_name', 'customer_phone',
            'status', 'total_amount', 'created_at', 'updated_at', 'notes', 'items'
        ]
        read_only_fields = ['total_amount', 'created_at', 'updated_at']


class CreateOrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    
    class Meta:
        model = Order
        fields = ['table', 'customer_name', 'customer_phone', 'notes', 'items']
    
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)
        
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)
        
        order.calculate_total()
        return order