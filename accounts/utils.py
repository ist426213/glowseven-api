# accounts/utils.py
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings

def send_activation_email(user, request):
    """
    Envia um email de ativação com link para o frontend.
    """
    profile = user.profile
    token = profile.activation_token

    frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000').strip()
    activation_link = f"{frontend_url}/activate-account?token={token}"  # ← caminho correto

    subject = "Ative a sua conta Glow Seven"
    context = {
        'user': user,
        'activation_link': activation_link,
    }

    # HTML
    html_message = render_to_string('accounts/emails/activation_email.html', context)

    # ✅ Texto plano personalizado (sem duplicação do URL com colchetes)
    plain_message = (
        f"Olá {user.first_name or user.username},\n\n"
        f"Obrigado por se registar na Glow Seven.\n\n"
        f"Para ativar a sua conta, clique no link abaixo:\n"
        f"{activation_link}\n\n"
        f"Se não se registou, ignore este email.\n\n"
        f"Equipa Glow Seven"
    )

    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=False,
    )