
from rest_framework import serializers
from .models import Register
from .models import *

class RegisterSerializer(serializers.ModelSerializer):
    latitude = serializers.FloatField(required=False, allow_null=True)
    longitude = serializers.FloatField(required=False, allow_null=True)

    class Meta:
        model = Register
        fields = '__all__'



# serializers.py
from rest_framework import serializers
from .models import DepressionPrediction

class DepressionPredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepressionPrediction
        fields = '__all__'

class AdvancedDepressionPredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdvancedDepressionPrediction
        fields = '__all__'


class ADHDPredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ADHDPrediction
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




from rest_framework import serializers
from .models import tbl_hospital_doctor_register

class HospitalDoctorProfileUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = tbl_hospital_doctor_register
        fields = [
            'name', 'email', 'qualification', 'specialization', 'experience',
            'hospital_address', 'hospital_phone', 'latitude', 'longitude', 'age',
            'gender', 'place', 'image', 'medical_id','hospital_name'
        ]
        extra_kwargs = {
            'email': {'required': False},
        }





class HospitalDoctorTimeSlotGroupSerializer(serializers.ModelSerializer):
    doctor_name = serializers.CharField(source='doctor.name', read_only=True)
    timeslots = serializers.ListField(
        child=serializers.CharField(), required=False
    )  # ✅ accept list of time strings like ["10:00", "10:30"]

    class Meta:
        model = HospitalDoctorTimeSlotGroup
        fields = ['id', 'doctor', 'doctor_name', 'date', 'start_time', 'end_time', 'timeslots']




class HospitalDoctorFeedbackSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True)
    doctor_name = serializers.CharField(source='doctor.name', read_only=True)

    class Meta:
        model = HospitalDoctorFeedback
        fields = ['id', 'user', 'user_name', 'doctor', 'doctor_name', 'rating', 'comments', 'created_at']
        







from adminapp.models import Book
class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model=Book
        fields="__all__"