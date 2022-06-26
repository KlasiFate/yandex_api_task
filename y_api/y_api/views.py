from rest_framework import views
from rest_framework.response import Response
import rest_framework

from .serializers import ImportsSerializer, MoreDetailShopUnitSerializer
from .models import ShopUnit

def return_400():
    return Response(
        {'code':400, 'message':'Validation Failed'},
        status=400,
    )
    
def return_404():
    return Response(
        {'code':404, 'message':'Item not found'},
        status=404,
    )

class YandexAPI(views.APIView):
    # /imports/
    def post(self, request, *args, **kwargs):
        serializer = ImportsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response()
        else:
            return return_400()
        
    # /delete/{id}
    def delete(self, request, *args, **kwargs):
        # if this view func called by different url than "/delete/{id}"
        _id = kwargs.get('id')
        if not _id:
            return return_400()
        
        try:
            ShopUnit.objects.get(id=_id).delete()
            return Response()
        except ShopUnit.DoesNotExist:
            return return_404()

    # /nodes/{id}
    def get(self, request, *args, **kwargs):
        # if this view func called by different url than "/nodes/{id}"
        _id = kwargs.get('id')
        if not _id:
            return return_400()
        
        try:
            unit = ShopUnit.objects.get(id=_id)
            serializer = MoreDetailShopUnitSerializer(unit)
            return Response(serializer.data)
        except ShopUnit.DoesNotExist:
            return return_404()
        
        
    



























