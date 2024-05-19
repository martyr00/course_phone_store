from .models import Telephone, Brand, UserProfile
from django.contrib.auth.hashers import make_password
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import serializers
from django.contrib.auth.models import User


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
    brand = serializers.IntegerField(required=False)

    class Meta:
        model = Telephone
        fields = '__all__'


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['image', 'number_telephone', 'address', 'birth_date']


class UserSerializer(serializers.ModelSerializer):
    userprofile = UserProfileSerializer()

    class Meta:
        model = User
        fields = ['last_login', 'is_superuser', 'username', 'first_name', 'last_name', 'email', 'is_staff', 'is_active', 'date_joined', 'userprofile']

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


class BrandSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=50)

    class Meta:
        model = Brand
        fields = '__all__'