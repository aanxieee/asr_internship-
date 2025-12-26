from rest_framework import serializers

class PricingInputSerializer(serializers.Serializer):
    origin = serializers.CharField(required=True)
    destination = serializers.CharField(required=True)
    mapped_from = serializers.CharField(required=True)
    mapped_to = serializers.CharField(required=True)
    aircraft_id = serializers.IntegerField(required=True)
    flight_hours = serializers.FloatField(required=True)
    passengers = serializers.IntegerField(required=True)
