from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet)
router.register(r'menu-items', views.MenuItemViewSet)
router.register(r'tables', views.TableViewSet)
router.register(r'orders', views.OrderViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('table-by-qr/', views.get_table_by_qr, name='table-by-qr'),
    path('menu-by-category/', views.menu_by_category, name='menu-by-category'),
    path('dashboard-stats/', views.dashboard_stats, name='dashboard-stats'),
]