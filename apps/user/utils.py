from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def send_otp_email(user, otp):
    """
    Send OTP verification email to the user
    """
    subject = 'Verify Your Email Address'
    html_message = render_to_string('user/email/email_verification.html', {
        'user': user,
        'otp': otp,
        'site_name': 'E-commerce API'
    })
    plain_message = strip_tags(html_message)
    
    return send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        html_message=html_message,
        fail_silently=False,
    )
