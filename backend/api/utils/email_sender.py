"Email Sender"
import os
from django.template import Context, Template
from django.conf import settings
import resend


def send_email(to, to_email, verify_secret):
    "Email Sender"
    resend.api_key = settings.EMAIL_HOST_PASSWORD
    subject = f"Verifica tu cuenta de usuario para {settings.WEB_SITE_NAME}"
    html_template_path = os.path.join(os.path.dirname(__file__), "email_html.html")
    with open(html_template_path, "r", encoding="utf-8") as file:
        html_template_content = file.read()
    template = Template(html_template_content)
    context = Context(
        {
            "user_name": to,
            "verification_url": f"{settings.VERIFICATION_URL}{verify_secret}",
        }
    )
    html_message = template.render(context)
    params: resend.Emails.SendParams = {
        "from": "Acme <onboarding@resend.dev>",
        "to": ["aflopez000430@gmail.com", to_email],
        "subject": subject,
        "html": html_message,
    }
    resend.Emails.send(params)
