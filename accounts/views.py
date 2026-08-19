from rest_framework import generics, permissions, status, views
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from orders.models import Order
from django.db.models import Sum
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from .models import UserProfile, Address, Wishlist
from .serializers import (
    RegisterSerializer, UserSerializer, OrderSummarySerializer, OrderDetailSerializer,
    AddressSerializer, WishlistSerializer, CustomTokenObtainPairSerializer
)
from .utils import send_activation_email
from rest_framework_simplejwt.views import TokenObtainPairView
import secrets
import string


# ============================================================
# AUTENTICAÇÃO
# ============================================================
class RegisterView(generics.CreateAPIView):
    """
    Registo normal com password fornecida pelo utilizador.
    """
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        send_activation_email(user, request)
        return Response({
            'message': 'Registo efetuado. Verifique o seu email para ativar a conta.',
            'email': user.email,
        }, status=status.HTTP_201_CREATED)


""" 
class CreateUserWithRandomPasswordView(APIView):
 
    #Cria um utilizador com password aleatória (para o fluxo de checkout).
    #A password é gerada automaticamente e enviada por email.
    
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        full_name = request.data.get('full_name')

        if not email or not full_name:
            return Response(
                {'error': 'Email e nome completo são obrigatórios.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verificar se o email já está registado
        if User.objects.filter(email=email).exists():
            return Response(
                {'error': 'Já existe uma conta com este email.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Gerar username a partir do email
        username = email.split('@')[0] + secrets.token_hex(4)

        # Gerar password aleatória de 10 caracteres (maiúsculas, minúsculas, números)
        alphabet = string.ascii_letters + string.digits
        password = ''.join(secrets.choice(alphabet) for _ in range(10))

        # Criar utilizador (inativo até ativação)
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=full_name.split(' ')[0],
            last_name=' '.join(full_name.split(' ')[1:]) if len(full_name.split(' ')) > 1 else '',
            is_active=False
        )

        # Enviar email com a password e link de ativação
        self._send_welcome_email(user, password, request)

        return Response({
            'message': 'Conta criada com sucesso. Verifique o seu email para ativar a conta.',
            'email': user.email,
        }, status=status.HTTP_201_CREATED)

    def _send_welcome_email(self, user, password, request):
        profile = user.profile
        token = profile.activation_token
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
        activation_link = f"{frontend_url}/ativar-conta?token={token}"

        subject = "Bem-vindo à Glow Seven – Ative a sua conta"
        context = {
            'user': user,
            'password': password,
            'activation_link': activation_link,
        }
        html_message = render_to_string('accounts/emails/welcome_with_password.html', context)
        plain_message = strip_tags(html_message)

        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        ) 
"""

