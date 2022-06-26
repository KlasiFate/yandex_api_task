from django.db import models
from bulk_update_or_create import BulkUpdateOrCreateQuerySet
import uuid

class ShopUnitType(models.IntegerChoices):
    OFFER = 0
    CATEGORY = 1

class ShopUnit(models.Model):
    objects = BulkUpdateOrCreateQuerySet.as_manager()
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.PositiveIntegerField(choices=ShopUnitType.choices)
    name = models.CharField(max_length=1024)
    date = models.DateTimeField()# (auto_now=True, auto_now_add=True)
    parentId = models.ForeignKey('self', on_delete=models.CASCADE, null=True)
    price = models.PositiveIntegerField(null=True)
    
    
    
    
    
# class ShopUnitStatisticUnit(models.Model):
#     # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     shop_unit = models.ForeignKey(ShopUnit, on_delete=models.CASCADE)
#     type = models.PositiveIntegerField(choices=ShopUnitType.choices)
#     name = models.CharField(max_length=1024)
#     date = models.DateTimeField()# (auto_now=True, auto_now_add=True)
#     parentId = models.ForeignKey('self', on_delete=models.CASCADE, null=True)
#     price = models.PositiveIntegerField(null=True)


