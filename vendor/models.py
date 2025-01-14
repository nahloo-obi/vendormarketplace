from django.db import models

from accounts.models import User, UserProfile
from accounts.utils import send_notification
from datetime import time, date, datetime
# Create your models here.

class Vendor(models.Model):
    user = models.OneToOneField(User, related_name="user", on_delete=models.CASCADE)
    user_profile = models.OneToOneField(UserProfile, related_name="user_profile", on_delete=models.CASCADE)
    vendor_slug = models.SlugField(max_length=100, unique=True)
    vendor_name = models.CharField(max_length=50)
    vendor_license = models.ImageField(upload_to='vendor/license')
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.vendor_name
    

    def is_open(self):
        get_today = date.today()
        today = get_today.isoweekday()    #to get the week day number

        current_day_opening_hour = OpeningHours.objects.filter(vendor=self, day=today)
        
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        
        is_open = None

        for current in current_day_opening_hour:

            if current.from_hour == "" and current.to_hour == "":
                is_open = False

            else:
                start = str(datetime.strptime(current.from_hour, "%I:%M %p").time())
                end = str(datetime.strptime(current.to_hour, "%I:%M %p").time())
      
                if current_time > start and current_time < end:
     
                    is_open = True
                    break
                else:
                    is_open = False

        return is_open
    

    def save(self, *args, **kwargs):
        if self.pk is not None:
            orig = Vendor.objects.get(pk=self.pk)

            if orig.is_approved != self.is_approved:
                mail_template = "accounts/emails/admin_approval_email.html"
                context = {
                    'user': self.user,
                    'is_approved': self.is_approved,
                    'to_email': self.user.email,
                }

                if self.is_approved == True:
                    mail_subject = "Congratulations!, Your Business has been approved"
                    
                    send_notification(mail_subject, mail_template, context)

                else:
                    mail_subject = "We are sorry your Business has not been approved to be on our platform"
                   
                    send_notification(mail_subject, mail_template, context)

        return super(Vendor, self).save(*args, **kwargs)


DAYS = [
    (1, ('Monday')),
    (2, ('Tuesday')),
    (3, ('Wednesday')),
    (4, ('Thursday')),
    (5, ('Friday')),
    (6, ('Saturday')),
    (7, ('Sunday')),
]

HOUR_OF_DAY = t = [(time(h, m).strftime('%I:%M %p'), time(h, m).strftime('%I:%M %p')) for h in range(0,24) for m in (0,30)]


class OpeningHours(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    day = models.IntegerField(choices=DAYS)
    from_hour = models.CharField(choices=HOUR_OF_DAY, max_length=10, blank=True)
    to_hour = models.CharField(choices=HOUR_OF_DAY, max_length=10, blank=True)
    is_closed = models.BooleanField(default=False)

    class Meta:
        ordering = ('day', '-from_hour')
        unique_together = ('vendor', 'day', 'from_hour', 'to_hour')


    def __str__(self):
        return self.get_day_display()   #field name is day
