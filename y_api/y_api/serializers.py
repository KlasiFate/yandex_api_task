from rest_framework import serializers
from rest_framework.serializers import ValidationError
import uuid
import math

from .models import ShopUnit, ShopUnitType

class TypeField(serializers.Field):
    # this is only for transferring string "type" field to integer "type" field and back
    def to_representation(self, value):
        for key, value_ in ShopUnitType.choices:
            if key == value:
                return value_.upper()
    
    def to_internal_value(self, data):
        try:
            return ShopUnitType[data].value
        except KeyError as error:
            raise ValidationError({'type':'Invalid value for the "type" field'}) from error

class parentIdField(serializers.Field):
    def to_representation(self, parent_obj):
        if parent_obj:
            res = parent_obj.id.urn
            return res.split(':')[-1]
    
    def to_internal_value(self, data):
        if data is None:
            return data
        if not isinstance(data, str):
            raise ValidationError({'parentId':'Invalid type of value for the "parentId" field'})
        try:
            return uuid.UUID(data)
        except ValueError as error:
            raise ValidationError({'parentId':'Invalid value of the "parentId" field'}) from error
       
        
class ShopUnitSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField()
    type = TypeField()
    parentId = parentIdField(allow_null=True)
    price = serializers.IntegerField(allow_null=True, max_value=2147483647, min_value=0, required=False)
    date = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%S.%fZ', required=False)
        
    
    class Meta:
        model = ShopUnit
        fields = '__all__'
        
    def validate(self, data):
        # price validation by the type
        if data['type'] == ShopUnitType.CATEGORY and data.get('price') is not None:
            raise ValidationError(
                {'price':'The "price" field should be null if the "type" field equals "CATEGORY".'}
            )
        elif data['type'] == ShopUnitType.OFFER and data.get('price') is None:
            raise ValidationError(
                {'price':'The "price" field can\'t be null if the "type" field equals "price".'}
            )
                
        #TODO: add validation of unique of "id" fields in the "items" field
        
        return super().validate(data)
    
class MoreDetailShopUnitSerializer(ShopUnitSerializer):
    children = serializers.SerializerMethodField()
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # this method should change price of ShopUnit 
        # self.change_price() # it doesn't work because it calls a error which must not raise. The error is BUG. The author of django REST framework is fucked idiot
    
    def get_children(self, obj):
        if not hasattr(self, 'children_'):
            self.get_children_and_price(obj)
        return self.children_
    
    def change_price(self):
        if self.data['type'] == ShopUnitType.CATEGORY:
            self._data['price'] = self.price_
        
    def get_children_and_price(self, obj):
        if obj.type == ShopUnitType.OFFER:
            self.children_ = None
            return
        self.children_ = MoreDetailShopUnitSerializer(obj.shopunit_set.all(), many=True).data

        sm = 0
        i = -1
        for i, child in enumerate(self.children_):
            if child['price'] is not None:
                sm += child['price']
        if i == -1:
            self.price_ = None
            return
        else:
            self.price_ = math.floor(sm / (i + 1))
            
            
            
            
            
            

class ImportsSerializer(serializers.Serializer):
    items = ShopUnitSerializer(many=True)
    updateDate = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%S.%fZ')
    
    def validate(self, data):
        ids = set()
        for item in data['items']:
            # parentId validation by type of the parent
            if item['parentId'] is not None:
                try:
                    unit = ShopUnit.objects.get(id=item['parentId'])
                except ShopUnit.DoesNotExist:
                    if item['parentId'] not in ids:
                        raise ValidationError(
                            # {'items':{'parentId':'A ShopUnit with given id as value of the "parentId" field doesn\'t exist.'}}
                        )
                else:
                    if unit.type == ShopUnitType.OFFER:
                        raise ValidationError(
                            # {'parentId':'A ShopUnit can\'t have a parent which his value of type is "OFFER".'}
                        )
                    
            ids.add(item['id'])
            
        return data
    
    def create(self, validated_data):
        with ShopUnit.objects.bulk_update_or_create_context(
            ['type', 'name', 'date', 'parentId', 'price'],
            match_field='id',
            batch_size=50
        ) as bulkit:
            units = {}
            for item in validated_data['items']:
                if item.get('parentId'):
                    try:
                        item['parentId'] = ShopUnit.objects.get(id=item.get('parentId'))
                    except ShopUnit.DoesNotExist:
                        parent_unit = units.get(item['parentId'])
                        if not parent_unit:
                            raise
                        item['parentId'] = parent_unit
                
                unit = ShopUnit(**item, date=validated_data['updateDate'])
                bulkit.queue(unit)
                units[item['id']] = unit
            
        # for item in validated_data['items']:
        #     if item.get('parentId'):
        #         item['parentId'] = ShopUnit.objects.get(id=item.get('parentId'))
        #     try:
        #         unit = ShopUnit.objects.get(id=item['id'])
        #         for key, value in item:
        #             
        #     except ShopUnit.DoesNotExist:
        #         unit = ShopUnit(**item, date=validated_data['updateDate'])
        #     unit.save()
            
            
            # ShopUnit(**item, date=validated_data['updateDate'])
            
            
        # it returns False only for not raising Exception
        return False










