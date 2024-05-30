from .models import Telephone, Brand, UserProfile, TelephoneImage, Order, order_product_details, Address, Vendor, \
    delivery_details, Delivery, Comment
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import serializers
from django.contrib.auth.models import User


class BrandSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=50)

    class Meta:
        model = Brand
        fields = ['title', 'id']


class TelephoneImages(serializers.ModelSerializer):
    class Meta:
        model = TelephoneImage
        fields = '__all__'


class GetAllTelephoneSerializer(serializers.ModelSerializer):
    brand = serializers.StringRelatedField()  # or you can use BrandSerializer here if available
    images = serializers.JSONField()

    class Meta:
        model = Telephone
        fields = ['id', 'title', 'price', 'brand', 'images']


class TelephoneSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=100, required=True)
    description = serializers.CharField(max_length=200)
    diagonal_screen = serializers.FloatField()
    built_in_memory = serializers.CharField(max_length=20)
    price = serializers.IntegerField()
    discount = serializers.IntegerField(max_value=100, min_value=0)
    weight = serializers.FloatField()
    number_stock = serializers.IntegerField()
    release_date = serializers.DateField()
    brand_id = serializers.IntegerField()

    class Meta:
        model = Telephone
        fields = ['title',
                  'description',
                  'diagonal_screen',
                  'built_in_memory',
                  'price',
                  'discount',
                  'weight',
                  'number_stock',
                  'release_date',
                  'brand_id']


class UserRegistrationSerializer(serializers.ModelSerializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    image = serializers.ImageField(required=False)
    number_telephone = serializers.CharField(required=True)
    birth_date = serializers.DateField(required=False)

    class Meta:
        model = UserProfile
        fields = ['username',
                  'email',
                  'password',
                  'first_name',
                  'last_name',
                  'image',
                  'number_telephone',
                  'birth_date',
                  ]


class UserProfileSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(read_only=True, required=False)  # Make the image field optional
    number_telephone = serializers.CharField(max_length=100, required=True)
    birth_date = serializers.DateField(required=False)  # Add this if birth_date is also optional

    class Meta:
        model = UserProfile
        fields = ['image', 'number_telephone', 'birth_date']


class UserSerializer(serializers.ModelSerializer):
    userprofile = UserProfileSerializer()
    username = serializers.CharField(max_length=50)
    last_login = serializers.DateField()
    first_name = serializers.CharField(max_length=50)
    last_name = serializers.CharField(max_length=50)
    email = serializers.CharField(max_length=100)
    is_staff = serializers.BooleanField()
    is_superuser = serializers.BooleanField()
    is_active = serializers.BooleanField()

    class Meta:
        model = User
        fields = [
            'last_login',
            'username',
            'first_name',
            'last_name',
            'email',
            'is_staff',
            'is_superuser',
            'is_active',
            'userprofile'
        ]


class AddressSerializer(serializers.ModelSerializer):
    street_name = serializers.CharField(max_length=50)
    city_id = serializers.IntegerField()
    post_code = serializers.CharField(max_length=10)

    class Meta:
        model = Address
        fields = ['street_name', 'city_id', 'post_code']


class OrderProductsSerializer(serializers.ModelSerializer):
    telephone_id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = order_product_details
        fields = ['telephone_id', 'amount']


class OrderSerializerAuthUser(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=50)
    second_name = serializers.CharField(max_length=50)
    surname = serializers.CharField(max_length=50)
    address = AddressSerializer()
    products = OrderProductsSerializer(many=True)  # Include products here

    class Meta:
        model = Order
        fields = ['address', 'products', 'first_name', 'second_name', 'surname']


class OrderSerializerNoAuthUser(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    first_name = serializers.CharField(max_length=50)
    second_name = serializers.CharField(max_length=50)
    surname = serializers.CharField(max_length=50)
    email = serializers.EmailField()
    number_telephone = serializers.CharField()
    address = AddressSerializer()
    products = OrderProductsSerializer(many=True)

    class Meta:
        model = User
        fields = ['id', 'first_name', 'second_name', 'surname', 'email', 'address', 'number_telephone', 'products']


class VendorSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=50, required=True)
    second_name = serializers.CharField(max_length=50, required=True)
    surname = serializers.CharField(max_length=50, required=True)
    number_telephone = serializers.CharField(max_length=12, required=True)

    class Meta:
        model = Vendor
        fields = ['first_name', 'second_name', 'surname', 'number_telephone']


class DeliveryDetailsSerializer(serializers.ModelSerializer):
    price = serializers.IntegerField(required=False)
    amount = serializers.IntegerField(required=False)
    telephone_id = serializers.IntegerField(required=False)

    class Meta:
        model = delivery_details
        fields = ['price', 'amount', 'telephone_id']


class DeliverySerializer(serializers.ModelSerializer):
    vendor_id = serializers.IntegerField(required=True)
    delivery_price = serializers.IntegerField(required=True)
    delivery_details = DeliveryDetailsSerializer(many=True)

    class Meta:
        model = Delivery
        fields = ['vendor_id', 'delivery_details', 'delivery_price']


class CommentSerializer(serializers.ModelSerializer):
    telephone_id = serializers.IntegerField()
    text = serializers.CharField()

    class Meta:
        model = Comment
        fields = ['telephone_id', 'text']


class CommentPatchSerializer(serializers.ModelSerializer):
    text = serializers.CharField()

    class Meta:
        model = Comment
        fields = ['text']
