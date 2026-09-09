import logging
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from .models import Order
from products.models import ProductVariant
from django.db import transaction
logger = logging.getLogger(__name__)


def send_multibanco_payment_email(order: Order):
    """Envia email com dados de pagamento Multibanco (entidade, referência, valor)."""
    try:
        order_ref = order.order_ref
        logger.info(f"📧 A enviar email Multibanco para {order.email} (ordem {order_ref})")
        subject = f"Pagamento da sua encomenda {order_ref} | Glow Seven"
        context = {
            'order': order,
            'entity': order.multibanco_payment.entity,
            'reference': order.multibanco_payment.reference,
            'amount': order.total,
        }
        html_message = render_to_string('orders/emails/multibanco_payment.html', context)
        plain_message = strip_tags(html_message)
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.email],
            html_message=html_message,
            fail_silently=False,
        )
        logger.info(f"✅ Email Multibanco enviado com sucesso para {order.email} (ordem {order_ref})")
    except Exception as e:
        logger.error(f"❌ Erro ao enviar email Multibanco para ordem {order.order_ref}: {e}", exc_info=True)


def send_order_confirmation_to_customer(order: Order):
    """Envia email de confirmação da compra para o cliente."""
    try:
        order_ref = order.order_ref
        logger.info(f"📧 A enviar confirmação para cliente {order.email} (ordem {order_ref})")
        subject = f"Encomenda confirmada {order_ref} | Glow Seven"
        context = {
            'order': order,
            'items': order.items.all(),
            'total': order.total,
            'shipping_method': order.get_shipping_method_display(),
        }
        html_message = render_to_string('orders/emails/order_confirmation_customer.html', context)
        plain_message = strip_tags(html_message)
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.email],
            html_message=html_message,
            fail_silently=False,
        )
        logger.info(f"✅ Confirmação enviada para {order.email} (ordem {order_ref})")
    except Exception as e:
        logger.error(f"❌ Erro ao enviar confirmação para cliente (ordem {order.order_ref}): {e}", exc_info=True)


def send_order_confirmation_to_admin(order: Order):
    """Envia email de notificação para o admin (loja)."""
    try:
        order_ref = order.order_ref
        logger.info(f"📧 A enviar notificação para admin (ordem {order_ref})")
        subject = f"Nova encomenda paga {order_ref}"
        context = {
            'order': order,
            'items': order.items.all(),
            'total': order.total,
            'customer': order.full_name,
            'email': order.email,
        }
        html_message = render_to_string('orders/emails/order_confirmation_admin.html', context)
        plain_message = strip_tags(html_message)
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.DEFAULT_FROM_EMAIL],
            html_message=html_message,
            fail_silently=False,
        )
        logger.info(f"✅ Notificação para admin enviada (ordem {order_ref})")
    except Exception as e:
        logger.error(f"❌ Erro ao enviar notificação para admin (ordem {order.order_ref}): {e}", exc_info=True)


def confirm_order_payment(order: Order):
    """
    Confirma o pagamento da ordem:
    - Altera o status para 'paid'
    - Subtrai stock das variantes correspondentes a cada item
    - Envia emails de confirmação (cliente e admin)
    """
    if order.status == "paid":
        logger.info(f"⏩ Ordem {order.order_ref} já está paga. Nenhuma ação tomada.")
        return

    logger.info(f"🔄 Confirmando pagamento da ordem {order.order_ref}")

    with transaction.atomic():
        # Subtrair stock para cada item da ordem
        for item in order.items.all():
            product = item.product
            size = item.size
            color = item.color
            quantity = item.quantity

            # Encontrar a variante correspondente (product + size + color)
            variant = ProductVariant.objects.filter(
                product=product,
                size__value=size,
                color__name=color,
            ).first()

            if variant:
                if variant.stock < quantity:
                    logger.error(
                        f"Stock insuficiente para {product.name} (tamanho {size}, cor {color}). "
                        f"Stock atual: {variant.stock}, pretendido: {quantity}"
                    )
                    # Lança erro para reverter a transação e manter ordem pendente
                    raise ValueError(
                        f"Stock insuficiente para {product.name} (tamanho {size}, cor {color})"
                    )
                variant.stock -= quantity
                variant.save()
                logger.info(
                    f"Stock subtraído: {product.name} (tamanho {size}, cor {color}) - {quantity} unidades"
                )
            else:
                # Se não encontrar variante, regista aviso e continua
                # (podes optar por lançar erro se preferires)
                logger.warning(
                    f"Variante não encontrada para {product.name} (tamanho {size}, cor {color})"
                )

        # Marcar ordem como paga
        order.status = "paid"
        order.save()
        logger.info(f"✅ Ordem {order.order_ref} atualizada para 'paid'")

    # Enviar emails (fora da transação para não bloquear)
    send_order_confirmation_to_customer(order)
    send_order_confirmation_to_admin(order)