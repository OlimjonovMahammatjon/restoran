from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Category, MenuItem, Table, Order, OrderItem
from .serializers import (
    CategorySerializer, MenuItemSerializer, TableSerializer,
    OrderSerializer, CreateOrderSerializer
)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]


class MenuItemViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MenuItem.objects.filter(is_available=True)
    serializer_class = MenuItemSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = MenuItem.objects.filter(is_available=True)
        category = self.request.query_params.get('category', None)
        if category is not None:
            queryset = queryset.filter(category=category)
        return queryset


class TableViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Table.objects.filter(is_active=True)
    serializer_class = TableSerializer
    permission_classes = [AllowAny]


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CreateOrderSerializer
        return OrderSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        order = self.get_object()
        new_status = request.data.get('status')
        
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            return Response({'status': 'Status yangilandi'})
        
        return Response(
            {'error': 'Noto\'g\'ri status'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=False, methods=['get'])
    def by_table(self, request):
        table_id = request.query_params.get('table_id')
        if not table_id:
            return Response(
                {'error': 'table_id parametri kerak'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        orders = Order.objects.filter(table_id=table_id).order_by('-created_at')
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def get_table_by_qr(request):
    """QR kod orqali stol ma'lumotlarini olish"""
    qr_data = request.GET.get('qr_data')
    if not qr_data:
        return Response(
            {'error': 'qr_data parametri kerak'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # QR data formatini tekshirish: "table_1", "table_2", etc.
    if qr_data.startswith('table_'):
        try:
            table_number = int(qr_data.split('_')[1])
            table = get_object_or_404(Table, number=table_number, is_active=True)
            serializer = TableSerializer(table)
            return Response(serializer.data)
        except (ValueError, IndexError):
            return Response(
                {'error': 'Noto\'g\'ri QR kod formati'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    return Response(
        {'error': 'QR kod topilmadi'}, 
        status=status.HTTP_404_NOT_FOUND
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def menu_by_category(request):
    """Kategoriya bo'yicha menyu"""
    categories = Category.objects.all()
    result = []
    
    for category in categories:
        menu_items = MenuItem.objects.filter(
            category=category, 
            is_available=True
        )
        result.append({
            'category': CategorySerializer(category).data,
            'items': MenuItemSerializer(menu_items, many=True).data
        })
    
    return Response(result)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """Admin panel uchun statistika"""
    from django.db.models import Count, Sum
    from django.utils import timezone
    from datetime import timedelta
    
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    
    stats = {
        'total_orders_today': Order.objects.filter(created_at__date=today).count(),
        'total_orders_week': Order.objects.filter(created_at__date__gte=week_ago).count(),
        'revenue_today': Order.objects.filter(
            created_at__date=today
        ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0,
        'revenue_week': Order.objects.filter(
            created_at__date__gte=week_ago
        ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0,
        'orders_by_status': Order.objects.values('status').annotate(
            count=Count('id')
        ),
        'active_tables': Table.objects.filter(is_active=True).count(),
        'menu_items_count': MenuItem.objects.filter(is_available=True).count(),
    }
    
    return Response(stats)