from django.urls import path, include
from django.contrib.auth.models import User
from rest_framework import routers, serializers, viewsets
from .models import *
from datetime import datetime
# Serializers define the API representation.
current_date = datetime.now().date()

class MesanMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = MesanMaster
        fields = '__all__'


class OpenOrdersSerializer(serializers.ModelSerializer):
    # mesan_item_ref = serializers.CharField(source="mesan_item_ref.mesan_item_name")
    
    class Meta:
        model = OpenOrders
        fields = '__all__'
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        remaining_qty=float(representation.get('balance_qty',0.0)) -float(representation.get('allocated_qty',0.0))
        representation['remaining_qty']=str(remaining_qty)
        representation['open_orders_qty']=str(representation.get('balance_qty',0.0)*1000)
        representation['sales_price_per_1000'] = str(float(representation.get('sales_price_per_1000',0)) / 1000)
        representation['order_qty'] = str(float(representation.get('order_qty',0.0)) * 1000)
        
        # representation['total_order_line_value'] = str(float(representation.get('order_qty',0)) * (float(representation.get('sales_price_per_1000')) * 1000))
# 
        return representation

class OpenOrdersEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = OpenOrders
        fields = ['order_entry_date','requested_ship_date']
        # field_name = {str(current_date): 'weekno'}
        
 
class BomSerializer(serializers.ModelSerializer):
    class Meta:
        model = BOM
        fields = '__all__'


class StockDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockData
        fields = '__all__'
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['balance'] = str(float(representation.get('balance')) * 1000)

        return representation
        

class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = '__all__'
        
class PurchaseSasSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseSas
        fields = '__all__'
        
class MasterDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = MasterData
        fields = '__all__'

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerMaster
        fields = '__all__'

class LeadTimeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeadTimeMaster
        fields = '__all__'
        


class SupplyTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupplyType
        fields = '__all__'

class MasterSupplyCodeSerializer(serializers.ModelSerializer):
    type = serializers.CharField(source="type.code")

    class Meta:
        model = MasterSupplyCode
        fields = '__all__'

    def update(self, instance, validated_data):
        type_id = validated_data.pop('type', None)
        if type_id is not None:
            try:
                type_obj=SupplyType.objects.get(code=type_id['code'])
            except:
                type_obj=instance.type
                    
            instance.type = type_obj

        # Update remaining fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Save and return the updated instance
        instance.save()
        return instance
        
        

class WorkOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkOrder
        fields = '__all__'
        
class EventTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventType
        fields = ('color','type_name')
    
class EventSerializer(serializers.ModelSerializer):
    color = serializers.CharField(source='type_name.color', read_only=True)
    start = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%S.000Z')
    end = serializers.DateTimeField(format='%Y-%m-%dT%H:%M:%S.000Z')
    

    class Meta:
        model = Event
        exclude = ['id','type_name','location','description']
        # depth = 1

        