class CreateUserWithRandomPasswordView(APIView):

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        full_name = request.data.get('full_name')
        order_id = request.data.get('order_id')

        if not email or not full_name or not order_id:
            return Response(
                {'error': 'Email, nome completo e ID da encomenda são obrigatórios.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Buscar a encomenda
        try:
            order = Order.objects.get(order_ref=order_id)
        except Order.DoesNotExist:
            return Response(
                {'error': 'Encomenda não encontrada.'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Validar que o email coincide com o da encomenda
        if order.email != email:
            return Response(
                {'error': 'O email não corresponde ao da encomenda.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verificar se o email já está registado
        if User.objects.filter(email=email).exists():
            return Response(
                {'error': 'Já existe uma conta com este email.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Gerar username e password
        username = email.split('@')[0] + secrets.token_hex(4)
        alphabet = string.ascii_letters + string.digits
        password = ''.join(secrets.choice(alphabet) for _ in range(10))

        # Criar utilizador (inativo até ativação)
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=full_name.split(' ')[0],
            last_name=' '.join(full_name.split(' ')[1:]) if len(full_name.split(' ')) > 1 else '',
            is_active=False
        )

        # Criar endereço a partir dos dados da encomenda
        Address.objects.create(
            user_profile=user.profile,
            name='Casa',
            street=order.street,
            number=order.number,
            floor=order.floor or '',
            postal_code=order.postal_code,
            city=order.city,
            country=order.country,
            is_default=True
        )

        # Associar a encomenda ao utilizador
        order.user = user
        order.save()

        # Enviar email com password e link de ativação (função inalterada)
        self._send_welcome_email(user, password, request)

        return Response({
            'message': 'Conta criada com sucesso. Verifique o seu email para ativar a conta.',
            'email': user.email,
        }, status=status.HTTP_201_CREATED)

    def _send_welcome_email(self, user, password, request):
        # Mantida exatamente como original
        profile = user.profile
        token = profile.activation_token
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
        activation_link = f"{frontend_url}/activate-account?token={token}"

        subject = "Bem-vindo à Glow Seven – Ative a sua conta"
        context = {
            'user': user,
            'password': password,
            'activation_link': activation_link,
        }
        html_message = render_to_string('accounts/emails/welcome_with_password.html', context)
        plain_message = strip_tags(html_message)

        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )



class UserDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class ActivateAccountView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        token = request.data.get('token')
        if not token:
            return Response({'error': 'Token não fornecido.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            profile = UserProfile.objects.get(activation_token=token)
            user = profile.user
            if user.is_active:
                return Response({'message': 'Conta já está ativa.'}, status=status.HTTP_200_OK)
            user.is_active = True
            user.save()
            profile.activation_token = None
            profile.save()
            return Response({'message': 'Conta ativada com sucesso.'}, status=status.HTTP_200_OK)
        except UserProfile.DoesNotExist:
            return Response({'error': 'Token inválido ou expirado.'}, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


# ============================================================
# DASHBOARD – ESTATÍSTICAS
# ============================================================
class DashboardStatsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        orders = Order.objects.filter(user=user)

        total_orders = orders.count()
        total_spent = orders.filter(status='paid').aggregate(total=Sum('total'))['total'] or 0
        pending_orders = orders.filter(status='pending').count()
        recent_orders = orders.order_by('-created_at')[:5]

        return Response({
            'total_orders': total_orders,
            'total_spent': total_spent,
            'pending_orders': pending_orders,
            'recent_orders': [
                {
                    'id': o.id,
                    'order_ref': o.order_ref,
                    'total': o.total,
                    'status': o.status,
                    'created_at': o.created_at,
                    'items_count': o.items.count(),
                } for o in recent_orders
            ],
        })


# ============================================================
# ENCOMENDAS
# ============================================================
class UserOrderListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrderSummarySerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')


class UserOrderDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = OrderDetailSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


# ============================================================
# MORADAS
# ============================================================
class AddressListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AddressSerializer

    def get_queryset(self):
        return Address.objects.filter(user_profile__user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user_profile=self.request.user.profile)


class AddressRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AddressSerializer

    def get_queryset(self):
        return Address.objects.filter(user_profile__user=self.request.user)


class AddressSetDefaultView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            address = Address.objects.get(pk=pk, user_profile__user=request.user)
        except Address.DoesNotExist:
            return Response({'error': 'Morada não encontrada.'}, status=status.HTTP_404_NOT_FOUND)

        address.is_default = True
        address.save()
        return Response({'status': 'Morada definida como padrão.'})


# ============================================================
# FAVORITOS (WISHLIST)
# ============================================================
class WishlistListView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        wishlist = Wishlist.objects.filter(user_profile__user=request.user)
        serializer = WishlistSerializer(wishlist, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        # Espera receber product_id
        product_id = request.data.get('product_id')
        if not product_id:
            return Response({'error': 'product_id é obrigatório'}, status=status.HTTP_400_BAD_REQUEST)

        # Verifica se já existe
        existing = Wishlist.objects.filter(user_profile__user=request.user, product_id=product_id).first()
        if existing:
            return Response({'error': 'Produto já está nos favoritos'}, status=status.HTTP_400_BAD_REQUEST)

        # Cria
        wishlist_item = Wishlist.objects.create(user_profile=request.user.profile, product_id=product_id)
        serializer = WishlistSerializer(wishlist_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class WishlistDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk):
        try:
            wishlist_item = Wishlist.objects.get(pk=pk, user_profile__user=request.user)
        except Wishlist.DoesNotExist:
            return Response({'error': 'Item não encontrado'}, status=status.HTTP_404_NOT_FOUND)

        wishlist_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class WishlistToggleView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        product_id = request.data.get('product_id')
        if not product_id:
            return Response({'error': 'product_id é obrigatório'}, status=status.HTTP_400_BAD_REQUEST)

        # Verificar se já existe
        wishlist_item = Wishlist.objects.filter(
            user_profile__user=request.user,
            product_id=product_id
        ).first()

        if wishlist_item:
            wishlist_item.delete()
            return Response({'added': False}, status=status.HTTP_200_OK)
        else:
            Wishlist.objects.create(
                user_profile=request.user.profile,
                product_id=product_id
            )
            return Response({'added': True}, status=status.HTTP_201_CREATED)

        
class AddressFromOrderView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):

        order_id = request.data.get('order_id')

        if not order_id:
            return Response(
                {'error': 'order_id é obrigatório.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            if order_id:
                #order = Order.objects.get(order_ref=order_id, user=request.user)
                order = Order.objects.get(order_ref=order_id)
        except Order.DoesNotExist:
            return Response(
                {'error': 'Encomenda não encontrada.'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Criar endereço a partir dos dados da encomenda
        address, created = Address.objects.get_or_create(
            user_profile=request.user.profile,
            street=order.street,
            number=order.number,
            floor=order.floor or '',
            postal_code=order.postal_code,
            city=order.city,
            country=order.country,
            defaults={'name': 'Casa', 'is_default': True}
        )
        if not created and not address.is_default:
            address.is_default = True
            address.save()

        return Response({
            'status': 'Morada guardada com sucesso.',
            'created': created,
            'address': AddressSerializer(address).data
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)