import os
from datetime import datetime

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models, connection, transaction
from django.utils import timezone
from psycopg2 import ProgrammingError
from base.utils import get_user_image_upload_path, get_telephone_image_upload_path, dictfetchall, write_error_to_file


class City(models.Model):
    name = models.CharField(max_length=100)

    @classmethod
    def get_all(cls):
        with connection.cursor() as cursor:
            query = """
                       SELECT id, name
                       FROM base_city
                       """
            cursor.execute(query)
            result = dictfetchall(cursor)
            return result


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=get_user_image_upload_path, null=True, blank=True)
    number_telephone = models.CharField(max_length=100, null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.user.username

    @classmethod
    def post(cls, data):
        username = data['username']
        email = data['email']
        password = make_password(data['password'])
        first_name = data['first_name']
        last_name = data['last_name']
        image = data.get('image')  # Используем get, чтобы избежать KeyError
        number_telephone = data.get('number_telephone')
        birth_date = data.get('birth_date')

        with connection.cursor() as cursor:
            cursor.execute("""
                   INSERT INTO auth_user (
                       username, 
                       email, 
                       password, 
                       first_name, 
                       last_name, 
                       is_staff, 
                       is_active, 
                       is_superuser,
                       date_joined
                   )
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
                   RETURNING id;
               """, [username, email, password, first_name, last_name, False, True, False])  # Добавлено значение False для is_superuser
            user_id = cursor.fetchone()[0]

            cursor.execute("""
                   INSERT INTO base_userprofile (
                       user_id,
                       image, 
                       number_telephone, 
                       birth_date
                   )
                   VALUES (%s, %s, %s, %s)
               """, [user_id, image, number_telephone, birth_date])

        return user_id

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
                base_userprofile.number_telephone AS number_telephone
                FROM auth_user JOIN base_userprofile
                    ON auth_user.id = base_userprofile.user_id
            """
            cursor.execute(query)
            result = dictfetchall(cursor)
            return result

    @classmethod
    def patch(cls, user_id, data):
        user_fields = ['username', 'first_name', 'last_name', 'email', 'password', 'is_staff', 'is_active',
                       'date_joined']
        profile_fields = ['image', 'number_telephone', 'birth_date']

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
            cursor.execute("""
                SELECT
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
                    base_userprofile.number_telephone AS number_telephone
                FROM auth_user
                JOIN base_userprofile ON auth_user.id = base_userprofile.user_id
                WHERE auth_user.id = %s
            """, [user_id])
            user_data = dictfetchall(cursor)
            return user_data[0]


class Address(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    street_name = models.CharField(max_length=100)
    post_code = models.CharField(max_length=10)


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    full_price = models.IntegerField()
    STATUS_CHOICES = [
        ('PENDING', 'PENDING'),
        ('SENDED', 'SENDED'),
        ('DONE', 'DONE'),
        ('CANCELED', 'CANCELED'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='created_time')
    update_time = models.DateTimeField(auto_now=True, verbose_name='update_time')
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)

    @classmethod
    def get_item_by_user(cls, user_id):
        with connection.cursor() as cursor:
            query = """
                    SELECT
                        base_order.id,
                        base_order.status,
                        base_order.created_time,
                        base_order.update_time,
                        base_order.address_id,
                        base_order_product_details.price,
                        base_order_product_details.amount,
                        base_order_product_details.telephone_id
                    FROM base_order
                    LEFT JOIN base_order_product_details ON base_order.id = base_order_product_details.order_id
                    WHERE base_order.user_id = %s
                """
            cursor.execute(query, [user_id])
            data = dictfetchall(cursor)
        return data

    @classmethod
    def post_is_authenticated(cls, validated_data):
        with transaction.atomic():
            try:
                with connection.cursor() as cursor:
                    # Insert the address
                    address_query = """
                        INSERT INTO base_address (street_name, city_id, post_code)
                        VALUES (%s, %s, %s)
                        RETURNING id;
                    """
                    cursor.execute(address_query, (
                        validated_data['address']['street'],
                        validated_data['address']['city'],
                        validated_data['address']['post_code']
                    ))
                    address_result = cursor.fetchone()
                    if not address_result:
                        raise Exception("Failed to insert address")
                    address_id = address_result[0]
                    order_full_price = 0

                    for product_data in validated_data['products']:
                        # Fetch the product price
                        product_price_query = """
                            SELECT price FROM base_telephone WHERE id = %s;
                        """
                        cursor.execute(product_price_query, (product_data['telephone_id'],))
                        product_result = cursor.fetchone()
                        if not product_result:
                            raise Exception(f"No product found with ID {product_data['telephone_id']}")
                        product_price = product_result[0]

                        total_price = product_price * product_data['amount']
                        order_full_price += total_price

                    # Insert the order
                    order_query = """
                        INSERT INTO base_order (user_id, address_id, status, created_time, update_time, full_price, first_name, last_name)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING id;
                    """
                    cursor.execute(order_query, (
                        validated_data['user_id'],
                        address_id,
                        'PREPARATION',
                        timezone.now(),
                        timezone.now(),
                        order_full_price,
                        validated_data['first_name'],
                        validated_data['last_name']
                    ))
                    fetch_result = cursor.fetchone()
                    if not fetch_result:
                        raise Exception("Failed to insert order")
                    order_id = fetch_result[0]

                    for product_data in validated_data['products']:
                        # Fetch the telephone image
                        telephone_image_query = """
                            SELECT image FROM base_telephoneimage WHERE telephone_id = %s LIMIT 1;
                        """
                        cursor.execute(telephone_image_query, (product_data['telephone_id'],))
                        image_result = cursor.fetchone()
                        telephone_image = image_result[0] if image_result else None

                        # Insert the product details
                        product_query = """
                            INSERT INTO base_order_product_details (order_id, telephone_id, price, amount, created_time, telephone_image)
                            VALUES (%s, %s, %s, %s, %s, %s);
                        """
                        cursor.execute(product_query, (
                            order_id,
                            product_data['telephone_id'],
                            product_price,
                            product_data['amount'],
                            timezone.now(),  # Ensure created_time is set correctly
                            telephone_image
                        ))

                    return cls.get_item(order_id)
            except Exception as e:
                write_error_to_file('POST_GetPostOrderAPIView', e)
                raise e

    @classmethod
    def post_is_not_authenticated(cls, validated_data):
       pass

    @classmethod
    def get_all(cls):
        with connection.cursor() as cursor:
            query = """
            SELECT
                base_order.status as status,
                base_order.user_id as user_id,
                base_order.full_price as full_price,
                base_order.status as first_name,
                base_order.status as last_name,
                base_address.street_name as street,
                base_address.post_code as post_code
            FROM base_order JOIN base_address
                ON base_order.address_id = base_address.id
            """
            cursor.execute(query)
            result = dictfetchall(cursor)
            return result

    @classmethod
    def get_item(cls, order_id):
        with connection.cursor() as cursor:
            order_query = """ 
               SELECT
                   base_order.id as id,
                   base_order.status as status,
                   base_order.user_id as user_id,
                   base_order.full_price as full_price,
                   base_order.first_name as first_name,
                   base_order.last_name as last_name,
                   base_address.street_name as street,
                   base_address.post_code as post_code
               FROM base_order
               JOIN base_address ON base_order.address_id = base_address.id
               JOIN auth_user ON base_order.user_id = auth_user.id
               WHERE base_order.id = %s;
           """
            cursor.execute(order_query, [order_id])
            order_data = dictfetchall(cursor)

            if not order_data:
                return None
            order_details_query = """
                SELECT *
                FROM base_order_product_details
                WHERE order_id = %s;
            """
            cursor.execute(order_details_query, [order_id])
            order_details_data = dictfetchall(cursor)
            return {
                "order": order_data,
                "order_product_details": order_details_data
            }


    @classmethod
    def get_list_by_user(cls, user_id):
        with connection.cursor() as cursor:
            query = """ 
                    SELECT
                        base_order.status as status,
                        base_order.user_id as user_id,
                        base_order.full_price as full_price,
                        auth_user.first_name as first_name,
                        auth_user.last_name as last_name,
                        base_address.street_name as street,
                        base_address.post_code as post_code
                    FROM base_order 
                    JOIN base_address ON base_order.address_id = base_address.id
                    JOIN auth_user ON base_order.user_id = auth_user.id
                    WHERE base_order.user_id = %s;
                """
            cursor.execute(query, [user_id])
            data = dictfetchall(cursor)
        if data:
            return data
        return None


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
            if result:
                return result[0]
            return None

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
    def get_list(cls, ids):
        with connection.cursor() as cursor:
            placeholders = ', '.join(['%s'] * len(ids))

            query = f"""SELECT 
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
                FROM base_telephone 
                JOIN base_brand 
                    ON base_telephone.brand_id = base_brand.id
                LEFT JOIN base_telephoneimage 
                    ON base_telephone.id = base_telephoneimage.telephone_id
                WHERE base_telephone.id IN ({placeholders})
                GROUP BY 
                    base_telephone.id, 
                    base_brand.title
                ORDER BY 
                    base_telephone.title;
            """
            cursor.execute(query, ids)
            data = dictfetchall(cursor)
        return data

    @classmethod
    def get_full_data_all(cls, sort_by):
        with connection.cursor() as cursor:
            query = """
                        SELECT 
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
                            {};
                        """.format(sort_by)
            cursor.execute(query)
            result = dictfetchall(cursor)
        return result

    @classmethod
    def get_all(cls, sort_by):
        with connection.cursor() as cursor:
            query = """
                        SELECT 
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
                        GROUP BY 
                            base_telephone.id, 
                            base_telephone.title,
                            base_telephone.price, 
                            base_brand.title
                        ORDER BY 
                            {};
                        """.format(sort_by)
            cursor.execute(query)
            result = dictfetchall(cursor)
        return result

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
            data = dictfetchall(cursor)
        if data:
            return data[0]
        return None

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


class order_product_details(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    telephone = models.ForeignKey(Telephone, on_delete=models.CASCADE)
    price = models.IntegerField()
    amount = models.IntegerField()
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='created_time')
    telephone_image = models.ImageField(null=True, blank=True)


class Comment(models.Model):
    telephone = models.ForeignKey(Telephone, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.CharField(max_length=200)
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='created_time')
    update_time = models.DateTimeField(auto_now=True, verbose_name='update_time')


class Vendor(models.Model):
    first_name = models.CharField(max_length=50)
    second_name = models.CharField(max_length=60, null=True, blank=True)
    surname = models.CharField(max_length=100)
    number_telephone = models.CharField(max_length=100)
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='created_time')


class Delivery(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    price = models.ImageField()
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='created_time')
    update_time = models.DateTimeField(auto_now=True, verbose_name='update_time')


class DeliveryDetails(models.Model):
    delivery = models.ForeignKey(Delivery, on_delete=models.CASCADE)
    telephone = models.ForeignKey(Telephone, on_delete=models.CASCADE)
    price_one_phone = models.IntegerField()
    title_telephone = models.CharField(max_length=100)
    amount = models.IntegerField()
