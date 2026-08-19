import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)
IFTHENPAY_API_URL = "https://api.ifthenpay.com"


def init_multibanco_payment(order):
    """Inicializa pagamento Multibanco na IfThenPay."""
    url = f"{IFTHENPAY_API_URL}/multibanco/reference/init"
    order_id = order.order_ref if hasattr(order, 'order_ref') and order.order_ref else str(order.id)

    payload = {
        "mbKey": settings.IFTHENPAY_MB_KEY,
        "orderId": order_id,
        "amount": f"{order.total:.2f}",
        "clientEmail": order.email,
        "clientName": order.full_name,
        "clientPhone": order.mbway_payment.phone if order.mbway_payment else "",
        "description": f"Encomenda #{order_id}",
    }

    logger.info(f"🚀 A criar referência Multibanco para ordem {order_id}")
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        logger.info(f"✅ Resposta IfThenPay (Multibanco): {data}")

        return {
            "entity": data.get("Entity", ""),
            "reference": data.get("Reference", ""),
            "request_id": data.get("RequestId", ""),
            "order_ref": order_id,
            "expiry_date": data.get("ExpiryDate", ""),
            "message": data.get("Message", ""),
            "status": data.get("Status", ""),
            "raw_data": data,
        }
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Erro ao chamar IfThenPay Multibanco: {e}")
        raise


def init_mbway_payment(order):
    """Inicializa pagamento MBWAY na IfThenPay."""
    url = f"{IFTHENPAY_API_URL}/spg/payment/mbway"
    phone = order.mbway_payment.phone if order.mbway_payment else ""
    if not phone:
        raise ValueError("Número de telefone não disponível para MBWAY.")

    clean_phone = ''.join(filter(str.isdigit, phone))
    mobile_number = f"351#{clean_phone}" if clean_phone else ""

    order_id = order.order_ref if hasattr(order, 'order_ref') and order.order_ref else str(order.id)

    payload = {
        "mbWayKey": settings.IFTHENPAY_MBWAY_KEY,
        "orderId": order_id,
        "amount": f"{order.total:.2f}",
        "mobileNumber": mobile_number,
        "email": order.email,
        "description": f"Encomenda #{order_id}",
    }

    logger.info(f"🚀 A iniciar MBWAY para ordem {order_id}")
    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        logger.info(f"✅ Resposta IfThenPay (MBWAY): {data}")

        return {
            "request_id": data.get("RequestId", ""),
            "amount": data.get("Amount", "0.00"),
            "message": data.get("Message", ""),
            "status": data.get("Status", ""),
            "order_ref": order_id,
            "raw_data": data,
        }
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Erro ao chamar IfThenPay MBWAY: {e}")
        raise


def check_mbway_status(request_id):
    """Verifica o estado de um pagamento MBWAY na IfThenPay."""
    url = f"{IFTHENPAY_API_URL}/spg/payment/mbway/status"
    params = {
        "mbWayKey": settings.IFTHENPAY_MBWAY_KEY,
        "requestId": request_id,
    }
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    return response.json()