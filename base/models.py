from datetime import datetime

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models, connection, transaction
from django.utils import timezone
from psycopg2 import ProgrammingError

from base.utils import get_user_image_upload_path, get_telephone_image_upload_path, dictfetchall, write_error_to_file, \
    get_dates_with_null_values


class City(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

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
    second_name = models.CharField(null=True, blank=True)

    def __str__(self):
        return self.user.username

    @classmethod
    def post(cls, data):
        username = data['username']
        email = data['email']
        password = make_password(data['password'])
        first_name = data['first_name']
        second_name = data['second_name']
        surname = data['surname']
        image = data.get('image')
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
               """, [username, email, password, first_name, surname, False, True, False])
            user_id = cursor.fetchone()[0]

            cursor.execute("""
                   INSERT INTO base_userprofile (
                       user_id,
                       image, 
                       number_telephone, 
                       birth_date,
                       second_name
                   )
                   VALUES (%s, %s, %s, %s, %s)
               """, [user_id, image, number_telephone, birth_date, second_name])

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
                auth_user.last_name AS surname,
                base_userprofile.second_name AS second_name,
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
        if data.get('surname'):
            data['last_name'] = data.pop('surname')
        user_fields = ['username', 'first_name', 'last_name', 'email', 'password', 'is_active',
                       'date_joined']
        profile_fields = ['image', 'number_telephone', 'birth_date', 'second_name']

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
                    auth_user.last_name AS surname,
                    base_userprofile.second_name AS second_name,
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

    @classmethod
    def get_users_placed_order_on_date(cls, date):
        with connection.cursor() as cursor:
            query = """
                SELECT DISTINCT
                    u.username,
                    u.first_name,
                    u.last_name
                FROM auth_user u
                JOIN base_order o ON u.Id = o.user_id
                WHERE
                    Date(o.created_time) = %s
            """
            cursor.execute(query, [date])
            result = dictfetchall(cursor)
            return result

    @classmethod
    def get_users_order_by_quantity_orders_and_total_cost(cls):
        with connection.cursor() as cursor:
            query = """
                SELECT
                    u.id,
                    u.first_name,
                    up.second_name,
                    u.last_name,
                    count(o.id) as quantity_orders,
                    SUM(opd.amount * t.price) as total_cost
                FROM base_userprofile as up, auth_user as u
                Join base_order o ON u.id = o.user_id
                JOIN base_order_product_details opd ON o.id = opd.order_id
                JOIN base_telephone t ON opd.telephone_id = t.id
                GROUP BY u.id, u.username, u.first_name, up.second_name, u.last_name, u.email
                ORDER BY quantity_orders DESC, total_cost DESC
            """
            cursor.execute(query)
            result = dictfetchall(cursor)
            return result


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
    weight = models.FloatField()
    number_stock = models.IntegerField()
    release_date = models.DateField()
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='created_time')
    update_time = models.DateTimeField(auto_now=True, verbose_name='update_time')

    def __str__(self):
        return self.title

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
    def get_all(cls, sort_by, full_data, diagonal_screen=None, built_in_memory=None, brand=None, price_min=None, price_max=None,
                weight_min=None, weight_max=None):
        with connection.cursor() as cursor:
            print(full_data)
            if full_data:
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
                    FROM base_telephone 
                    JOIN base_brand ON base_telephone.brand_id = base_brand.id
                    LEFT JOIN base_telephoneimage ON base_telephone.id = base_telephoneimage.telephone_id
                    WHERE 1=1
                """
            else:
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
                    WHERE 1=1
                """

            conditions = []

            if diagonal_screen:
                conditions.append(f"base_telephone.diagonal_screen IN ({', '.join(map(str, diagonal_screen))})")

            if built_in_memory:
                conditions.append(f"base_telephone.built_in_memory IN ({', '.join(map(str, built_in_memory))})")

            if brand:
                brand_list = "', '".join(brand)
                conditions.append(f"base_brand.title IN ('{brand_list}')")

            if price_min is not None:
                conditions.append(f"base_telephone.price >= {price_min}")

            if price_max is not None:
                conditions.append(f"base_telephone.price <= {price_max}")

            if weight_min is not None:
                conditions.append(f"base_telephone.weight >= {weight_min}")

            if weight_max is not None:
                conditions.append(f"base_telephone.weight <= {weight_max}")

            if conditions:
                query += " AND " + " AND ".join(conditions)

            query += f" GROUP BY base_telephone.id, base_telephone.title, base_telephone.price, base_brand.title ORDER BY {sort_by};"
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
                    weight,
                    number_stock,
                    brand_id,
                    release_date,
                    created_time,
                    update_time
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
                base_brand.id AS brand_id,
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
                    base_brand.title,
                    base_brand.id;
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

    @classmethod
    def get_filters(cls):
        with connection.cursor() as cursor:
            cursor.execute("""
                    SELECT MIN(price) AS min_price, MAX(price) AS max_price
                    FROM base_telephone
                """)
            row = cursor.fetchone()
            price_range = {'min_price': row[0], 'max_price': row[1]}

            cursor.execute("""
                    SELECT DISTINCT diagonal_screen
                    FROM base_telephone
                    ORDER BY diagonal_screen
                """)
            diagonal_screen_values = [row[0] for row in cursor.fetchall()]

            cursor.execute("""
                    SELECT DISTINCT built_in_memory
                    FROM base_telephone
                    ORDER BY built_in_memory
                """)
            built_in_memory_values = [row[0] for row in cursor.fetchall()]

            cursor.execute("""
                    SELECT DISTINCT base_brand.title
                    FROM base_telephone
                    JOIN base_brand ON base_telephone.brand_id = base_brand.id
                    ORDER BY base_brand.title
                """)
            brand_values = [row[0] for row in cursor.fetchall()]

            cursor.execute("""
                            SELECT MIN(weight) AS min_weight, MAX(weight) AS max_weight
                            FROM base_telephone
                        """)
            row = cursor.fetchone()
            weight_range = {'min': row[0], 'max': row[1]}

        items = [
            {
                "title": "diagonal_screen",
                "options": diagonal_screen_values
            },
            {
                "title": "built_in_memory",
                "options": built_in_memory_values
            },
            {
                "title": "brand",
                "options": brand_values
            }
        ]

        return {
            "price_range": price_range,
            "weight": weight_range,
            "items": items,
        }

    @classmethod
    def get_percent_sells(cls, start_date, end_date):
        with connection.cursor() as cursor:
            query = """
           SELECT
                base_telephone.title AS telephone_title,
                COALESCE(telephone_sells.total_sold, NULL) AS total_sold
            FROM
                base_telephone
            LEFT JOIN (
                SELECT
                    base_order_product_details.telephone_id,
                    COALESCE(SUM(base_order_product_details.amount), 0) AS total_sold
                FROM
                    base_order_product_details
                JOIN
                    base_order ON base_order_product_details.order_id = base_order.id
                WHERE
                    base_order.status = 'DONE' AND DATE(base_order.created_time) BETWEEN %s AND %s
                GROUP BY
                    base_order_product_details.telephone_id
            ) telephone_sells ON base_telephone.id = telephone_sells.telephone_id
            GROUP BY
                base_telephone.title, telephone_sells.total_sold;
        """

            cursor.execute(query, [start_date, end_date])
            result = dictfetchall(cursor)
            return result

    @classmethod
    def get_more_than_in_wish_list(cls):
        with connection.cursor() as cursor:
            query = """
                SELECT
                    t.title,
                    COUNT(w.telephone_id) as quantity_added
                FROM
                    base_wish_list as w
                JOIN base_telephone t ON w.telephone_id = t.id
                GROUP BY
                    t.title
                HAVING
                    count(w.telephone_id) >= 1;
            """
            cursor.execute(query)
            result = dictfetchall(cursor)
            return result

    @classmethod
    def get_best_selling_telephone(cls):
        with connection.cursor() as cursor:
            query = """
                SELECT
                    base_telephone.title AS title,
                    SUM(opd.amount) AS total_sells
                FROM base_telephone JOIN base_brand
                    ON base_telephone.brand_id = base_brand.id
                JOIN base_order_product_details opd ON opd.telephone_id = base_telephone.id
                GROUP BY
                    base_telephone.id,
                    base_brand.title,
                    base_brand.id
                ORDER BY
                    total_sells DESC
                LIMIT 1;
            """
            cursor.execute(query)
            result = dictfetchall(cursor)
            return result


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

    def __str__(self):
        return self.status

    @classmethod
    def get_full_data(cls, start_date, end_date, order_status=None, user_id=None, ):
        with connection.cursor() as cursor:
            query_conditions = []
            query_params = []

            if order_status is not None:
                query_conditions.append("base_order.status = %s")
                query_params.append(order_status.upper())
            if user_id is not None:
                query_conditions.append("base_order.user_id = %s")
                query_params.append(user_id)

            query_condition = ""
            if query_conditions:
                query_condition = "AND ".join(query_conditions)

            query_date = f"AND base_order.update_time BETWEEN '{start_date}' AND '{end_date}'"

            query_order = f"""
                SELECT
                    base_order.id AS id,
                    base_order.status AS status,
                    base_order.user_id AS user_id,
                    base_order.surname,
                    DATE(base_order.created_time),
                    DATE(base_order.update_time),
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
                WHERE 1=1
                {query_condition}
                {query_date}
            """
            cursor.execute(query_order, query_params)
            result_orders = dictfetchall(cursor)

            for order in result_orders:
                order_id = order['id']
                query_order_product_details = """
                    SELECT
                        base_order_product_details.id,
                        base_order_product_details.telephone_id,
                        base_order_product_details.price,
                        base_order_product_details.amount,
                        base_order_product_details.order_id,
                        base_order_product_details.created_time,
                        (
                        SELECT image
                        FROM base_telephoneimage
                        WHERE telephone_id = base_order_product_details.telephone_id
                        ORDER BY base_telephoneimage.created_time
                        LIMIT 1
                        )
                    FROM base_order_product_details
                    WHERE order_id = %s
                """
                cursor.execute(query_order_product_details, [order_id])
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
                        Telephone.edit_amount(product_data['telephone_id'], -product_data['amount'])
                        print(-product_data['amount'])
                        product_price_query = """
                            SELECT price, discount FROM base_telephone WHERE id = %s;
                        """
                        cursor.execute(product_price_query, (product_data['telephone_id'],))
                        product_result = cursor.fetchone()
                        if not product_result:
                            raise Exception(f"No product found with ID {product_data['telephone_id']}")

                        product_price = product_result[0]
                        discount_percentage = product_result[1]

                        if discount_percentage is not None and discount_percentage > 0:
                            discount_amount = product_price * (discount_percentage / 100)
                            product_price -= discount_amount

                        product_prices[product_data['telephone_id']] = product_price

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
                        'PENDING',
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
    def get_all(cls, start_date, end_date, user_id=None):
        with connection.cursor() as cursor:
            query = f"""
            SELECT
                base_order.id AS id,
                base_order.status AS status,
                base_order.user_id AS user_id,
                base_order.first_name AS first_name,
                base_order.second_name AS second_name,
                base_order.surname AS surname,
                DATE(base_order.update_time) AS update_time,
                DATE(base_order.created_time) AS created_time,
                base_address.street_name AS street,
                base_address.post_code AS post_code,
                base_city.name AS city,
                (
                    SELECT SUM(base_order_product_details.amount * base_order_product_details.price)
                    FROM base_order_product_details
                    WHERE base_order_product_details.order_id = base_order.id
                ) AS full_price
            FROM base_order
            JOIN base_address
                ON base_order.address_id = base_address.id
            JOIN base_city
                ON base_address.city_id = base_city.id
            ORDER BY base_order.update_time DESC
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
                    WHERE base_order.user_id = %s;
                """
            cursor.execute(query, [user_id])
            data = dictfetchall(cursor)
        if data:
            return data
        return None

    @classmethod
    def patch(cls, item_id, data):

        item_fields = {
            'Address': ['city_id', 'street_name', 'post_code'],
            'Order': ['status', 'created_time', 'update_time', 'address_id', 'first_name', 'second_name', 'surname'],
            'OrderProductDetails': ['order_id', 'telephone_id', 'price', 'amount', 'created_time']
        }

        item_type = cls.__name__
        if item_type not in item_fields:
            raise ValueError(f"Invalid item type: {item_type}")

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

    @classmethod
    def get_avg_order_cost(cls, start_date=None, end_date=None):
        with connection.cursor() as cursor:
            query = """
                SELECT
                    DATE(base_order.created_time) AS date,
                    AVG(
                        (
                            SELECT SUM(base_order_product_details.amount * base_order_product_details.price)
                            FROM base_order_product_details
                            WHERE base_order_product_details.order_id = base_order.id
                        )
                    ) AS value
                FROM
                    base_order
                JOIN
                    base_address ON base_order.address_id = base_address.id
                JOIN
                    base_city ON base_address.city_id = base_city.id
                WHERE
                    DATE(base_order.created_time) BETWEEN %s AND %s
                GROUP BY
                    DATE(base_order.created_time)
                """
            cursor.execute(query, [start_date, end_date])
            result = dictfetchall(cursor)
            return get_dates_with_null_values(result, start_date, end_date)

    @classmethod
    def get_order_amount_product(cls, start_date=None, end_date=None):
        with connection.cursor() as cursor:
            query = """
                SELECT
                    DATE(base_order.created_time) AS DATE,
                    SUM(base_order_product_details.amount) AS VALUE
                FROM
                    base_order
                JOIN
                    base_order_product_details ON base_order.id = base_order_product_details.order_id
                WHERE
                    DATE(base_order.created_time) BETWEEN %s AND %s
                GROUP BY
                    DATE(base_order.created_time)
                ORDER BY
                    DATE DESC
                """
            cursor.execute(query, [start_date, end_date])
            result = dictfetchall(cursor)

            return get_dates_with_null_values(result, start_date, end_date)

    @classmethod
    def get_order_amount(cls, start_date=None, end_date=None):
        with connection.cursor() as cursor:
            query = """
                SELECT
                    DATE(created_time) AS date,
                    COUNT(id) AS value
                FROM
                    base_order
                WHERE
                    DATE(base_order.created_time) BETWEEN %s AND %s
                GROUP BY
                    DATE(base_order.created_time)
                ORDER BY
                    date DESC
                """
            cursor.execute(query, [start_date, end_date])
            result = dictfetchall(cursor)
            return get_dates_with_null_values(result, start_date, end_date)

    @classmethod
    def get_total_order_cost(cls, start_date=None, end_date=None):
        with connection.cursor() as cursor:
            query = """
                SELECT
                    DATE(base_order.created_time) AS date,
                    SUM(
                        (
                            SELECT SUM(base_order_product_details.amount * base_order_product_details.price)
                            FROM base_order_product_details
                            WHERE base_order_product_details.order_id = base_order.id
                        )
                    ) AS value
                FROM
                    base_order
                JOIN
                    base_address ON base_order.address_id = base_address.id
                JOIN
                    base_city ON base_address.city_id = base_city.id
                WHERE
                    DATE(base_order.created_time) BETWEEN %s AND %s
                GROUP BY
                    DATE(base_order.created_time)
                 ORDER BY
                    date DESC;
                """
            cursor.execute(query, [start_date, end_date])
            result = dictfetchall(cursor)
            return get_dates_with_null_values(result, start_date, end_date)


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
                    id,
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

        if result_vendor:
            return result_vendor[0]
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

    @classmethod
    def get_vendors_by_telephones_brand(cls, brand_title='Apple'):
        with connection.cursor() as cursor:
            query = """
                SELECT DISTINCT
                    v.id,
                    v.first_name,
                    v.second_name,
                    v.surname,
                    v.number_telephone
                FROM
                    base_vendor as v
                JOIN base_delivery as d ON v.id = d.vendor_id
                JOIN base_delivery_details as bd ON d.id = bd.delivery_id
                JOIN base_telephone as t ON bd.telephone_id = t.id
                JOIN base_brand as b ON t.brand_id = b.id
                WHERE b.title = %s
            """
            cursor.execute(query, [brand_title])
            result = dictfetchall(cursor)
            return result


class Delivery(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='created_time')
    update_time = models.DateTimeField(auto_now=True, verbose_name='update_time')

    def __str__(self):
        return 'id: ' + str(self.pk)

    @classmethod
    def get_item(cls, delivery_id):
        with connection.cursor() as cursor:
            delivery_query = """ 
                SELECT 
                    base_delivery.id AS delivery_id,
                    base_delivery.vendor_id
                FROM base_delivery JOIN base_vendor 
                    ON base_vendor.id = base_delivery.vendor_id
                WHERE base_delivery.id = %s;
           """
            cursor.execute(delivery_query, [delivery_id])
            delivery_data = dictfetchall(cursor)

            if not delivery_data:
                return None
            delivery_details_query = """
                SELECT
                    price_one_phone,
                    amount,
                    telephone_id
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
                    base_delivery.vendor_id,
                    CONCAT(base_vendor.surname, ' ', base_vendor.first_name, ' ', base_vendor.second_name) as full_name
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
                            vendor_id,
                            created_time,
                            update_time
                        )
                        VALUES (%s, %s, %s)
                        RETURNING id;
                    """
                    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    cursor.execute(
                        query_delivery, [
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
                                delivery_details_data.get('price_one_phone'),
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
                WHERE id = %s
                RETURNING *;
            """
            cursor.execute(
                query_telephone, list(data.values()) + [delivery_id]
            )
            fetch_result = cursor.fetchone()
            if not fetch_result:
                raise Exception({'error': 'Failed to patch delivery'})

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
    def get_full_data_stat(cls, start_date=None, end_date=None):
        query = f"""
                SELECT
                    DATE(base_views.created_time) AS date,
                    COUNT(base_views.telephone_id) AS value
                FROM base_views
                WHERE
                    DATE(base_views.created_time) BETWEEN '2024-05-28' AND '2024-06-04'
                GROUP BY
                    DATE(base_views.created_time)
                ORDER BY
                    DATE(base_views.created_time) DESC
            """

        with connection.cursor() as cursor:
            cursor.execute(query, [start_date, end_date])
            result = dictfetchall(cursor)

        return get_dates_with_null_values(result, start_date, end_date)

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


class wish_list(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    telephone = models.ForeignKey(Telephone, on_delete=models.CASCADE)
    created_time = models.DateTimeField()

    @classmethod
    def get_by_user_id(cls, user_id):
        with connection.cursor() as cursor:
            query = """
                    SELECT *
                    FROM base_wish_list
                    WHERE user_id = %s
                """
            cursor.execute(query, [user_id])
            result = dictfetchall(cursor)
            if result:
                return result
            return None

    @classmethod
    def post_by_user(cls, data):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data['created_time'] = current_time
        with connection.cursor() as cursor:
            query_telephone = """
                               INSERT INTO base_wish_list (
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

    @classmethod
    def delete_obj(cls, data):
        with connection.cursor() as cursor:
            query_telephone = """
               DELETE FROM base_wish_list
                    WHERE user_id = %s AND telephone_id = %s;
           """
            cursor.execute(
                query_telephone, [data['user_id'], data['telephone_id']])
