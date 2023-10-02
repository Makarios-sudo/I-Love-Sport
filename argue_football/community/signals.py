# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from argue_football.community import models as v2_models
# from argue_football.users.models import Account


# @receiver(post_save, sender=v2_models.FriendRequest)
# def create_new_request(sender, instance=None, created=False, **kwargs):
#     if created:
#         account = Account.objects.get(id=instance.receiver.id)
#         user = account.owner
       
#         v2_models.Friends.objects.create(
#             owner = user,
#             account = instance.receiver,
#             new_request = instance
#         )