from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=50, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    scan_limit = models.IntegerField(help_text="Number of scans allowed per month. Use -1 for unlimited.")
    features = models.TextField(help_text="Comma separated list of features")

    def __str__(self):
        return f"{self.name} (${self.price})"

class UserSubscription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='subscription')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL, null=True, blank=True)
    scans_used = models.IntegerField(default=0)
    last_reset_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} - {self.plan.name if self.plan else 'Free'}"

    def can_scan(self):
        if not self.plan:
            return False
        if self.plan.scan_limit == -1:
            return True
        return self.scans_used < self.plan.scan_limit

@receiver(post_save, sender=User)
def create_user_subscription(sender, instance, created, **kwargs):
    if created:
        # Try to assign a default Free plan if it exists
        free_plan = SubscriptionPlan.objects.filter(price=0).first()
        UserSubscription.objects.create(user=instance, plan=free_plan)

@receiver(post_save, sender=User)
def save_user_subscription(sender, instance, **kwargs):
    instance.subscription.save()

