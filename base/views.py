import uuid
from datetime import datetime

from django.contrib.auth.models import User
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .const import END_DATE_DEFAULT, START_DATE_DEFAULT
from .permission import IsAdminOrReadOnly, AuthenticatedUser, AllowOnlyAdmin, AuthenticatedOrSafeMethodsUser
from .serializer import TelephoneSerializer, BrandSerializer, UserSerializer, \
    GetAllTelephoneSerializer, OrderSerializerAuthUser, OrderSerializerNoAuthUser, OrderProductsSerializer, \
    UserRegistrationSerializer, VendorSerializer, DeliverySerializer, DeliveryDetailsSerializer, CommentSerializer, \
    CommentPatchSerializer, DeliveryPatchSerializer, WishListSerializer

from base.models import Telephone, Brand, UserProfile, Order, City, Vendor, Delivery, delivery_details, Address, \
    Comment, Views, wish_list
from .utils import write_error_to_file


class TelephoneGetPostAPIView(APIView):
    queryset = Telephone.objects.all()
    permission_classes = [AllowAny]
    serializers = TelephoneSerializer

    def get(self, request, *args, **kwargs):
        try:
            sort_by = request.query_params.get('sort_by', 'title')
            sort_dir = request.query_params.get('sort_dir', 'asc')

            diagonal_screen = request.query_params.getlist('diagonal_screen')
            built_in_memory = request.query_params.getlist('built_in_memory')
            brand = request.query_params.getlist('brand')
            price_min = request.query_params.get('price_min')
            price_max = request.query_params.get('price_max')
            weight_min = request.query_params.get('weight_min')
            weight_max = request.query_params.get('weight_max')

            sort_dict = {
                'title': 'base_telephone.title',
                'price': 'base_telephone.price',
            }
            if sort_by not in sort_dict:
                sort_by = 'title'

            sort_field = sort_dict[sort_by]
            if sort_dir == 'desc':
                sort_field += ' DESC'

            if request.user.is_staff:
                query_params_full_date = request.query_params.get('fulldata', None)
                if query_params_full_date:
                    result = Telephone.get_all(
                        sort_field,
                        True,
                        diagonal_screen,
                        built_in_memory,
                        brand,
                        price_min,
                        price_max,
                        weight_min,
                        weight_max
                    )
                    return Response(result, status=status.HTTP_200_OK)
            result = Telephone.get_all(
                sort_field,
                False,
                diagonal_screen,
                built_in_memory,
                brand,
                price_min,
                price_max,
                weight_min,
                weight_max
            )
            serialized_result = GetAllTelephoneSerializer(result, many=True)
            return Response(serialized_result.data, status=status.HTTP_200_OK)
        except Exception as e:
            write_error_to_file('GET_TelephoneGetAPIView', e)
            return Response({'error': e}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(request_body=TelephoneSerializer)
    def post(self, request, *args, **kwargs):
        try:
            serializer = TelephoneSerializer(data=request.data)
            if serializer.is_valid():
                return Response(Telephone.post_item(serializer.validated_data), status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            write_error_to_file('POST_TELEPHONE', e)
            return Response({'error': e}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TelephoneGetItemPatchDeleteAPIView(APIView):
    queryset = Telephone.objects.all()
    serializer = TelephoneSerializer
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        try:
            telephone_id = kwargs.get("id", None)
            if request.user.is_authenticated:
                data = {'telephone_id': telephone_id, 'user_id': request.user.id}
                Views.post_item(data)
            result_get_item = Telephone.get_item(telephone_id)
            if result_get_item:
                return Response(result_get_item, status=status.HTTP_200_OK)
            return Response({'error': 'Object does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        except TypeError:
            return Response({'error': 'Object does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            write_error_to_file('GET_item_TelephoneGetAPIView', e)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, *args, **kwargs):
        try:
            telephone_id = kwargs.get("id", None)
            return Response(Telephone.delete_item(telephone_id), status=status.HTTP_204_NO_CONTENT)
        except TypeError:
            return Response({'error': 'Object does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            write_error_to_file('DELETE_TELEPHONE', e)
            return Response({'error': e}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request, *args, **kwargs):
        try:
            telephone_id = kwargs.get("id", None)
            telephone = Telephone.objects.get(pk=telephone_id)

            serializer = TelephoneSerializer(instance=telephone, data=request.data, partial=True)
            if serializer.is_valid():
                validated_data = serializer.validated_data
                return Response(Telephone.patch_item(telephone_id, validated_data), status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Telephone.DoesNotExist:
            return Response({"error": "Telephone not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            write_error_to_file('PATCH_TELEPHONE', e)
            return Response({'error': e}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TelephoneGetListAPIView(APIView):
    queryset = Telephone.objects.all()
    serializer = TelephoneSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request):
        try:
            telephone_ids_string = request.query_params.getlist('id')
            result_get_item = Telephone.get_list(telephone_ids_string)
            if result_get_item:
                return Response(result_get_item, status=status.HTTP_200_OK)
            return Response({[]}, status=status.HTTP_200_OK)
        except TypeError:
            return Response({'error': 'Object does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            write_error_to_file('GET_item_TelephoneGetAPIView', e)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FiltersForTelephoneGetAPIView(APIView):
    queryset = Telephone.objects.all()
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            result = Telephone.get_filters()
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            write_error_to_file('GET_FiltersForTelephoneGetAPIView', e)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BrandGetPostAPIView(APIView):
    queryset = Brand.objects.all()
    serializer = BrandSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request, *args, **kwargs):
        try:
            result_get_all = Brand.get_all()
            return Response(result_get_all, status=status.HTTP_200_OK)
        except Exception as e:
            write_error_to_file('GET_BrandAPIView', e)
            return Response({'error': e}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, *args, **kwargs):
        try:
            serializer = BrandSerializer(data=request.data)
            if serializer.is_valid():
                result = Brand.post_item(serializer.validated_data)
                return Response(result, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            write_error_to_file('POST_BrandAPIView', e)
            return Response({'error': e}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BrandGetItemPatchDeleteAPIView(APIView):
    queryset = Brand.objects.all()
    serializer = BrandSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request, *args, **kwargs):
        try:
            brand_id = kwargs.get("id", None)
            if brand_id is None:
                return Response({'error': 'ID is required'}, status=status.HTTP_400_BAD_REQUEST)

            result_get_all = Brand.get_item(brand_id)
            if result_get_all:
                return Response(result_get_all, status=status.HTTP_200_OK)

            return Response({'error': 'Object does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            write_error_to_file('GET_BrandAPIView', e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, *args, **kwargs):
        try:
            brand_id = kwargs.get("id", None)
            result = Brand.delete_item(brand_id)
            return Response(result, status=status.HTTP_204_NO_CONTENT)
        except TypeError:
            return Response({'error': 'Object does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            write_error_to_file('DELETE_BrandAPIView', e)
            return Response({'error': e}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request, *args, **kwargs):
        try:
            brand_id = kwargs.get("id", None)
            brand = Brand.objects.get(pk=brand_id)

            serializer = BrandSerializer(instance=brand, data=request.data, partial=True)
            if serializer.is_valid():
                validated_data = serializer.validated_data
                result = Brand.patch_item(brand_id, validated_data)
                return Response(result, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Brand.DoesNotExist:
            return Response({"error": "Brand not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            write_error_to_file('PATCH_BrandAPIView', e)
            return Response({'error': e}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserPostRegistration(APIView):
    permission_classes = [AllowAny]
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer

    def post(self, request, *args, **kwargs):
        serializer = UserRegistrationSerializer(data=request.data)
        try:
            if serializer.is_valid():
                user_id = UserProfile.post(serializer.validated_data)
                user = User.objects.get(id=user_id)

                refresh = RefreshToken.for_user(user)
                tokens = {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
                return Response(tokens, status=status.HTTP_201_CREATED)
            print("Errors: ", serializer.errors)  # Debugging line
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            write_error_to_file('POST_Registration', e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UsersAuthenticatedGetPatchAPIView(APIView):
    permission_classes = [AuthenticatedUser]
    queryset = UserProfile.objects.all()
    serializer_class = UserSerializer

    def get(self, request, *args, **kwargs):
        try:
            user_id = request.user.id
            if user_id:
                result_get_item = UserProfile.get_item(user_id)
                if result_get_item:
                    return Response(result_get_item, status=status.HTTP_200_OK)
                return Response({'error': 'Object does not exist'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(
                    {
                        'error': 'Authentication credentials were not provided'
                    },
                    status=status.HTTP_401_UNAUTHORIZED
                )
        except Exception as e:
            write_error_to_file('GET_AuthenticatedUsersAPIView', e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request, *args, **kwargs):
        try:
            user_id = request.user.id
            user = User.objects.get(pk=user_id)

            serializer = UserSerializer(instance=user, data=request.data, partial=True)
            if serializer.is_valid():
                validated_data = serializer.validated_data
                result = UserProfile.patch(user_id, validated_data)
                return Response(result, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except User.DoesNotExist:
            return Response(
                {'error': 'Authentication credentials were not provided'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        except TypeError as e:
            write_error_to_file('PATCH_AuthenticatedUsersAPIView_TypeError', e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            write_error_to_file('PATCH_AuthenticatedUsersAPIView', e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OrderGetSelfAPIView(APIView):
    permission_classes = [AuthenticatedUser]
    queryset = UserProfile.objects.all()
    serializer_class = OrderProductsSerializer

    def get(self, request, *args, **kwargs):
        try:
            user_id = request.user.id
            if user_id:
                result_get_item = Order.get_list_by_user(user_id)
                return Response(result_get_item, status=status.HTTP_200_OK)
            else:
                return Response(
                    {
                        'error': 'Authentication credentials were not provided'
                    },
                    status=status.HTTP_401_UNAUTHORIZED
                )
        except Exception as e:
            write_error_to_file('GET_AuthenticatedUsersAPIView', e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UsersAdminGetAPIView(APIView):
    permission_classes = [AllowOnlyAdmin]
    queryset = UserProfile.objects.all()
    serializer_class = UserSerializer

    def get(self, request, *args, **kwargs):
        try:
            data = UserProfile.get_all()
            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            write_error_to_file('GET_AdminUsersAPIView', str(e))
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UsersAdminGetItemPatchDeleteAPIView(APIView):
    permission_classes = [AllowOnlyAdmin]
    queryset = UserProfile.objects.all()
    serializer_class = UserSerializer

    def get(self, *args, **kwargs):
        try:
            user_id = kwargs.get("id", None)
            result_get_item = UserProfile.get_item(user_id)
            if result_get_item:
                return Response(result_get_item, status=status.HTTP_200_OK)
            return Response({'error': 'Object does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        except TypeError:
            return Response({'error': 'Object does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            write_error_to_file('GET_item_AdminUsersAPIView', e)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request, *args, **kwargs):
        user_id = kwargs.get("id", None)
        if not user_id:
            return Response({'error': 'BadRequest'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            data = request.data
            UserProfile.patch(user_id, data)

            user_profile = UserProfile.get_item(user_id)
            if not user_profile:
                return Response({'error': 'UserProfile not found'}, status=status.HTTP_404_NOT_FOUND)

            return Response(user_profile, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            write_error_to_file('PATCH_User', e)
            return Response({'error': e}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, *args, **kwargs):
        try:
            user_id = kwargs.get("id", None)
            return Response(UserProfile.delete(user_id), status=status.HTTP_204_NO_CONTENT)
        except TypeError:
            return Response({'error': 'Object does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            write_error_to_file('DELETE_TELEPHONE', e)
            return Response({'error': e}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CityAPIView(APIView):
    permission_classes = [AllowAny]
    queryset = City.objects.all()

    def get(self, request, *args, **kwargs):
        try:
            result_get_all = City.get_all()
            return Response(result_get_all, status=status.HTTP_200_OK)
        except Exception as e:
            write_error_to_file('GET_CityAPIView', e)
            return Response({'error': 'An unexpected error occurred.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OrderGetAPIView(APIView):
    permission_classes = [AllowOnlyAdmin]
    queryset = Order.objects.all()
    serializers = OrderSerializerAuthUser

    def get(self, request, *args, **kwargs):
        try:
            user_id = request.query_params.get('user_id', None)
            full_data = request.query_params.get('fulldata', None)
            order_status = request.query_params.get('status', None)
            start_date = request.query_params.get('start_date', START_DATE_DEFAULT)
            end_date = request.query_params.get('end_date', END_DATE_DEFAULT)
            if full_data:
                result = Order.get_full_data(start_date, end_date, order_status, user_id)
                return Response(result, status=status.HTTP_200_OK)
            result = Order.get_all(start_date, end_date, user_id)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            write_error_to_file('GET_BrandAPIView', e)
            return Response({'error': e}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OrderPostAPIView(APIView):
    permission_classes = [AllowAny]
    queryset = Order.objects.all()

    def post(self, request, *args, **kwargs):
        try:
            if request.user.is_authenticated:
                serializer = OrderSerializerAuthUser(data=request.data)
                if serializer.is_valid():
                    serializer.validated_data['user_id'] = request.user.id
                    result = Order.post(serializer.validated_data)
                    if isinstance(result, dict) and 'error' in result:
                        return Response(result, status=status.HTTP_400_BAD_REQUEST)
                    return Response(result, status=status.HTTP_201_CREATED)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            serializer = OrderSerializerNoAuthUser(data=request.data)
            if serializer.is_valid():
                data = serializer.validated_data
                data['username'] = str(uuid.uuid4())
                data['password'] = str(uuid.uuid4())
                user_id = UserProfile.post(data)
                data['user_id'] = user_id
                result = Order.post(serializer.validated_data)
                if isinstance(result, dict) and 'error' in result:
                    return Response(result, status=status.HTTP_400_BAD_REQUEST)
                return Response(result, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            write_error_to_file('POST_GetPostOrderAPIView', e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OrderGetItemPatchAPIView(APIView):
    permission_classes = [AuthenticatedUser]
    queryset = Order.objects.all()

    def get(self, request, *args, **kwargs):
        try:
            order_id = kwargs.get("id", None)
            result_get_item = Order.get_item(order_id)
            if result_get_item:
                if request.user.is_staff:
                    return Response(result_get_item, status=status.HTTP_200_OK)
                user_id = request.user.id
                if result_get_item.get('user_id') == user_id:
                    return Response(result_get_item, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
            return Response({'error': 'Object does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        except TypeError:
            return Response({'error': 'Object does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            write_error_to_file('GET_item_GetPatchOrderAPIView', e)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request, *args, **kwargs):
        try:
            order_id = kwargs.get("id", None)
            user_id = request.user.id
            order = Order.get_item(order_id)
            current_status = order['status']

            if order['user_id'] == user_id or request.user.is_staff:
                if current_status not in ['PENDING', 'PREPARATION'] and not request.user.is_staff:
                    return Response({
                        'error': 'Only admin can update order when status is not PENDING'
                    }, status=status.HTTP_403_FORBIDDEN)

                data = request.data
                if data.get('status') == 'CANCELED':
                    for product in order['order_product_details']:
                        Telephone.edit_amount(product['telephone_id'], product['amount'])

                result = Order.patch(order_id, request.data)
                return Response(result, status=status.HTTP_200_OK)
            return Response({'error': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            error_message = str(e)
            write_error_to_file('PATCH_OrderGetItemPatchAPIView', error_message)
            return Response({'error': error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OrderGetListByUserAPIView(APIView):
    permission_classes = [AllowAny]
    queryset = Order.objects.all()

    def get(self, request, *args, **kwargs):
        try:
            user_id = request.query_params.get('user_id')
            if not user_id:
                return Response({'error': 'No user_id in query_params'}, status=status.HTTP_400_BAD_REQUEST)
            result_get_item = Order.get_list_by_user(user_id)
            if result_get_item:
                return Response(result_get_item, status=status.HTTP_200_OK)
            return Response([], status=status.HTTP_200_OK)
        except Exception as e:
            write_error_to_file('GET_item_TelephoneGetAPIView', e)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VendorGetPostAPIView(APIView):
    permission_classes = [AllowOnlyAdmin]
    queryset = Vendor.objects.all()

    def get(self, request, *args, **kwargs):
        try:
            sort_by = request.query_params.get('sort_by', 'surname')
            sort_dir = request.query_params.get('sort_dir', 'asc')
            sort_dict = {
                'surname': 'base_vendor.surname',
                'count_deliveries': 'count_deliveries',
            }
            if sort_by not in sort_dict:
                sort_by = 'title'

            sort_field = sort_dict[sort_by]
            if sort_dir == 'desc':
                sort_field += ' DESC'
            result = Vendor.get_all(sort_field)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            write_error_to_file('GET_VendorGetPostAPIView', e)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, *args, **kwargs):
        try:
            serializer = VendorSerializer(data=request.data)
            if serializer.is_valid():
                result = Vendor.post(serializer.validated_data)
                return Response(result, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            write_error_to_file('POST_VendorGetPostAPIView', e)
            return Response({'error': e}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VendorGetPatchDeleteItemAPIView(APIView):
    permission_classes = [AllowOnlyAdmin]
    queryset = Vendor.objects.all()

    def patch(self, request, *args, **kwargs):
        try:
            vendor_id = kwargs.get("id", None)
            serializer = VendorSerializer(data=request.data)
            if serializer.is_valid():
                Vendor.patch(vendor_id, serializer.validated_data)
                return Response('Successful', status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            error_message = str(e)  # Extract error message
            write_error_to_file('PATCH_VendorGetPatchDeleteItemAPIView', error_message)
            return Response({'error': error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request, *args, **kwargs):
        try:
            vendor_id = kwargs.get("id", None)
            if vendor_id is None:
                return Response({'error': 'ID is required'}, status=status.HTTP_400_BAD_REQUEST)

            result = Vendor.get_item(vendor_id)
            if result:
                return Response(result, status=status.HTTP_200_OK)
            return Response({'error': 'Object does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            write_error_to_file('GET_VendorGetPatchDeleteItemAPIView', e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, *args, **kwargs):
        pass


class DeliveryGetPostAPIView(APIView):
    permission_classes = [AllowOnlyAdmin]
    queryset = Delivery.objects.all()

    def get(self, request, *args, **kwargs):
        try:
            sort_by = request.query_params.get('sort_by', 'time')
            sort_dir = request.query_params.get('sort_dir', 'asc')
            sort_dict = {
                'delivery_price': 'base_delivery.delivery_price',
                'time': 'base_delivery.created_time',
                'full_name': 'full_name',
            }
            if sort_by not in sort_dict:
                sort_by = 'surname'

            sort_field = sort_dict[sort_by]
            if sort_dir == 'desc':
                sort_field += ' DESC'
            vendor_id = request.query_params.get('vendor', None)
            result = Delivery.get_all(sort_field, vendor_id)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            write_error_to_file('GET_DeliveryGetPostAPIView', e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, *args, **kwargs):
        try:
            serializer = DeliverySerializer(data=request.data)
            if serializer.is_valid():
                result = Delivery.post(serializer.validated_data)
                return Response(result, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            write_error_to_file('POST_DeliveryGetPostAPIView', e)
            return Response({'error': e}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DeliveryGetPatchDeleteItemAPIView(APIView):
    permission_classes = [AllowOnlyAdmin]
    queryset = Delivery.objects.all()

    def get(self, request, *args, **kwargs):
        try:
            delivery_id = kwargs.get("id", None)
            if delivery_id is None:
                return Response({'error': 'ID is required'}, status=status.HTTP_400_BAD_REQUEST)

            result = Delivery.get_item(delivery_id)
            if result:
                return Response(result, status=status.HTTP_200_OK)
            return Response({'error': 'Object does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            write_error_to_file('GET_DeliveryGetPatchDeleteItemAPIView', e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request, *args, **kwargs):
        try:
            delivery_id = kwargs.get("id", None)
            serializer = DeliveryPatchSerializer(data=request.data)
            if serializer.is_valid():
                Delivery.patch(delivery_id, serializer.validated_data)
                return Response('Successful', status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            error_message = str(e)
            write_error_to_file('PATCH_VendorGetPatchDeleteItemAPIView', error_message)
            return Response({'error': error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DeliveryDetailsPatch(APIView):
    permission_classes = [AllowOnlyAdmin]
    queryset = delivery_details.objects.all()

    def patch(self, request, *args, **kwargs):
        try:
            delivery_details_id = kwargs.get("id", None)
            serializer = DeliveryDetailsSerializer(data=request.data)
            if serializer.is_valid():
                result = delivery_details.patch(delivery_details_id, serializer.validated_data)
                return Response('Successful', status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            error_message = str(e)  # Extract error message
            write_error_to_file('PATCH_VendorGetPatchDeleteItemAPIView', error_message)
            return Response({'error': error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CommentGetPostAPIView(APIView):
    permission_classes = [AuthenticatedOrSafeMethodsUser]
    queryset = Comment.objects.all()

    def get(self, request, *args, **kwargs):
        try:
            telephone_id = request.query_params.get('telephone_id')
            if telephone_id:
                result = Comment.get_by_telephone(telephone_id)
                return Response(result, status=status.HTTP_200_OK)
            return Response({'error': 'Bad request'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            write_error_to_file('GET_CommentGetPostAPIView', e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, *args, **kwargs):
        try:
            serializer = CommentSerializer(data=request.data)
            if serializer.is_valid():
                data = serializer.validated_data
                data['user_id'] = request.user.id
                print(data)
                Comment.post_item(data)
                return Response({"result": 'Success'}, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            write_error_to_file('POST_CommentGetPostAPIView', e)
            error_message = str(e)
            return Response({'error': error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CommentPatchAPIView(APIView):
    permission_classes = [AuthenticatedUser]
    queryset = Comment.objects.all()

    def patch(self, request, *args, **kwargs):
        try:
            comment_id = kwargs.get('id')

            serializer = CommentPatchSerializer(data=request.data)
            if serializer.is_valid():
                data = serializer.validated_data

                user_id = request.user.id
                if Comment.check_comment_from_user(comment_id, user_id) or request.user.is_staff:
                    Comment.patch_item(comment_id, data)
                    return Response({"result": 'Success'}, status=status.HTTP_200_OK)
                return Response({"error": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            write_error_to_file('POST_CommentGetPostAPIView', e)
            error_message = str(e)
            return Response({'error': error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ViewsGetFullDataAPIView(APIView):
    permission_classes = [AllowOnlyAdmin]
    queryset = Views.objects.all()

    def get(self, request, *args, **kwargs):
        try:
            start_date = request.query_params.get('start_date', START_DATE_DEFAULT)
            end_date = request.query_params.get('end_date', END_DATE_DEFAULT)
            result = Views.get_full_data_stat(start_date, end_date)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            write_error_to_file('GET_ViewsGetFullDataAPIView', e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OrderGetStatAVGCostAPIView(APIView):
    permission_classes = [AllowOnlyAdmin]
    queryset = Order.objects.all()

    def get(self, request, *args, **kwargs):
        try:
            start_date = request.query_params.get('start_date', START_DATE_DEFAULT)
            end_date = request.query_params.get('end_date', END_DATE_DEFAULT)
            return Response(Order.get_avg_order_cost(start_date, end_date), status=status.HTTP_200_OK)
        except Exception as e:
            write_error_to_file('GET_OrderGetStatAVGCostAPIView', e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OrderGetStatAmountProductAPIView(APIView):
    permission_classes = [AllowOnlyAdmin]
    queryset = Order.objects.all()

    def get(self, request, *args, **kwargs):
        try:
            start_date = request.query_params.get('start_date', START_DATE_DEFAULT)
            end_date = request.query_params.get('end_date', END_DATE_DEFAULT)
            return Response(Order.get_order_amount_product(start_date, end_date), status=status.HTTP_200_OK)
        except Exception as e:
            write_error_to_file('GET_OrderGetStatAVGCostAPIView', e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OrderGetStatAmountOrderAPIView(APIView):
    permission_classes = [AllowOnlyAdmin]
    queryset = Order.objects.all()

    def get(self, request, *args, **kwargs):
        try:
            start_date = request.query_params.get('start_date', START_DATE_DEFAULT)
            end_date = request.query_params.get('end_date', END_DATE_DEFAULT)
            return Response(Order.get_order_amount(start_date, end_date), status=status.HTTP_200_OK)
        except Exception as e:
            write_error_to_file('GET_OrderGetStatAVGCostAPIView', e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class OrderGetTotalSumAPIView(APIView):
    permission_classes = [AllowOnlyAdmin]
    queryset = Order.objects.all()

    def get(self, request, *args, **kwargs):
        try:
            start_date = request.query_params.get('start_date', START_DATE_DEFAULT)
            end_date = request.query_params.get('end_date', END_DATE_DEFAULT)
            return Response(Order.get_total_order_cost(start_date, end_date), status=status.HTTP_200_OK)
        except Exception as e:
            write_error_to_file('GET_OrderGetStatAVGCostAPIView', e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProductGetPercentSellsAPIView(APIView):
    permission_classes = [AllowOnlyAdmin]
    queryset = Telephone.objects.all()

    def get(self, request, *args, **kwargs):
        try:
            start_date = request.query_params.get('start_date', START_DATE_DEFAULT)
            end_date = request.query_params.get('end_date', END_DATE_DEFAULT)
            return Response(Telephone.get_percent_sells(start_date, end_date), status=status.HTTP_200_OK)
        except Exception as e:
            write_error_to_file('GET_OrderGetStatAVGCostAPIView', e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class WishListAPIView(APIView):
    permission_classes = [AuthenticatedUser]
    queryset = wish_list.objects.all()

    def get(self, request, *args, **kwargs):
        try:
            user_id = request.user.id
            result_get_items_by_user_id = wish_list.get_by_user_id(user_id)
            return Response(result_get_items_by_user_id, status=status.HTTP_200_OK)
        except TypeError:
            return Response({'error': 'Object does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            write_error_to_file('GET_item_WishListAPIView', e)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, *args, **kwargs):
        try:
            data = {'telephone_id': kwargs.get("id"), 'user_id': request.user.id}
            serializer = WishListSerializer(data=data)
            if serializer.is_valid():
                return Response(wish_list.post_by_user(serializer.validated_data), status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            write_error_to_file('POST_WISH_LIST', e)
            return Response({'error': e}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, *args, **kwargs):
        try:
            data = {'telephone_id': kwargs.get("id"), 'user_id': request.user.id}
            serializer = WishListSerializer(data=data)
            if serializer.is_valid():
                return Response(wish_list.delete_obj(serializer.validated_data), status=status.HTTP_204_NO_CONTENT)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            write_error_to_file('DELETE_WISH_LIST', e)
            return Response({'error': e}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PhonesAddedWishListAPIView(APIView):
    permission_classes = [AuthenticatedUser]
    queryset = wish_list.objects.all()

    def get(self, request, *args, **kwargs):
        pass


class BestSellingTelephoneAPIView(APIView):
    permission_classes = [AllowOnlyAdmin]

    def get(self, request, *args, **kwargs):
        try:
            return Response(Telephone.get_best_selling_telephone(), status=status.HTTP_200_OK)
        except Exception as e:
            write_error_to_file('GET_MoreThanWishListAPIView', e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MoreThanWishListAPIView(APIView):
    permission_classes = [AllowOnlyAdmin]

    def get(self, request, *args, **kwargs):
        try:
            return Response(Telephone.get_more_than_in_wish_list(), status=status.HTTP_200_OK)
        except Exception as e:
            write_error_to_file('GET_MoreThanWishListAPIView', e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class VendorsByTelephonesBrandAPIView(APIView):
    queryset = Vendor.objects.all()
    permission_classes = [AllowOnlyAdmin]

    def get(self, request, *args, **kwargs):
        try:
            brand_title = request.GET.get('brand')
            if not brand_title:
                return Response({'error': 'Brand parameter is missing'}, status=status.HTTP_400_BAD_REQUEST)

            data = {'title': request.GET.get('brand')}
            serializer = BrandSerializer(data=data)
            if serializer.is_valid():
                return Response(Vendor.get_vendors_by_telephones_brand(serializer.validated_data['title']), status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            write_error_to_file('GET_VendorsByTelephonesBrandAPIView', e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UsersByQuantityAndTotalCostOrderAPIView(APIView):
    permission_classes = [AllowOnlyAdmin]

    def get(self, request, *args, **kwargs):
        try:
            return Response(UserProfile.get_users_order_by_quantity_orders_and_total_cost(), status=status.HTTP_200_OK)
        except Exception as e:
            write_error_to_file('GET_UsersByQuantityAndTotalCostOrderAPIView', e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UsersPlacedOrderOnDateAPIView(APIView):
    permission_classes = [AllowOnlyAdmin]

    def get(self, request, *args, **kwargs):
        try:
            date = request.GET.get('date')
            if not date:
                return Response({'error': 'Date parameter is missing'}, status=status.HTTP_400_BAD_REQUEST)

            return Response(UserProfile.get_users_placed_order_on_date(date), status=status.HTTP_200_OK)
        except Exception as e:
            write_error_to_file('GET_UsersByQuantityAndTotalCostOrderAPIView', e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
