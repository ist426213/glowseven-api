from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from decimal import Decimal
from .models import Order, OrderItem, MBwayPayment, MultibancoPayment
from .serializers import CheckoutSerializer, OrderSerializer, CouponValidateSerializer
from .utils import send_multibanco_payment_email, confirm_order_payment
from .services.ifthenpay import init_multibanco_payment, init_mbway_payment
import random
import logging
import threading

logger = logging.getLogger(__name__)
IFTHENPAY_ANTI_PHISHING_KEY = getattr(settings, 'IFTHENPAY_ANTI_PHISHING_KEY', '')


def send_email_async(email_func, order):
    """Envia email em thread separada para não bloquear a resposta."""
    def task():
        try:
            email_func(order)
        except Exception as e:
            logger.error(f"Erro ao enviar email para ordem #{order.id}: {e}")
    thread = threading.Thread(target=task)
    thread.start()


class CheckoutAPIView(CreateAPIView):

    """Cria uma nova encomenda, processa o pagamento e integra com a IfThenPay."""
    serializer_class = OrderSerializer

    def create(self, request, *args, **kwargs):

        logger.info("Iniciando checkout...")
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        logger.info(f"Dados do checkout validados: {data}")

        order = Order.objects.create(
            email=data["email"],
            full_name=data["full_name"],
            street=data["street"],
            number=data["number"],
            floor=data.get("floor", ""),
            postal_code=data["postal_code"],
            city=data["city"],
            country=data["country"],
            shipping_method=data["shipping_method"],
            payment_method=data["payment_method"],
            coupon=data.get("coupon"),
            coupon_discount=data.get("coupon_discount", 0),
            subtotal=data["subtotal"],
            shipping_cost=data["shipping_cost"],
            total=data["total"],
            status="pending",
        )

        if request.user.is_authenticated:
            order.user = request.user
            order.save(update_fields=["user"])
            logger.info(f"Ordem #{order.id} associada ao user {request.user.username}")
        else:
            logger.info("👤 Utilizador não autenticado – ordem sem user")

        logger.info(f"Ordem criada: #{order.id} (user: {order.user})")

        for item_data in data["items"]:
            product = item_data["_product"]
            OrderItem.objects.create(
                order=order,
                product=product,
                product_name=product.name,
                product_price=item_data["_price"],
                quantity=item_data["quantity"],
                size=item_data.get("size", ""),
                color=item_data.get("color", ""),
            )
        logger.info(f"Itens da ordem #{order.id} criados.")

        if data.get("coupon"):
            coupon = data["coupon"]
            coupon.used_count += 1
            coupon.save()
            logger.info(f"Cupão {coupon.code} usado na ordem #{order.id}.")

        if data["payment_method"] == "mbway":
            mbway = MBwayPayment.objects.create(
                phone=data["mbway_phone"],
                authorized=False,
            )
            order.mbway_payment = mbway
            order.save()
            try:
                result = init_mbway_payment(order)
                mbway.request_id = result.get("request_id", "")
                mbway.status = result.get("status", "")
                mbway.amount = result.get("amount", 0)
                mbway.raw_data = result.get("raw_data", {})
                mbway.save()
                logger.info(f"✅ MBWAY inicializado com sucesso: {result}")
            except Exception as e:
                logger.error(f"❌ Erro ao inicializar MBWAY: {e}")
                mbway.status = "local_fallback"
                mbway.save()

        elif data["payment_method"] == "multibanco":
            multibanco = MultibancoPayment.objects.create(
                entity="",
                reference="",
                amount=data["total"],
                paid=False,
            )
            order.multibanco_payment = multibanco
            order.save()
            try:
                result = init_multibanco_payment(order)
                multibanco.entity = result["entity"]
                multibanco.reference = result["reference"]
                multibanco.request_id = result.get("request_id", "")
                multibanco.status = result.get("status", "")
                multibanco.raw_data = result.get("raw_data", {})
                multibanco.save()
                logger.info(f"✅ Multibanco inicializado com sucesso: {result}")
                send_email_async(send_multibanco_payment_email, order)
            except Exception as e:
                logger.error(f"❌ Erro ao obter referência Multibanco: {e}")
                multibanco.entity = "12345"
                multibanco.reference = str(random.randint(100000000, 999999999))
                multibanco.status = "local_fallback"
                multibanco.raw_data = {"error": str(e)}
                multibanco.save()
                send_email_async(send_multibanco_payment_email, order)

        order.save()
        logger.info(f"Ordem #{order.id} guardada com sucesso.")

        order_serializer = OrderSerializer(order)
        return Response(order_serializer.data, status=status.HTTP_201_CREATED)


