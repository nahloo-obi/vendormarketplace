from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.conf import settings

def detectUser(user):
    if user.role == 1:
        redirecturl = 'vendorDashboard'
        return redirecturl
    
    elif user.role == 2:
        redirecturl = "customerDashboard"
        return redirecturl
    
    elif user.role == None and user.is_superadmin:
        redirecturl = '/admin'
        return redirecturl
    

def send_email_verification(request, user, mail_subject, email_template):
    from_email = settings.DEFAULT_FROM_EMAIL
    site  = get_current_site(request)
    email_body = render_to_string(email_template,{
        'user': user,
        'domain': site,
        'uid':urlsafe_base64_encode(force_bytes(user.pk)),
        'token': default_token_generator.make_token(user)
    })
    to_email = user.email
    mail = EmailMessage(mail_subject, email_body, from_email, to=[to_email])
    mail.send()

def send_notification(mail_subject, email_template, context):
    from_email = settings.DEFAULT_FROM_EMAIL
    email_body = render_to_string(email_template, context)
    to_email = context['user'].email
    mail = EmailMessage(mail_subject, email_body, from_email, to=[to_email])
    mail.send()


