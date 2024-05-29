from datetime import datetime

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
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
               """, [username, email, password, first_name, last_name, False, True, False])
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

    @classmethod
    def get_item(cls, address_id):
        with connection.cursor() as cursor:
            query_telephone = f"""
                 SELECT
                    base_address.id,
                    base_address.street_name,
                    base_address.post_code,
                    base_address.city_id,
                    base_city.name
                FROM base_address join base_city
                    ON base_address.city_id = base_city.id
                WHERE base_address.id = %s;
             """
            cursor.execute(query_telephone, address_id)
            result = cursor.fetchone()[0]
            if result:
                return result
            return None

    @classmethod
    def patch_item(cls, address_id, data):
        with connection.cursor() as cursor:
            set_clause = ", ".join(f"{field} = %s" for field in data.keys())
            query_telephone = f"""
                     UPDATE base_address
                     SET {set_clause}
                     WHERE id = %s;
                 """
            cursor.execute(
                query_telephone, list(data.values()) + [address_id]
            )

            return Address.get_item(address_id)


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
                      WHERE id = %s
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

    @classmethod
    def edit_amount(cls, telephone_id, amount):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with connection.cursor() as cursor:
            query_telephone = """
                   SELECT base_telephone.number_stock AS amount
                   FROM base_telephone
                   WHERE id = %s
               """
            cursor.execute(query_telephone, [telephone_id])
            data = cursor.fetchone()
            old_amount = data[0]
            if amount < 0 and abs(amount) > old_amount:
                raise ValidationError("There are not enough items in stock to complete the operation",
                                      code='stock_error', params={'telephone_id': telephone_id})
            new_amount = old_amount + amount
            query_telephone = """
                   UPDATE base_telephone
                   SET number_stock = %s, update_time = %s
                   WHERE id = %s
               """
            cursor.execute(query_telephone, [new_amount, current_time, telephone_id])
            return cls.objects.get(id=telephone_id)


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


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
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
    second_name = models.CharField(null=True, blank=True)
    surname = models.CharField(max_length=50)

    @classmethod
    def get_full_data(cls, user_id=None):
        with connection.cursor() as cursor:
            query_user = ""
            if user_id:
                query_user = f'WHERE base_order.user_id = {user_id}'  # Modify query_user if user_id is provided
            query_order = f"""
                SELECT
                    base_order.id AS id,
                    base_order.status AS status,
                    base_order.user_id AS user_id,
                    base_order.surname,
                     base_order.first_name,
                     base_order.second_name,
                    base_address.street_name AS street,
                    base_address.post_code AS post_code,
                    base_city.name AS city,
                    (
                        SELECT SUM(base_order_product_details.amount * base_order_product_details.price)
                        FROM base_order_product_details
                        WHERE base_order_product_details.order_id = base_order.id
                    ) AS full_price
                FROM base_order 
                JOIN base_address ON base_order.address_id = base_address.id
                JOIN base_city ON base_address.city_id = base_city.id
                {query_user};
            """
            cursor.execute(query_order)
            result_orders = dictfetchall(cursor)

            for order in result_orders:
                order_id = order['id']
                query_order_product_details = f"""
                    SELECT
                        base_order_product_details.id,
                        base_order_product_details.price,
                        base_order_product_details.amount,
                        base_order_product_details.order_id,
                        base_order_product_details.created_time,
                        (
                        SELECT image
                        FROM base_telephoneimage
                        WHERE telephone_id =  base_order_product_details.telephone_id
                        ORDER BY base_telephoneimage.created_time
                        LIMIT 1
                        )
                    FROM base_order_product_details
                    WHERE order_id = {order_id}
                """
                cursor.execute(query_order_product_details)
                result_order_product_details = dictfetchall(cursor)

                order['products'] = result_order_product_details

            return result_orders

    @classmethod
    def post(cls, validated_data):
        with transaction.atomic():
            try:
                with connection.cursor() as cursor:
                    address_query = """
                            INSERT INTO base_address (street_name, city_id, post_code)
                            VALUES (%s, %s, %s)
                            RETURNING id;
                        """
                    cursor.execute(address_query, (
                        validated_data['address']['street_name'],
                        validated_data['address']['city_id'],
                        validated_data['address']['post_code']
                    ))
                    address_result = cursor.fetchone()
                    if not address_result:
                        raise Exception("Failed to insert address")
                    address_id = address_result[0]

                    product_prices = {}
                    for product_data in validated_data['products']:
                        try:
                            Telephone.edit_amount(product_data['telephone_id'], -product_data['amount'])
                        except ValidationError as e:
                            return {
                                'error': e.message,
                                'telephone_id': e.params['telephone_id']
                            }

                        product_price_query = """
                            SELECT price FROM base_telephone WHERE id = %s;
                        """
                        cursor.execute(product_price_query, (product_data['telephone_id'],))
                        product_result = cursor.fetchone()
                        if not product_result:
                            raise Exception(f"No product found with ID {product_data['telephone_id']}")
                        product_prices[product_data['telephone_id']] = product_result[0]

                    # Insert the order
                    order_query = """
                            INSERT INTO base_order (
                                user_id, 
                                address_id, 
                                status, 
                                created_time, 
                                update_time, 
                                first_name, 
                                second_name,
                                surname
                            )
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                            RETURNING id;
                        """
                    cursor.execute(order_query, (
                        validated_data['user_id'],
                        address_id,
                        'PREPARATION',
                        timezone.now(),
                        timezone.now(),
                        validated_data['first_name'],
                        validated_data['second_name'],
                        validated_data['surname']
                    ))
                    fetch_result = cursor.fetchone()
                    if not fetch_result:
                        raise Exception("Failed to insert order")
                    order_id = fetch_result[0]

                    for product_data in validated_data['products']:
                        product_query = """
                                INSERT INTO base_order_product_details (
                                    order_id, 
                                    telephone_id, 
                                    price, 
                                    amount, 
                                    created_time
                                )
                                VALUES (%s, %s, %s, %s, %s);
                            """
                        cursor.execute(product_query, (
                            order_id,
                            product_data['telephone_id'],
                            product_prices[product_data['telephone_id']],
                            product_data['amount'],
                            timezone.now()
                        ))

                    return Order.get_item(order_id)
            except Exception as e:
                write_error_to_file('POST_GetPostOrderAPIView', e)
                raise e

    @classmethod
    def get_all(cls, user_id=None):
        with connection.cursor() as cursor:
            query_user = ""
            if user_id:
                query_user = f'WHERE base_order.user_id = {user_id}'
            query = f"""
            SELECT
                base_order.id AS id,
                base_order.status AS status,
                base_order.user_id AS user_id,
                base_order.status AS first_name,
                base_order.status AS last_name,
                base_address.street_name AS street,
                base_address.post_code AS post_code,
                base_city.name AS city,
                (
                    SELECT SUM(base_order_product_details.amount * base_order_product_details.price)
                    FROM base_order_product_details
                    WHERE base_order_product_details.order_id = base_order.id
                ) AS full_price
            FROM base_order JOIN base_address
                ON base_order.address_id = base_address.id
            JOIN base_city
                ON base_address.city_id = base_city.id
                {query_user};
            """
            cursor.execute(query)
            result = dictfetchall(cursor)
            return result

    @classmethod
    def get_item(cls, order_id):
        with connection.cursor() as cursor:
            order_query = """ 
               SELECT
                   base_order.id AS id,
                   base_order.status AS status,
                   base_order.user_id AS user_id,
                   base_order.surname,
                   base_order.first_name,
                   base_order.second_name,
                   base_address.street_name AS street,
                   base_address.post_code AS post_code,
                   (
                    SELECT SUM(base_order_product_details.amount * base_order_product_details.price)
                    FROM base_order_product_details
                    WHERE base_order_product_details.order_id = base_order.id
                    ) AS full_price
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
                **order_data[0],
                "order_product_details": order_details_data
            }

    @classmethod
    def get_list_by_user(cls, user_id):
        with connection.cursor() as cursor:
            query = """ 
                    SELECT
                        base_order.status AS status,
                        base_order.user_id AS user_id,
                        base_order.surname,
                        base_order.first_name,
                        base_order.second_name,
                        base_address.street_name AS street,
                        base_address.post_code AS post_code,
                        (
                        SELECT SUM(base_order_product_details.amount * base_order_product_details.price)
                        FROM base_order_product_details
                        WHERE base_order_product_details.order_id = base_order.id
                        ) AS full_price
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

    @classmethod
    def patch(cls, item_id, data):
        if not isinstance(data, dict):
            raise ValueError("Data must be a dictionary")

        item_fields = {
            'Address': ['city_id', 'street_name', 'post_code'],
            'Order': ['status', 'created_time', 'update_time', 'address_id', 'first_name', 'second_name', 'surname'],
            'OrderProductDetails': ['order_id', 'telephone_id', 'price', 'amount', 'created_time']
        }

        item_type = cls.__name__
        if item_type not in item_fields:
            raise ValueError(f"Invalid item type: {item_type}")

        # Get the current item to check its status
        current_item = cls.get_item(item_id)
        current_status = current_item['status']

        item_data = {key: value for key, value in data.items() if key in item_fields[item_type]}

        if not item_data:
            return cls.get_item(item_id)  # Nothing to update, return the current item

        try:
            with transaction.atomic():
                set_clause = ", ".join(f"{field} = %s" for field in item_data.keys())
                table_name = cls._meta.db_table  # Get the correct table name
                query = f"""
                    UPDATE {table_name}
                    SET {set_clause}
                    WHERE id = %s;
                """
                with connection.cursor() as cursor:
                    cursor.execute(query, list(item_data.values()) + [item_id])

                return cls.get_item(item_id)
        except ProgrammingError as e:
            raise e
        except Exception as e:
            raise e


class order_product_details(models.Model):
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

    @classmethod
    def check_comment_from_user(cls, comment_id, user_id):
        with connection.cursor() as cursor:
            query = """
                SELECT
                   base_comment.id
                FROM base_comment JOIN auth_user
                    ON auth_user.id = base_comment.user_id
                WHERE base_comment.id = %s AND auth_user.id = %s
            """
            cursor.execute(query, [comment_id, user_id])
            result = dictfetchall(cursor)
            print(result)
            if result:
                return True
            return False

    @classmethod
    def get_by_telephone(cls, telephone_id):
        with connection.cursor() as cursor:
            query = """
                    SELECT
                        base_comment.id,
                        base_comment.telephone_id,
                        base_comment.user_id,
                        base_comment.text,
                        base_comment.created_time,
                        base_comment.update_time,
                        auth_user.username
                    FROM base_comment JOIN auth_user
                        ON auth_user.id = base_comment.user_id
                    WHERE base_comment.telephone_id = %s
                """
            cursor.execute(query, [telephone_id])
            result = dictfetchall(cursor)
            return result

    @classmethod
    def post_item(cls, data):
        try:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            data['created_time'] = current_time
            data['update_time'] = current_time

            with connection.cursor() as cursor:
                query_telephone = """
                       INSERT INTO base_comment (
                           text,
                           user_id,
                           telephone_id,
                           update_time,
                           created_time
                       )
                       VALUES (%s, %s, %s, %s, %s)
                   """
                cursor.execute(
                    query_telephone, [
                        data.get('text'),
                        data.get('user_id'),
                        data.get('telephone_id'),
                        data['created_time'],
                        data['update_time'],
                    ])
            return True
        except Exception as e:
            write_error_to_file('POST_Comment_post_item', e)
            raise e

    @classmethod
    def patch_item(cls, comment_id, data):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if isinstance(data, dict):
            data['update_time'] = current_time
            telephone_id = data.get('telephone_id')
            with connection.cursor() as cursor:
                set_clause = ", ".join(f"{field} = %s" for field in data.keys())
                update_query = f"""
                       UPDATE base_comment
                       SET {set_clause}
                       WHERE id = %s;
                   """
                cursor.execute(update_query, list(data.values()) + [comment_id])
            return Comment.get_by_telephone(telephone_id)
        else:
            raise ValueError("Expected `data` to be a dictionary.")
    @classmethod
    def delete_item(cls, comment_id):
        pass


class Vendor(models.Model):
    first_name = models.CharField(max_length=50)
    second_name = models.CharField(max_length=60, null=True, blank=True)
    surname = models.CharField(max_length=100)
    number_telephone = models.CharField(max_length=100)
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='created_time')

    def __str__(self):
        return self.first_name + ' ' + self.second_name + ' ' + self.surname

    @classmethod
    def get_all(cls, sort_by):
        with connection.cursor() as cursor:
            query = """
                SELECT
                    base_vendor.id,
                    base_vendor.first_name,
                    base_vendor.second_name,
                    base_vendor.surname,
                    base_vendor.number_telephone,
                    base_vendor.created_time,
                    COUNT(base_delivery.id) as count_deliveries
                FROM base_vendor LEFT JOIN base_delivery 
                    ON base_vendor.id = base_delivery.vendor_id
                GROUP BY 
                    base_vendor.id,
                    base_vendor.created_time, 
                    base_vendor.number_telephone, 
                    base_vendor.surname, 
                    base_vendor.second_name, 
                    base_vendor.first_name
                ORDER BY {};
            """.format(sort_by)
            cursor.execute(query)
            result = dictfetchall(cursor)
        return result

    @classmethod
    def post(cls, data):
        with connection.cursor() as cursor:
            query_image = """
                INSERT INTO base_vendor (
                    first_name,
                    second_name,
                    surname,
                    number_telephone,
                    created_time
                )
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id;
            """
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute(
                query_image, [
                    data.get('first_name'),
                    data.get('second_name'),
                    data.get('first_name'),
                    data.get('number_telephone'),
                    current_time])
            new_vendor_id = cursor.fetchone()[0]
            print(new_vendor_id)
        return Vendor.get_item(new_vendor_id)

    @classmethod
    def get_item(cls, vendor_id):
        with connection.cursor() as cursor:
            query_vendor = """
                SELECT
                    first_name,
                    second_name,
                    surname,
                    number_telephone,
                    created_time
                FROM base_vendor
                WHERE id = %s;
            """
            cursor.execute(query_vendor, [vendor_id])
            result_vendor = dictfetchall(cursor)

            query_delivery = """
                SELECT
                    *
                FROM base_delivery
                WHERE vendor_id = %s;
            """
            cursor.execute(query_delivery, [vendor_id])
            result_delivery = dictfetchall(cursor)
        if result_vendor:
            return {**result_vendor[0], "delivery": result_delivery}
        return None

    @classmethod
    def patch(cls, vendor_id, data):
        with connection.cursor() as cursor:
            set_clause = ", ".join(f"{field} = %s" for field in data.keys())
            query_telephone = f"""
                UPDATE base_vendor
                SET {set_clause}
                WHERE id = %s
            """
            cursor.execute(
                query_telephone, list(data.values()) + [vendor_id]
            )
            return Vendor.get_item(vendor_id)


class Delivery(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    delivery_price = models.IntegerField()
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='created_time')
    update_time = models.DateTimeField(auto_now=True, verbose_name='update_time')

    def __str__(self):
        return 'id: ' + str(self.pk)

    @classmethod
    def get_full_data(cls, sort_field, vendor_id):
        with connection.cursor() as cursor:
            vendor_condition = "AND base_delivery.vendor_id = %s" if vendor_id else ""

            delivery_query = f"""
                    SELECT 
                        base_delivery.id AS delivery_id,
                        base_delivery.delivery_price AS delivery_price,
                        base_delivery.vendor_id,
                        base_vendor.surname,
                        base_vendor.first_name,
                        base_vendor.second_name,
                        base_delivery.created_time,
                        base_delivery.update_time,
                        (
                            SELECT SUM(base_delivery_details.amount * base_delivery_details.price_one_phone) 
                            FROM base_delivery_details 
                            WHERE base_delivery_details.delivery_id = base_delivery.id
                        ) + base_delivery.delivery_price AS full_price
                    FROM base_delivery JOIN base_vendor 
                        ON base_vendor.id = base_delivery.vendor_id
                    WHERE 1=1 {vendor_condition}
                    ORDER BY {sort_field};
                """
            params = [vendor_id] if vendor_id else []
            cursor.execute(delivery_query, params)
            deliveries = dictfetchall(cursor)

            # Для каждой записи из base_delivery извлекаем детали
            for delivery in deliveries:
                delivery_id = delivery['delivery_id']
                delivery_details_query = """
                        SELECT
                            id,
                            price_one_phone,
                            amount,
                            telephone_id
                        FROM base_delivery_details
                        WHERE delivery_id = %s;
                    """
                cursor.execute(delivery_details_query, [delivery_id])
                new_delivery_details_data = dictfetchall(cursor)

                delivery["delivery_details"] = new_delivery_details_data
            return deliveries

    @classmethod
    def get_item(cls, delivery_id):
        with connection.cursor() as cursor:
            delivery_query = """ 
                SELECT 
                    base_delivery.id AS delivery_id,
                    base_delivery.delivery_price AS delivery_price,
                    base_delivery.vendor_id,
                    base_vendor.surname,
                    base_vendor.first_name,
                    base_vendor.second_name,
                    base_delivery.created_time,
                    base_delivery.update_time,
                    (
                        SELECT SUM(base_delivery_details.amount * base_delivery_details.price_one_phone) 
                        FROM base_delivery_details 
                        WHERE base_delivery_details.delivery_id = base_delivery.id
                    ) + base_delivery.delivery_price AS full_price
                FROM base_delivery JOIN base_vendor 
                    ON base_vendor.id = base_delivery.vendor_id
                WHERE base_delivery.id = %s;
           """
            cursor.execute(delivery_query, [delivery_id])
            delivery_data = dictfetchall(cursor)

            if not delivery_data:
                return None
            delivery_details_query = """
                SELECT *
                FROM base_delivery_details
                WHERE delivery_id = %s;
            """
            cursor.execute(delivery_details_query, [delivery_id])
            delivery_details_data = dictfetchall(cursor)
            return {
                **delivery_data[0],
                "delivery_details": delivery_details_data
            }

    @classmethod
    def get_all(cls, sort_by, vendor_id):
        with connection.cursor() as cursor:
            vendor_condition = "AND base_delivery.vendor_id = %s" if vendor_id is not None else ""
            query = f"""
                SELECT
                    base_delivery.id as delivery_id,
                    base_delivery.delivery_price as delivery_price,
                    base_delivery.vendor_id,
                    base_vendor.surname
                FROM
                    base_vendor, base_delivery
                WHERE base_vendor.id = base_delivery.vendor_id
                {vendor_condition}
                ORDER BY {sort_by};
            """
            params = (vendor_id,) if vendor_id is not None else ()
            cursor.execute(query, params)
            result = dictfetchall(cursor)
        return result

    @classmethod
    def post(cls, data):
        with transaction.atomic():
            try:
                with connection.cursor() as cursor:
                    query_delivery = """
                        INSERT INTO base_delivery (
                            delivery_price,
                            vendor_id,
                            created_time,
                            update_time
                        )
                        VALUES (%s, %s, %s, %s)
                        RETURNING id;
                    """
                    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    cursor.execute(
                        query_delivery, [
                            data.get('delivery_price'),
                            data.get('vendor_id'),
                            current_time,
                            current_time])
                    delivery_id = cursor.fetchone()[0]

                    for delivery_details_data in data['delivery_details']:
                        Telephone.edit_amount(delivery_details_data['telephone_id'], delivery_details_data['amount'])
                        query_details = """
                            INSERT INTO base_delivery_details (
                                price_one_phone,
                                amount,
                                delivery_id,
                                telephone_id
                            )
                            VALUES (%s, %s, %s, %s);
                        """
                        cursor.execute(
                            query_details, [
                                delivery_details_data.get('price'),
                                delivery_details_data.get('amount'),
                                delivery_id,
                                delivery_details_data.get('telephone_id')])
                        result = Delivery.get_item(delivery_id)
                    return result
            except Exception as e:
                write_error_to_file('POST_classmethod_Delivery', e)
                raise e

    @classmethod
    def patch(cls, delivery_id, data):
        with connection.cursor() as cursor:
            data['update_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            set_clause = ", ".join(f"{field} = %s" for field in data.keys())
            query_telephone = f"""
                UPDATE base_delivery
                SET {set_clause}
                WHERE id = 1
                RETURNING *;
            """
            cursor.execute(
                query_telephone, list(data.values()) + [delivery_id]
            )
            fetch_result = cursor.fetchone()
            if not fetch_result:
                raise Exception({'error': 'Failed to patch delivery'})
        delivery = fetch_result

        return delivery

    @classmethod
    def delete_item(cls, delivery_id):
        with transaction.atomic():
            try:
                with connection.cursor() as cursor:
                    delete_delivery_details_query = """
                            DELETE FROM base_delivery_order
                            WHERE delivery_id = %s;
                        """
                    cursor.execute(delete_delivery_details_query, [delivery_id])

                    delete_delivery_query = """
                            DELETE FROM base_delivery
                            WHERE id = %s;
                        """
                    cursor.execute(delete_delivery_query, [delivery_id])
            except Exception as e:
                write_error_to_file('DELETE_classmethod_Delivery', e)
                raise e


class delivery_details(models.Model):
    delivery = models.ForeignKey(Delivery, on_delete=models.CASCADE)
    telephone = models.ForeignKey(Telephone, on_delete=models.CASCADE)
    price_one_phone = models.IntegerField()
    amount = models.IntegerField()

    def __str__(self):
        return 'id: ' + str(self.pk)

    @classmethod
    def patch(cls, delivery_details_id, data):
        with connection.cursor() as cursor:
            instance = delivery_details.get_item(delivery_details_id)
            if 'price' in data:
                data['price_one_phone'] = data.pop('price')
            if data.get('amount'):
                Telephone.edit_amount(instance['telephone_id'], data['amount'] - instance['amount'])
            set_clause = ", ".join(f"{field} = %s" for field in data.keys())
            query_telephone = f"""
                UPDATE base_delivery_details
                SET {set_clause}
                WHERE id = %s;
            """
            cursor.execute(
                query_telephone, list(data.values()) + [delivery_details_id]
            )
            return delivery_details.get_item(delivery_details_id)

    @classmethod
    def get_item(cls, delivery_details_id):
        with connection.cursor() as cursor:
            query = """
                        SELECT id, amount, price_one_phone, delivery_id, telephone_id
                        FROM base_delivery_details
                        WHERE id = %s
                    """
            cursor.execute(query, [delivery_details_id])
            result = dictfetchall(cursor)
            if result:
                return result[0]
            return None


class Views(models.Model):
    telephone = models.ForeignKey(Telephone, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_time = models.DateTimeField()

    @classmethod
    def get_full_data_stat(cls, telephone_id=None, user_id=None, start_date=None, end_date=None):
        queue_conditions = []

        if telephone_id:
            queue_conditions.append(f"base_views.telephone_id = {telephone_id}")
        if user_id:
            queue_conditions.append(f"base_views.user_id = {user_id}")
        if start_date:
            queue_conditions.append(f"base_views.created_time >= '{start_date}'")
        if end_date:
            queue_conditions.append(f"base_views.created_time <= '{end_date}'")

        queue = ""
        if queue_conditions:
            queue = "WHERE " + " AND ".join(queue_conditions)

        query = f"""
                    SELECT
                        base_views.telephone_id,
                        base_views.user_id,
                        base_views.created_time,
                        auth_user.username,
                        base_telephone.title
                    FROM base_views
                    JOIN auth_user ON auth_user.id = base_views.user_id
                    JOIN base_telephone ON base_views.telephone_id = base_telephone.id
                    {queue}
                """

        with connection.cursor() as cursor:
            cursor.execute(query)
            result = dictfetchall(cursor)

        return result

    @classmethod
    def post_item(cls, data):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data['created_time'] = current_time

        with connection.cursor() as cursor:
            query_telephone = """
                       INSERT INTO base_views (
                           telephone_id,
                           user_id,
                           created_time
                       )
                       VALUES (%s, %s, %s)
                   """
            cursor.execute(
                query_telephone, [
                    data.get('telephone_id'),
                    data.get('user_id'),
                    data['created_time']
                ])
