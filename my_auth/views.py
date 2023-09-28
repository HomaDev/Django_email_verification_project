from django.shortcuts import render
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from rest_framework import generics, status
from rest_framework.response import Response
import rest_framework_simplejwt
from rest_framework_simplejwt.tokens import RefreshToken, UntypedToken
from rest_framework_simplejwt.state import token_backend

import my_auth
from .models import User
from .serializers import RegisterSerializer
from .utils import Util
from django.conf import settings


class RegisterView(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request):
        user = request.data
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user_data = serializer.data
        user = User.objects.get(email=user_data['email'])
        token = RefreshToken.for_user(user).access_token

        current_site = get_current_site(request).domain
        relativeLink = reverse('email-verify')
        absrul = f'http://{current_site}{relativeLink}?token={token}'
        email_body = f'Hi click link below to verify your email on {current_site}\n{absrul}'
        data = {'email_body': email_body, 'domain': current_site,
                'email_subject': 'Verify your email', 'to_email': user.email}
        Util.send_email(data)

        return Response(user_data, status=status.HTTP_201_CREATED)


class VerifyEmail(generics.GenericAPIView):

    def get(self, request):
        token = request.GET.get('token')
        try:
            UntypedToken(token)
            payload = token_backend.decode(token)
            print(payload)
            user = User.objects.get(id=payload['user_id'])
            print(user)
            if not user.is_verified:
                user.is_verified = True
                user.save()
            return Response({'email': 'Successfully Activated'}, status=status.HTTP_200_OK)
        except rest_framework_simplejwt.exceptions.TokenError:
            return Response({'error': 'Token invalid or expired'}, status=status.HTTP_400_BAD_REQUEST)
        except my_auth.models.User.DoesNotExist as identifier:
            return Response({'error': 'User does not exist'}, status=status.HTTP_400_BAD_REQUEST)