class ValidateCouponAPIView(CreateAPIView):
    """Valida um cupão de desconto e retorna o valor do desconto."""
    serializer_class = CouponValidateSerializer

    def post(self, request, *args, **kwargs):
        logger.info("Validando cupão...")
        serializer = CouponValidateSerializer(data=request.data)
        if serializer.is_valid():
            logger.info(f"Cupão válido: {serializer.validated_data['coupon'].code}")
            return Response({
                "valid": True,
                "discount": float(serializer.validated_data["discount"]),
                "message": "Cupão aplicado com sucesso!"
            })
        logger.warning(f"Cupão inválido: {serializer.errors}")
        return Response({
            "valid": False,
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class PaymentMBWayAPIView(APIView):
    """Endpoint manual para confirmar pagamento MBWAY (botão "Já paguei")."""
    def post(self, request):
        order_identifier = request.data.get("order_id")
        logger.info(f"Verificando pagamento MBWAY para ordem {order_identifier}")

        try:
            order = Order.objects.get(order_ref=order_identifier)
        except Order.DoesNotExist:
            try:
                order = Order.objects.get(id=int(order_identifier))
            except (Order.DoesNotExist, ValueError):
                logger.error(f"Ordem não encontrada: {order_identifier}")
                return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        if order.payment_method != "mbway":
            logger.error(f"Método de pagamento inválido para ordem {order_identifier}: {order.payment_method}")
            return Response({"error": "Invalid payment method"}, status=status.HTTP_400_BAD_REQUEST)

        mbway = order.mbway_payment
        if not mbway:
            logger.error(f"Pagamento MBWAY não associado à ordem {order_identifier}")
            return Response({"error": "No MBWAY payment associated"}, status=status.HTTP_400_BAD_REQUEST)

        if mbway.authorized:
            if order.status == "pending":
                logger.info(f"Ordem {order_identifier} autorizada, confirmando pagamento...")
                confirm_order_payment(order)
            return Response({
                "status": "success",
                "message": "Pagamento já autorizado.",
                "order_id": order_identifier
            }, status=status.HTTP_200_OK)
        else:
            logger.info(f"Ordem {order_identifier} ainda pendente de autorização MBWAY.")
            return Response({
                "status": "pending",
                "message": "Pagamento ainda não foi autorizado. Aguarde a confirmação do gateway."
            }, status=status.HTTP_200_OK)


class PaymentMultibancoAPIView(APIView):
    """Endpoint manual para confirmar pagamento Multibanco (botão "Já paguei")."""
    def post(self, request):
        order_identifier = request.data.get("order_id")
        logger.info(f"Verificando pagamento Multibanco para ordem {order_identifier}")

        try:
            order = Order.objects.get(order_ref=order_identifier)
        except Order.DoesNotExist:
            try:
                order = Order.objects.get(id=int(order_identifier))
            except (Order.DoesNotExist, ValueError):
                logger.error(f"Ordem não encontrada: {order_identifier}")
                return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        if order.payment_method != "multibanco":
            logger.error(f"Método de pagamento inválido para ordem {order_identifier}: {order.payment_method}")
            return Response({"error": "Invalid payment method"}, status=status.HTTP_400_BAD_REQUEST)

        multibanco = order.multibanco_payment
        if not multibanco:
            logger.error(f"Pagamento Multibanco não associado à ordem {order_identifier}")
            return Response({"error": "No Multibanco payment associated"}, status=status.HTTP_400_BAD_REQUEST)

        if multibanco.paid:
            if order.status == "pending":
                logger.info(f"Ordem {order_identifier} paga, confirmando pagamento...")
                confirm_order_payment(order)
            return Response({
                "status": "success",
                "message": "Pagamento já confirmado.",
                "order_id": order_identifier,
                "payment_details": {
                    "entity": multibanco.entity,
                    "reference": multibanco.reference,
                    "amount": str(multibanco.amount),
                }
            }, status=status.HTTP_200_OK)
        else:
            logger.info(f"Ordem {order_identifier} ainda pendente de confirmação Multibanco.")
            return Response({
                "status": "pending",
                "message": "Pagamento ainda não foi confirmado. Aguarde a confirmação do gateway."
            }, status=status.HTTP_200_OK)


class PaymentMBWayWebhookAPIView(APIView):
    """Webhook MBWAY – recebe notificações de pagamento autorizado via GET."""
    def get(self, request):
        received_key = request.GET.get('key')
        if received_key != IFTHENPAY_ANTI_PHISHING_KEY:
            logger.warning(f"Chave anti-phishing inválida (MBWAY): {received_key}")
            return Response({"error": "Invalid anti-phishing key"}, status=status.HTTP_403_FORBIDDEN)

        order_identifier = request.GET.get('orderId')
        request_id = request.GET.get('requestId')
        amount_raw = request.GET.get('amount', '0')

        try:
            amount_decimal = Decimal(amount_raw.replace(',', '.'))
        except:
            amount_decimal = Decimal('0.00')

        logger.info(f"Webhook MBWAY recebido: orderId={order_identifier}, requestId={request_id}, amount={amount_decimal}")

        if not order_identifier:
            logger.error("Webhook MBWAY sem orderId")
            return Response({"error": "Missing orderId"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            order = Order.objects.get(order_ref=order_identifier)
        except Order.DoesNotExist:
            try:
                order = Order.objects.get(id=int(order_identifier))
            except (Order.DoesNotExist, ValueError):
                logger.error(f"Ordem não encontrada: {order_identifier}")
                return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        if order.payment_method != "mbway":
            logger.error(f"Método de pagamento inválido no webhook MBWAY para ordem {order_identifier}: {order.payment_method}")
            return Response({"error": "Invalid payment method"}, status=status.HTTP_400_BAD_REQUEST)

        mbway = order.mbway_payment
        if not mbway:
            logger.error(f"Pagamento MBWAY não associado à ordem {order_identifier} no webhook.")
            return Response({"error": "No MBWAY payment associated"}, status=status.HTTP_400_BAD_REQUEST)

        if mbway.authorized:
            logger.info(f"Ordem {order_identifier} já estava autorizada.")
            return Response({"status": "already_authorized"}, status=status.HTTP_200_OK)

        from django.utils.timezone import now
        mbway.authorized = True
        mbway.authorized_at = now()
        mbway.request_id = request_id or mbway.request_id
        mbway.amount = amount_decimal if amount_decimal > 0 else mbway.amount
        mbway.save()
        logger.info(f"Pagamento MBWAY autorizado para ordem {order_identifier} via webhook.")
        confirm_order_payment(order)

        return Response({
            "status": "success",
            "message": "Pagamento MBWAY confirmado pelo gateway.",
            "order_ref": order.order_ref,
            "order_id": order.id,
        }, status=status.HTTP_200_OK)


class PaymentMultibancoWebhookAPIView(APIView):
    """Webhook Multibanco – recebe notificações de pagamento confirmado via GET."""
    def get(self, request):
        received_key = request.GET.get('key')
        if received_key != IFTHENPAY_ANTI_PHISHING_KEY:
            logger.warning(f"Chave anti-phishing inválida (Multibanco): {received_key}")
            return Response({"error": "Invalid anti-phishing key"}, status=status.HTTP_403_FORBIDDEN)

        order_identifier = request.GET.get('orderId')
        request_id = request.GET.get('requestId')
        entity = request.GET.get('entity')
        reference = request.GET.get('reference')
        amount_raw = request.GET.get('amount', '0')

        try:
            amount_decimal = Decimal(amount_raw.replace(',', '.'))
        except:
            amount_decimal = Decimal('0.00')

        logger.info(f"Webhook Multibanco recebido: orderId={order_identifier}, entity={entity}, reference={reference}, amount={amount_decimal}")

        if not order_identifier:
            logger.error("Webhook Multibanco sem orderId")
            return Response({"error": "Missing orderId"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            order = Order.objects.get(order_ref=order_identifier)
        except Order.DoesNotExist:
            try:
                order = Order.objects.get(id=int(order_identifier))
            except (Order.DoesNotExist, ValueError):
                logger.error(f"Ordem não encontrada: {order_identifier}")
                return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        if order.payment_method != "multibanco":
            logger.error(f"Método de pagamento inválido no webhook Multibanco para ordem {order_identifier}: {order.payment_method}")
            return Response({"error": "Invalid payment method"}, status=status.HTTP_400_BAD_REQUEST)

        multibanco = order.multibanco_payment
        if not multibanco:
            logger.error(f"Pagamento Multibanco não associado à ordem {order_identifier} no webhook.")
            return Response({"error": "No Multibanco payment associated"}, status=status.HTTP_400_BAD_REQUEST)

        if multibanco.paid:
            logger.info(f"Ordem {order_identifier} já estava paga.")
            return Response({"status": "already_paid"}, status=status.HTTP_200_OK)

        from django.utils.timezone import now
        multibanco.paid = True
        multibanco.paid_at = now()
        if entity:
            multibanco.entity = entity
        if reference:
            multibanco.reference = reference
        if request_id:
            multibanco.request_id = request_id
        multibanco.amount = amount_decimal if amount_decimal > 0 else multibanco.amount
        multibanco.save()
        logger.info(f"Pagamento Multibanco confirmado para ordem {order_identifier} via webhook.")
        confirm_order_payment(order)

        return Response({
            "status": "success",
            "message": "Pagamento Multibanco confirmado pelo gateway.",
            "order_ref": order.order_ref,
            "order_id": order.id,
            "payment_details": {
                "entity": entity,
                "reference": reference,
                "amount": str(amount_decimal),
            }
        }, status=status.HTTP_200_OK)