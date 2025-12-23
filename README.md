# Restoran va Fastfood API

Django REST Framework asosida yaratilgan restoran buyurtma tizimi.

## Xususiyatlar

- QR kod orqali stol identifikatsiyasi
- Menyu boshqaruvi (rasm, tavsif, narx, og'irlik)
- Buyurtma qabul qilish va boshqarish
- Admin panel orqali to'liq boshqaruv
- REST API endpoints

## O'rnatish

1. Virtual muhit yarating:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# yoki
.venv\Scripts\activate  # Windows
```

2. Bog'liqliklarni o'rnating:
```bash
pip install -r requirements.txt
```

3. Ma'lumotlar bazasini yarating:
```bash
python manage.py makemigrations
python manage.py migrate
```

4. Superuser yarating:
```bash
python manage.py createsuperuser
```

5. Serverni ishga tushiring:
```bash
python manage.py runserver
```

## API Endpoints

### Umumiy foydalanish (autentifikatsiya shart emas)

- `GET /api/categories/` - Kategoriyalar ro'yxati
- `GET /api/menu-items/` - Menyu elementlari
- `GET /api/tables/` - Stollar ro'yxati
- `GET /api/table-by-qr/?qr_data=table_1` - QR kod orqali stol
- `GET /api/menu-by-category/` - Kategoriya bo'yicha menyu
- `POST /api/orders/` - Yangi buyurtma yaratish

### Admin uchun (autentifikatsiya kerak)

- `GET /api/orders/` - Barcha buyurtmalar
- `PATCH /api/orders/{id}/update_status/` - Buyurtma holatini yangilash
- `GET /api/orders/by_table/?table_id=1` - Stol bo'yicha buyurtmalar
- `GET /api/dashboard-stats/` - Dashboard statistikasi

## Buyurtma yaratish misoli

```json
POST /api/orders/
{
    "table": 1,
    "customer_name": "Akmal Akramov",
    "customer_phone": "+998901234567",
    "notes": "Achchiq bo'lmasin",
    "items": [
        {
            "menu_item": 1,
            "quantity": 2,
            "special_instructions": "Kam tuzli"
        },
        {
            "menu_item": 3,
            "quantity": 1
        }
    ]
}
```

## Admin Panel

Admin panelga kirish: `http://localhost:8000/admin/`

Admin panel orqali:
- Kategoriya va menyu boshqaruvi
- Stol va QR kod yaratish
- Buyurtmalarni kuzatish va boshqarish
- Statistika ko'rish

## QR Kod Tizimi

Har bir stol uchun avtomatik QR kod yaratiladi. QR kod formati: `table_{stol_raqami}`

Mijozlar QR kodni skanerlaydi va `/api/table-by-qr/?qr_data=table_1` endpoint orqali stol ma'lumotlarini oladi.