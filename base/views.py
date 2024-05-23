from django.contrib.auth.models import User
from django.core import serializers
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .permission import IsAdminOrReadOnly, AuthenticatedUser, AllowOnlyAdmin
from .serializer import TelephoneSerializer, BrandSerializer, UserSerializerRegistration, UserSerializer, \
    GetAllTelephoneSerializer, OrderSerializerAuthUser, OrderSerializerNoAuthUser

from base.models import Telephone, Brand, UserProfile, Order, City
from .utils import write_error_to_file


class TelephoneGetPostAPIView(APIView):
    queryset = Telephone.objects.all()
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request, *args, **kwargs):
        try:
            sort_by = request.query_params.get('sort_by', 'title')
            sort_dir = request.query_params.get('sort_dir', 'asc')
            sort_dict = {
                'title': 'base_telephone.title',
                'price': 'base_telephone.price',
            }
            if sort_by not in sort_dict:
                sort_by = 'title'

            sort_field = sort_dict[sort_by]
            if sort_dir == 'desc':
                sort_field += ' DESC'

            result = Telephone.get_all(sort_field)
            serialized_result = GetAllTelephoneSerializer(result, many=True)
            return Response(serialized_result.data, status=status.HTTP_200_OK)
        except Exception as e:
            write_error_to_file('GET_TelephoneGetAPIView', e)
            return Response({'error': e}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
    permission_classes = [IsAdminOrReadOnly]

    def get(self, *args, **kwargs):
        try:
            telephone_id = kwargs.get("id", None)
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


class Registration(APIView):
    permission_classes = [AllowAny]
    queryset = User.objects.all()
    serializer_class = UserSerializerRegistration

    def post(self, request, *args, **kwargs):
        serializer = UserSerializerRegistration(data=request.data)
        try:
            if serializer.is_valid():
                tokens = serializer.save()
                return Response({
                    'refresh': tokens.get('refresh'),
                    'access': tokens.get('access'),
                }, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            write_error_to_file('POST_Registration', e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AuthenticatedUsersAPIView(APIView):
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


class AdminUsersGetAPIView(APIView):
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


class AdminUsersGetItemPatchDeleteAPIView(APIView):
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


class GetPostOrderAPIView(APIView):
    permission_classes = [AllowAny]
    queryset = Order.objects.all()

    def post(self, request, *args, **kwargs):
        try:
            if request.user.is_authenticated:
                serializer = OrderSerializerAuthUser(data=request.data)
                if serializer.is_valid():
                    serializer.validated_data['user_id'] = request.user.id
                    result = Order.post_is_authenticated(serializer.validated_data)
                    return Response(result, status=status.HTTP_201_CREATED)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            serializer = OrderSerializerNoAuthUser(data=request.data)
            if serializer.is_valid():
                result = Order.post_is_not_authenticated(serializer.validated_data)
                return Response(result, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            write_error_to_file('POST_GetPostOrderAPIView', e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request, *args, **kwargs):
        try:
            result_get_all = Order.get_all()
            return Response(result_get_all, status=status.HTTP_200_OK)
        except Exception as e:
            write_error_to_file('GET_BrandAPIView', e)
            return Response({'error': e}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetItemPatchOrderAPIView(APIView):
    permission_classes = [AllowAny]
    queryset = Order.objects.all()

    def get(self, *args, **kwargs):
        try:
            order_id = kwargs.get("id", None)
            result_get_item = Order.get_item(order_id)
            if result_get_item:
                return Response(result_get_item, status=status.HTTP_200_OK)
            return Response({'error': 'Object does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        except TypeError:
            return Response({'error': 'Object does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            write_error_to_file('GET_item_GetPatchOrderAPIView', e)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request, *args, **kwargs):
        pass


class GetListByUserOrderAPIView(APIView):
    permission_classes = [AllowAny]
    queryset = Order.objects.all()

    def get(self, request):
        try:
            user_id = request.query_params.get('user')
            if not user_id:
                return Response({'error': 'No user_id in query_params'}, status=status.HTTP_400_BAD_REQUEST)
            result_get_item = Order.get_list_by_user(user_id)
            if result_get_item:
                return Response(result_get_item, status=status.HTTP_200_OK)
            return Response([], status=status.HTTP_200_OK)
        except Exception as e:
            write_error_to_file('GET_item_TelephoneGetAPIView', e)
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)