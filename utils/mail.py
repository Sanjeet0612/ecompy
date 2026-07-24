import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

import config.settings as settings


# -----------------------------
# Jinja2 Template Loader
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

TEMPLATE_DIR = BASE_DIR / "templates" / "email"

env = Environment(
    loader=FileSystemLoader(str(TEMPLATE_DIR)),
    autoescape=True
)


def render_template(template_name: str, context: dict) -> str:
    """
    Render Jinja2 email template.
    """

    template = env.get_template(template_name)
    return template.render(**context)


def send_email(
    to_email: str,
    subject: str,
    template_name: str,
    context: dict
) -> bool:
    """
    Generic Email Sender
    """

    try:

        html = render_template(template_name, context)

        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = settings.SMTP_FROM_EMAIL
        message["To"] = to_email

        message.attach(
            MIMEText(html, "html", "utf-8")
        )

        with smtplib.SMTP(
            settings.SMTP_HOST,
            settings.SMTP_PORT
        ) as server:

            server.ehlo()

            server.starttls()

            server.ehlo()

            server.login(
                settings.SMTP_USERNAME,
                settings.SMTP_PASSWORD
            )

            server.sendmail(
                settings.SMTP_FROM_EMAIL,
                to_email,
                message.as_string()
            )

        return True

    except Exception as e:

        print(f"Email Error : {e}")

        return False


def send_verification_email(
    name: str,
    email: str,
    verify_url: str
) -> bool:
    """
    Vendor Email Verification
    """

    return send_email(

        to_email=email,

        subject="Verify Your Email",

        template_name="verify_email.html",

        context={
            "name": name,
            "verify_url": verify_url,
            "app_name": settings.APP_NAME
        }

    )