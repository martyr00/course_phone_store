import os
from datetime import datetime

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models, connection, transaction
from django.utils import timezone
from psycopg2 import ProgrammingError

from base.utils import get_user_image_upload_path, get_telephone_image_upload_path, dictfetchall


class City(models.Model):
    name = models.CharField(max_length=100)


class Region(models.Model):
    name = models.CharField(max_length=100)
    city = models.ForeignKey(City, on_delete=models.CASCADE)


class Address(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    street_name = models.CharField(max_length=100)
    post_code = models.CharField(max_length=10)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=get_user_image_upload_path, null=True, blank=True)
    number_telephone = models.CharField(max_length=100, null=True, blank=True)
    address = models.ForeignKey(Address, on_delete=models.CASCADE, null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.user.username

    @classmethod
    def post(cls, data):
        username = data['username']
        email = data['email']
        password = make_password(data['password'])
        first_name = data['first_name']
        second_name = data['second_name']

        image = data['image']
        number_telephone = data['image']
        birth_date = data['image']
        address_id = data['address_id']

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO auth_user (
                    username, 
                    email, 
                    password, 
                    first_name, 
                    second_name, 
                    is_staff, 
                    is_active, 
                    date_joined
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
                RETURNING id;
            """, [username, email, password, first_name, second_name, False, True])
            user_id = cursor.fetchone()[0]
            cursor.execute("""
                            INSERT INTO base_userprofile (
                                user_id,
                                image, 
                                number_telephone, 
                                birth_date, 
                                address_id, 
                            )
                            VALUES (%s, %s, %s, %s, %s)
                        """, [user_id, image, number_telephone, birth_date, address_id])

    @classmethod
    def get_all(cls):
        with connection.cursor() as cursor:
            query = """SELECT
                auth_user.id AS id,
                auth_user.last_login AS last_login,
                auth_user.is_superuser AS is_superuser,
                auth_user.username AS username,
                auth_user.first_name AS first_name,
                auth_user.last_name AS last_name,
                auth_user.email AS email,
                auth_user.is_staff AS is_staff,
                auth_user.is_active AS is_active,
                auth_user.date_joined AS date_joined,
                base_userprofile.image AS image,
                base_userprofile.number_telephone AS number_telephone,
                base_address.street_name AS street,
                base_address.post_code AS post_code,
                base_city.name AS city,
                base_region.name AS region
                FROM auth_user JOIN base_userprofile 
                    ON auth_user.id = base_userprofile.user_id
                LEFT JOIN base_address 
                    ON base_userprofile.address_id = base_address.id
                LEFT JOIN base_city 
                    ON base_address.city_id = base_city.id
                LEFT JOIN base_region 
                    ON base_address.region_id = base_region.id
            """
            cursor.execute(query)
            result = dictfetchall(cursor)
            return result

    @classmethod
    def patch(cls, user_id, data):
        user_fields = ['username', 'first_name', 'last_name', 'email', 'password', 'is_staff', 'is_active',
                       'date_joined']
        profile_fields = ['image', 'number_telephone', 'address_id', 'birth_date']

        user_data = {key: value for key, value in data.items() if key in user_fields}
        profile_data = {key: value for key, value in data.items() if key in profile_fields}

        try:
            with transaction.atomic():
                if user_data:
                    set_clause = ", ".join(f"{field} = %s" for field in user_data.keys())
                    query = f"""
                        UPDATE auth_user
                        SET {set_clause}
                        WHERE id = %s;
                    """
                    with connection.cursor() as cursor:
                        cursor.execute(query, list(user_data.values()) + [user_id])

                if profile_data:
                    set_clause = ", ".join(f"{field} = %s" for field in profile_data.keys())
                    query = f"""
                        UPDATE base_userprofile
                        SET {set_clause}
                        WHERE user_id = %s;
                    """
                    with connection.cursor() as cursor:
                        cursor.execute(query, list(profile_data.values()) + [user_id])

                return cls.get_item(user_id)
        except ProgrammingError as e:
            raise e

    @classmethod
    def get_item(cls, user_id):
        with connection.cursor() as cursor:
            query = """
            SELECT
                auth_user.last_login AS last_login,
                auth_user.is_superuser AS is_superuser,
                auth_user.username AS username,
                auth_user.first_name AS first_name,
                auth_user.last_name AS last_name,
                auth_user.email AS email,
                auth_user.is_staff AS is_staff,
                auth_user.is_active AS is_active,
                auth_user.date_joined AS date_joined,
                base_userprofile.image AS image,
                base_userprofile.number_telephone AS number_telephone,
                base_address.street_name AS street,
                base_address.post_code AS post_code,
                base_city.name AS city,
                base_region.name AS region
            FROM auth_user JOIN base_userprofile 
                ON auth_user.id = base_userprofile.user_id
            LEFT JOIN base_address 
                ON base_userprofile.address_id = base_address.id
            LEFT JOIN base_city 
                ON base_address.city_id = base_city.id
            LEFT JOIN base_region 
                ON base_address.region_id = base_region.id
            WHERE auth_user.id = %s
            """
            cursor.execute(query, [user_id])
            columns = [col[0] for col in cursor.description]
            result = cursor.fetchone()
            if result:
                result = dict(zip(columns, result))
            return result

    @classmethod
    def get_item_admin(cls, user_id):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    auth_user.last_login AS last_login,
                    auth_user.is_superuser AS is_superuser,
                    auth_user.username AS username,
                    auth_user.first_name AS first_name,
                    auth_user.last_name AS last_name,
                    auth_user.email AS email,
                    auth_user.is_staff AS is_staff,
                    auth_user.is_active AS is_active,
                    auth_user.date_joined AS date_joined,
                    base_userprofile.image AS image,
                    base_userprofile.number_telephone AS number_telephone,
                    base_address.street_name AS street,
                    base_address.post_code AS post_code,
                    base_city.name AS city,
                    base_region.name AS region
                FROM auth_user
                JOIN base_userprofile ON auth_user.id = base_userprofile.user_id
                LEFT JOIN base_address ON base_userprofile.address_id = base_address.id
                LEFT JOIN base_city ON base_address.city_id = base_city.id
                LEFT JOIN base_region ON base_address.region_id = base_region.id
                WHERE auth_user.id = %s
            """, [user_id])
            user_data = dictfetchall(cursor)

            cursor.execute("""
                SELECT
                    base_order.id,
                    base_order.number_telephone,
                    base_order.status,
                    base_order.created_time,
                    base_order.update_time,
                    base_order.address_id,
                    base_orderdetails.price,
                    base_orderdetails.amount,
                    base_orderdetails.telephone_id
                FROM base_order
                JOIN base_orderdetails ON base_order.id = base_orderdetails.order_id
                WHERE base_order.user_id = %s
            """, [user_id])
            order_data = dictfetchall(cursor)

        combined_data = {
            'user': user_data[0],
            'orders': order_data
        }

        return combined_data


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    number_telephone = models.CharField(max_length=100)
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    STATUS_CHOICES = [
        ('Preparation', 'Preparation'),
        ('Dispatch', 'Dispatch'),
        ('Done', 'Done'),
        ('Canceled', 'Canceled'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='created_time')
    update_time = models.DateTimeField(auto_now=True, verbose_name='update_time')

    @classmethod
    def create_order_with_details(cls, user_id, number_telephone, address_id, status, telephone_id, price, amount):
        with connection.cursor() as cursor:
            try:
                sql_order = """
                    INSERT INTO orders (user_id, number_telephone, address_id, status, created_time, update_time)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                created_time = timezone.now()
                cursor.execute(sql_order, [user_id, number_telephone, address_id, status, created_time, created_time])
                order_id = cursor.lastrowid

                sql_order_details = """
                    INSERT INTO order_details (order_id, telephone_id, price, amount, created_time)
                    VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(sql_order_details, [order_id, telephone_id, price, amount, created_time])

                connection.commit()

                return True
            except Exception as e:
                connection.rollback()
                print(f"Error creating order with details: {e}")
                return False


class Brand(models.Model):
    title = models.CharField(max_length=50, unique=True)
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='created_time')

    @classmethod
    def get_item(cls, brand_id):
        with connection.cursor() as cursor:
            query = """
                SELECT id, title
                FROM base_brand
                WHERE id = %s
            """
            cursor.execute(query, [brand_id])
            result = dictfetchall(cursor)
            return result

    @classmethod
    def get_all(cls):
        with connection.cursor() as cursor:
            query = """
            SELECT id, title
            FROM base_brand
            """
            cursor.execute(query)
            result = dictfetchall(cursor)
            return result

    @classmethod
    def post_item(cls, data):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data['created_time'] = current_time

        with connection.cursor() as cursor:
            query_telephone = """
                INSERT INTO base_brand (
                    title,
                    created_time
                )
                VALUES (%s, %s)
                RETURNING id;
            """
            cursor.execute(
                query_telephone, [
                    data.get('title'),
                    data['created_time'],
                ])
            new_telephone_id = cursor.fetchone()[0]
        return Brand.get_item(new_telephone_id)

    @classmethod
    def delete_item(cls, base_brand):
        with connection.cursor() as cursor:
            query = """
                    DELETE FROM base_brand
                    WHERE id = %s;
                """
            cursor.execute(query, [base_brand])

    @classmethod
    def patch_item(cls, brand_id, data):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data['created_time'] = current_time
        with connection.cursor() as cursor:
            set_clause = ", ".join(f"{field} = %s" for field in data.keys())
            query_telephone = f"""
                 UPDATE base_brand
                 SET {set_clause}
                 WHERE id = %s;
             """
            cursor.execute(
                query_telephone, list(data.values()) + [brand_id]
            )

            return Brand.get_item(brand_id)


class Telephone(models.Model):
    title = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=200)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    diagonal_screen = models.FloatField()
    built_in_memory = models.CharField(max_length=20)
    price = models.IntegerField()
    discount = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    recommended_price = models.IntegerField(null=True, blank=True)
    weight = models.FloatField()
    number_stock = models.IntegerField()
    release_date = models.DateField()
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='created_time')
    update_time = models.DateTimeField(auto_now=True, verbose_name='update_time')

    @classmethod
    def post_item(cls, data):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data['created_time'] = current_time
        data['update_time'] = current_time

        with connection.cursor() as cursor:
            query_telephone = """
                INSERT INTO base_telephone (
                    title,
                    description,
                    diagonal_screen,
                    built_in_memory,
                    price,
                    discount,
                    recommended_price,
                    weight,
                    number_stock,
                    brand_id,
                    release_date,
                    created_time,
                    update_time
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id;
            """
            cursor.execute(
                query_telephone, [
                    data.get('title'),
                    data.get('description'),
                    data.get('diagonal_screen'),
                    data.get('built_in_memory'),
                    data.get('price'),
                    data.get('discount'),
                    data.get('recommended_price'),
                    data.get('weight'),
                    data.get('number_stock'),
                    data.get('brand_id'),
                    data.get('release_date'),
                    data['created_time'],
                    data['update_time'],
                ])
            new_telephone_id = cursor.fetchone()[0]
        return Telephone.get_item(new_telephone_id)

    @classmethod
    def patch_item(cls, telephone_id, data):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data['update_time'] = current_time

        with connection.cursor() as cursor:
            set_clause = ", ".join(f"{field} = %s" for field in data.keys())
            query_telephone = f"""
                      UPDATE base_telephone
                      SET {set_clause}
                      WHERE id = %s;
                  """
            cursor.execute(
                query_telephone, list(data.values()) + [telephone_id]
            )

            return Telephone.get_item(telephone_id)

    @classmethod
    def get_all(cls):
        with connection.cursor() as cursor:
            query = """
            SELECT 
                base_telephone.id AS id, 
                base_telephone.title AS title, 
                base_telephone.price AS price, 
                base_brand.title AS brand,
                COALESCE(json_agg(base_telephoneimage.image), '[]'::json) AS images
            FROM 
                base_telephone
            JOIN 
                base_brand ON base_telephone.brand_id = base_brand.id
            LEFT JOIN 
                base_telephoneimage ON base_telephone.id = base_telephoneimage.telephone_id
            GROUP BY 
                 base_telephone.id, 
                 base_telephone.title,
                 base_telephone.price, 
                 base_brand.title
            ORDER BY 
                base_telephone.title;
            """
            cursor.execute(query)
            result = dictfetchall(cursor)
        return result

    @classmethod
    def get_item(cls, telephone_id):
        with connection.cursor() as cursor:
            query = """SELECT 
                base_telephone.id AS id, 
                base_telephone.title AS title, 
                base_telephone.price AS price, 
                base_brand.title AS brand,
                base_telephone.description AS description, 
                base_telephone.diagonal_screen AS diagonal_screen,
                base_telephone.built_in_memory AS built_in_memory,
                base_telephone.weight AS weight,
                base_telephone.number_stock AS number_stock,
                base_telephone.discount AS discount, 
                base_telephone.release_date AS release_date,
                COALESCE(json_agg(base_telephoneimage.image), '[]'::json) AS images
                FROM base_telephone JOIN base_brand 
                    ON base_telephone.brand_id = base_brand.id
                LEFT JOIN base_telephoneimage 
                    ON base_telephone.id = base_telephoneimage.telephone_id
                WHERE base_telephone.id = %s
                GROUP BY 
                    base_telephone.id, 
                    base_brand.title
                ORDER BY 
                    base_telephone.title;
                """
            cursor.execute(query, [telephone_id])
            result = dictfetchall(cursor)
        return result

    @classmethod
    def delete_item(cls, telephone_id):
        with connection.cursor() as cursor:
            query = """
                    DELETE FROM base_telephone
                    WHERE id = %s;
                """
            cursor.execute(query, [telephone_id])


