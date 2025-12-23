from django.db import models
from django.contrib.auth.models import User
import qrcode
from io import BytesIO
from django.core.files import File
import uuid


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Kategoriya nomi")
    description = models.TextField(blank=True, verbose_name="Tavsif")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Kategoriya"
        verbose_name_plural = "Kategoriyalar"
    
    def __str__(self):
        return self.name


class MenuItem(models.Model):
    title = models.CharField(max_length=200, verbose_name="Taom nomi")
    description = models.TextField(verbose_name="Tavsif")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Narx")
    weight = models.CharField(max_length=50, verbose_name="Og'irligi")
    image = models.ImageField(upload_to='menu_items/', verbose_name="Rasm")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Kategoriya")
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, verbose_name="QR Kod")
    is_available = models.BooleanField(default=True, verbose_name="Mavjud")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Taom"
        verbose_name_plural = "Taomlar"
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.qr_code:
            qr_data = f"menu_item_{self.id}_{uuid.uuid4().hex[:8]}"
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(qr_data)
            qr.make(fit=True)
            
            qr_image = qr.make_image(fill_color="black", back_color="white")
            buffer = BytesIO()
            qr_image.save(buffer, format='PNG')
            buffer.seek(0)
            
            filename = f'qr_{self.title}_{uuid.uuid4().hex[:8]}.png'
            self.qr_code.save(filename, File(buffer), save=False)
        
        super().save(*args, **kwargs)


class Table(models.Model):
    number = models.IntegerField(unique=True, verbose_name="Stol raqami")
    capacity = models.IntegerField(verbose_name="Sig'imi")
    qr_code = models.ImageField(upload_to='table_qr_codes/', blank=True, verbose_name="QR Kod")
    is_active = models.BooleanField(default=True, verbose_name="Faol")
    
    class Meta:
        verbose_name = "Stol"
        verbose_name_plural = "Stollar"
    
    def __str__(self):
        return f"Stol #{self.number}"
    
    def save(self, *args, **kwargs):
        if not self.qr_code:
            qr_data = f"table_{self.number}"
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(qr_data)
            qr.make(fit=True)
            
            qr_image = qr.make_image(fill_color="black", back_color="white")
            buffer = BytesIO()
            qr_image.save(buffer, format='PNG')
            buffer.seek(0)
            
            filename = f'table_qr_{self.number}.png'
            self.qr_code.save(filename, File(buffer), save=False)
        
        super().save(*args, **kwargs)


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Kutilmoqda'),
        ('confirmed', 'Tasdiqlangan'),
        ('preparing', 'Tayyorlanmoqda'),
        ('ready', 'Tayyor'),
        ('delivered', 'Yetkazilgan'),
        ('cancelled', 'Bekor qilingan'),
    ]
    
    table = models.ForeignKey(Table, on_delete=models.CASCADE, verbose_name="Stol")
    customer_name = models.CharField(max_length=100, verbose_name="Mijoz ismi")
    customer_phone = models.CharField(max_length=20, blank=True, verbose_name="Telefon")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Holat")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Umumiy summa")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqt")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Yangilangan vaqt")
    notes = models.TextField(blank=True, verbose_name="Izohlar")
    
    class Meta:
        verbose_name = "Buyurtma"
        verbose_name_plural = "Buyurtmalar"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Buyurtma #{self.id} - Stol #{self.table.number}"
    
    def calculate_total(self):
        total = sum(item.subtotal for item in self.items.all())
        self.total_amount = total
        self.save()
        return total
# sjbfsjhfsjhdfsjh 

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE, verbose_name="Buyurtma")
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, verbose_name="Taom")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Miqdor")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Narx")
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Jami")
    special_instructions = models.TextField(blank=True, verbose_name="Maxsus ko'rsatmalar")
    
    class Meta:
        verbose_name = "Buyurtma elementi"
        verbose_name_plural = "Buyurtma elementlari"
    
    def save(self, *args, **kwargs):
        self.price = self.menu_item.price
        self.subtotal = self.price * self.quantity
        super().save(*args, **kwargs)
        self.order.calculate_total()
    
    def __str__(self):
        return f"{self.menu_item.title} x {self.quantity}"