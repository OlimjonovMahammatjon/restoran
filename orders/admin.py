from django.contrib import admin
from django.utils.html import format_html
from .models import Category, MenuItem, Table, Order, OrderItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']
    list_filter = ['created_at']


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'price', 'weight', 'is_available', 'image_preview', 'qr_code_preview']
    list_filter = ['category', 'is_available', 'created_at']
    search_fields = ['title', 'description']
    list_editable = ['price', 'is_available']
    readonly_fields = ['qr_code_preview']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" />', obj.image.url)
        return "Rasm yo'q"
    image_preview.short_description = "Rasm"
    
    def qr_code_preview(self, obj):
        if obj.qr_code:
            return format_html('<img src="{}" width="100" height="100" />', obj.qr_code.url)
        return "QR kod yo'q"
    qr_code_preview.short_description = "QR Kod"


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ['number', 'capacity', 'is_active', 'qr_code_preview']
    list_filter = ['is_active']
    list_editable = ['capacity', 'is_active']
    readonly_fields = ['qr_code_preview']
    
    def qr_code_preview(self, obj):
        if obj.qr_code:
            return format_html('<img src="{}" width="100" height="100" />', obj.qr_code.url)
        return "QR kod yo'q"
    qr_code_preview.short_description = "QR Kod"


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['subtotal']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'table', 'customer_name', 'status', 'total_amount', 'created_at']
    list_filter = ['status', 'created_at', 'table']
    search_fields = ['customer_name', 'customer_phone']
    list_editable = ['status']
    readonly_fields = ['total_amount', 'created_at', 'updated_at']
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('table', 'customer_name', 'customer_phone', 'status')
        }),
        ('Moliyaviy ma\'lumotlar', {
            'fields': ('total_amount',)
        }),
        ('Qo\'shimcha ma\'lumotlar', {
            'fields': ('notes', 'created_at', 'updated_at')
        }),
    )


# Admin panel sozlamalari
admin.site.site_header = "Restoran Boshqaruv Paneli"
admin.site.site_title = "Restoran Admin"
admin.site.index_title = "Boshqaruv Paneli"