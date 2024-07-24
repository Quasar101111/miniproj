# #users/adapteres.py

# from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
# from django.contrib.auth import get_user_model
# from .models import Profile

# class MySocialAccountAdapter(DefaultSocialAccountAdapter):
#     def pre_social_login(self, request, sociallogin):
#         if sociallogin.is_existing:
#             return

#         user = sociallogin.user
#         if not user.id:
#             try:
#                 existing_user = get_user_model().objects.get(email=user.email)
#                 sociallogin.connect(request, existing_user)
#             except get_user_model().DoesNotExist:
#                 user.save()
#                 # Set the user_type based on the next parameter
#                 user_type = request.GET.get('user_type')
#                 profile = Profile(user=user, user_type=user_type)
#                 profile.save()
