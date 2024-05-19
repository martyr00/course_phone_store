from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .permission import IsAdminOrReadOnly, AuthenticatedUser, AllowOnlyAdmin
from .serializer import TelephoneSerializer, UserSerializer, BrandSerializer

from base.models import Telephone, Brand, UserProfile
from .utils import write_error_to_file


class TelephoneGetAPIView(APIView):
    queryset = Telephone.objects.all()
    serializer = TelephoneSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request, *args, **kwargs):
        try:
            telephone_id = kwargs.get("telephone_id", None)
            if telephone_id is not None:
                try:
                    result_get_item = Telephone.get_item(telephone_id)
                    if result_get_item:
                        return Response(result_get_item, status=status.HTTP_200_OK)
                    return Response({'error': 'Object does not exist'}, status=status.HTTP_404_NOT_FOUND)
                except Exception as e:
                    write_error_to_file('GET_item_TelephoneAPIView', e)
                    return Response({'error': 'Failed to retrieve phone information'},
                                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                telephones = Telephone.get_all()
                return Response(telephones, status=status.HTTP_200_OK)
        except Exception as e:
            write_error_to_file('GET_TelephoneAPIView', e)
            return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TelephonePatchPostDeleteAPIView(APIView):
    queryset = Telephone.objects.all()
    serializer = TelephoneSerializer
    permission_classes = [IsAdminOrReadOnly]

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

    def delete(self, request, *args, **kwargs):
        try:
            telephone_id = kwargs.get("telephone_id", None)
            return Response(Telephone.delete_item(telephone_id), status=status.HTTP_204_NO_CONTENT)
        except TypeError:
            return Response({'error': 'Object does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            write_error_to_file('DELETE_TELEPHONE', e)
            return Response({'error': e}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request, *args, **kwargs):
        try:
            telephone_id = kwargs.get("telephone_id", None)
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


class BrandGetAPIView(APIView):
    queryset = Brand.objects.all()
    serializer = BrandSerializer
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request, *args, **kwargs):
        try:
            brand_id = kwargs.get("brand_id", None)
            if brand_id:
                try:
                    result_get_item = Brand.get_item(brand_id)
                    if result_get_item:
                        return Response(result_get_item, status=status.HTTP_200_OK)
                    return Response({'error': 'Object does not exist'}, status=status.HTTP_400_BAD_REQUEST)
                except TypeError:
                    return Response({'error': 'Object does not exist'}, status=status.HTTP_400_BAD_REQUEST)
                except Exception as e:
                    write_error_to_file('GET_item_BrandAPIView', e)
                    return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            result_get_all = Brand.get_all()
            return Response(result_get_all, status=status.HTTP_200_OK)
        except Exception as e:
            write_error_to_file('GET_BrandAPIView', e)
            return Response({'error': e}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BrandPostPatchDeleteAPIView(APIView):
    queryset = Brand.objects.all()
    serializer = BrandSerializer
    permission_classes = [IsAdminOrReadOnly]

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

    def delete(self, request, *args, **kwargs):
        try:
            brand_id = kwargs.get("brand_id", None)
            result = Brand.delete_item(brand_id)
            return Response(result, status=status.HTTP_204_NO_CONTENT)
        except TypeError:
            return Response({'error': 'Object does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            write_error_to_file('DELETE_BrandAPIView', e)
            return Response({'error': e},status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request, *args, **kwargs):
        try:
            brand_id = kwargs.get("brand_id", None)
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
            return Response({'error': e},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class Registration(APIView):
    permission_classes = [AllowAny]
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        try:
            if serializer.is_valid():
                tokens = serializer.save()
                return Response({
                    'tokens': tokens
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

    def delete(self):
        pass


class AdminUsersGetAPIView(APIView):
    permission_classes = [AllowOnlyAdmin]
    queryset = UserProfile.objects.all()
    serializer_class = UserSerializer

    def get(self, request, *args, **kwargs):
        try:
            user_id = kwargs.get("user_id", None)
            if user_id:
                try:
                    result_get_item = UserProfile.get_item_admin(user_id)
                    if result_get_item:
                        return Response(result_get_item, status=status.HTTP_200_OK)
                    return Response({'error': 'Object does not exist'}, status=status.HTTP_400_BAD_REQUEST)
                except TypeError:
                    return Response({'error': 'Object does not exist'}, status=status.HTTP_400_BAD_REQUEST)
                except Exception as e:
                    write_error_to_file('GET_item_AdminUsersAPIView', e)
                    return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response(UserProfile.get_all(), status=status.HTTP_200_OK)

        except Exception as e:
            write_error_to_file('GET_AdminUsersAPIView', e)
            return Response({'error': e}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AdminUsersPatchDeleteAPIView(APIView):
    permission_classes = [AllowOnlyAdmin]
    queryset = UserProfile.objects.all()
    serializer_class = UserSerializer

    def patch(self, request, *args, **kwargs):
        user_id = kwargs.get("user_id", None)
        if not user_id:
            return Response({'error': 'BadRequest'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(id=user_id)

            data = request.data
            UserProfile.patch(user_id, data)

            user_profile = UserProfile.get_item(user_id)
            if not user_profile:
                return Response({'error': 'UserProfile not found'}, status=status.HTTP_404_NOT_FOUND)

            user_serializer = UserSerializer(user)
            return Response(user_serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            write_error_to_file('PATCH_User', e)
            return Response({'error': e}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self):
        # TODO
        pass
