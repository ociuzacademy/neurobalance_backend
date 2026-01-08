
from rest_framework import serializers
from .models import Register
from .models import *

class RegisterSerializer(serializers.ModelSerializer):
    latitude = serializers.FloatField(required=False, allow_null=True)
    longitude = serializers.FloatField(required=False, allow_null=True)

    class Meta:
        model = Register
        fields = '__all__'



from rest_framework import serializers
from .models import tbl_hospital_doctor_register

class HospitalDoctorRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = tbl_hospital_doctor_register
        exclude = ['available']  # 👈 hide from Swagger input

    def create(self, validated_data):
        # 👇 Always mark new hospital doctors as available by default
        validated_data['available'] = True
        return super().create(validated_data)

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        if instance.image:
            rep['image'] = instance.image.url
        if instance.medical_id:
            rep['medical_id'] = instance.medical_id.url
        rep['available'] = instance.available  # 👈 show in API response
        return rep



       
from rest_framework import serializers

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()





# serializers.py
from rest_framework import serializers
from .models import DepressionPrediction

class DepressionPredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepressionPrediction
        fields = '__all__'


class ADHDPredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ADHDPrediction
        fields = '__all__'