class TelephoneImage(models.Model):
    title = models.CharField(max_length=100, unique=True)
    image = models.ImageField(upload_to=get_telephone_image_upload_path)
    telephone = models.ForeignKey(Telephone, on_delete=models.CASCADE)
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='created_time')

    @classmethod
    def post(cls, data):
        with connection.cursor() as cursor:
            query_image = """
                INSERT INTO base_telephoneimage (
                    title,
                    image
                )
                VALUES (%s, %s);
                            """
            cursor.execute(
                query_image, [data.get('title'), data.get('image')])
            new_image_id = cursor.lastrowid
        return new_image_id

    @classmethod
    def delete_item(cls, image_id):
        with connection.cursor() as cursor:
            query = """
                        DELETE FROM base_telephoneimage
                        WHERE id = %s;
                    """
            cursor.execute(query, [image_id])


class OrderDetails(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    telephone = models.ForeignKey(Telephone, on_delete=models.CASCADE)
    price = models.IntegerField()
    amount = models.IntegerField()
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='created_time')


class Comment(models.Model):
    telephone = models.ForeignKey(Telephone, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.CharField(max_length=200)
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='created_time')
    update_time = models.DateTimeField(auto_now=True, verbose_name='update_time')


class WishList(models.Model):
    telephone = models.ForeignKey(Telephone, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='created_time')


class Review(models.Model):
    telephone = models.ForeignKey(Telephone, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='created_time')


class Provider(models.Model):
    first_name = models.CharField(max_length=50)
    second_name = models.CharField(max_length=60, null=True, blank=True)
    surname = models.CharField(max_length=100)
    number_telephone = models.CharField(max_length=100)
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='created_time')


class Delivery(models.Model):
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE)
    price = models.ImageField()
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='created_time')
    update_time = models.DateTimeField(auto_now=True, verbose_name='update_time')


class DeliveryDetails(models.Model):
    delivery = models.ForeignKey(Delivery, on_delete=models.CASCADE)
    telephone = models.ForeignKey(Telephone, on_delete=models.CASCADE)
    price_one_phone = models.IntegerField()
    title_telephone = models.CharField(max_length=100)
    amount = models.IntegerField()
