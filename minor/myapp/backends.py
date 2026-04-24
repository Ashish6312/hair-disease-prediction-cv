from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.db.models import Q

class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Check if the "username" provided is an email
            user = User.objects.get(Q(email__iexact=username) | Q(username__iexact=username))
        except User.DoesNotExist:
            return None
        except User.MultipleObjectsReturned:
            # If multiple users have the same email (shouldn't happen if unique), 
            # pick the first one or handle appropriately
            user = User.objects.filter(Q(email__iexact=username) | Q(username__iexact=username)).first()
            
        if user.check_password(password):
            return user
        return None
