import os
import django
import sys

# Script setup
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_dir)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'minor.settings')
django.setup()

from myapp.models import SubscriptionPlan
from django.contrib.auth.models import User
from myapp.models import UserSubscription

# Create default plans
plans = [
    {
        'name': 'Free Tier',
        'price': 0.00,
        'scan_limit': 5,
        'features': 'Basic AI diagnosis,Low priority support,Community access,5 Scans/Month'
    },
    {
        'name': 'Pro User',
        'price': 9.99,
        'scan_limit': 100,
        'features': 'Advanced AI diagnosis,Detailed Clinical Assessment,High priority support,PDF Export,100 Scans/Month'
    },
    {
        'name': 'Clinic Enterprise',
        'price': 49.99,
        'scan_limit': -1, # Unlimited
        'features': 'SaaS Dashboard for Patients,Unlimited AI Sub-accounts,White-label reports,24/7 Priority Support,Unlimited Scans'
    }
]

for plan_data in plans:
    plan, created = SubscriptionPlan.objects.get_or_create(
        name=plan_data['name'],
        defaults={
            'price': plan_data['price'],
            'scan_limit': plan_data['scan_limit'],
            'features': plan_data['features']
        }
    )
    if created:
        print(f"Created Plan: {plan.name}")
    else:
        # Update existing
        plan.price = plan_data['price']
        plan.scan_limit = plan_data['scan_limit']
        plan.features = plan_data['features']
        plan.save()
        print(f"Updated Plan: {plan.name}")

print("Default SaaS plans initialized.")

# Ensure existing users have a free plan
free_plan = SubscriptionPlan.objects.get(name='Free Tier')
users_without_sub = User.objects.filter(subscription__isnull=True)
count = 0
for u in users_without_sub:
    UserSubscription.objects.create(user=u, plan=free_plan)
    count += 1
print(f"Assigned Free plan to {count} existing users without a subscription.")
