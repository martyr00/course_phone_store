from .models import Telephone, Brand, UserProfile, TelephoneImage, Order, order_product_details, Address
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
    title = serializers.CharField(max_length=100)
    description = serializers.CharField(max_length=200)
    diagonal_screen = serializers.FloatField()
    built_in_memory = serializers.CharField(max_length=20)
    price = serializers.IntegerField()
    discount = serializers.IntegerField(max_value=100, min_value=0)
    recommended_price = serializers.IntegerField(allow_null=True)
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
                  'recommended_price',
                  'weight',
                  'number_stock',
                  'release_date',
                  'brand_id']


class UserProfileSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False)
    number_telephone = serializers.CharField(max_length=100)
    address = serializers.CharField(max_length=100, required=False)
    birth_date = serializers.DateField(required=False)

    class Meta:
        model = UserProfile
        fields = ['image', 'number_telephone', 'address', 'birth_date']


class UserSerializerRegistration(serializers.ModelSerializer):
    password = serializers.CharField(max_length=100)
    userprofile = UserProfileSerializer(required=False)
    username = serializers.CharField(max_length=50)
    first_name = serializers.CharField(max_length=50, required=False)
    last_name = serializers.CharField(max_length=50, required=False)
    email = serializers.EmailField()

    class Meta:
        model = User
        fields = ['password', 'username', 'first_name', 'last_name', 'email', 'userprofile']

    def create(self, validated_data):
        user = User(
            username=validated_data['username'],
            email=validated_data['email'],
            password=make_password(validated_data['password'])
        )
        user.save()

        refresh = RefreshToken.for_user(user)
        tokens = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
        return tokens


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
    street = serializers.CharField(max_length=50)
    city = serializers.IntegerField()
    post_code = serializers.CharField(max_length=10)

    class Meta:
        model = Address
        fields = ['street', 'city', 'post_code']


class OrderProductsSerializer(serializers.ModelSerializer):
    amount = serializers.IntegerField()
    telephone = serializers.IntegerField()

    class Meta:
        model = order_product_details
        fields = ['amount', 'telephone']


class OrderSerializerAuthUser(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=50)
    last_name = serializers.CharField(max_length=50)
    address = AddressSerializer()
    products = OrderProductsSerializer(many=True)

    class Meta:
        model = Order
        fields = ['address', 'products', 'first_name', 'last_name']


class OrderSerializerNoAuthUser(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    first_name = serializers.CharField(max_length=50)
    last_name = serializers.CharField(max_length=50)
    email = serializers.EmailField()
    number_telephone = serializers.EmailField()
    address = AddressSerializer()
    products = OrderProductsSerializer(many=True)

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'address', 'number_telephone', 'products']

