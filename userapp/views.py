from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from rest_framework.decorators import api_view
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from .models import *

class RegisterViewSet(viewsets.ModelViewSet):
    queryset = Register.objects.all()
    serializer_class = RegisterSerializer



class LoginView(APIView):
    """
    Login endpoint for:
    - Hospital Doctor
    - Normal User 
    """

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        

        # --- Hospital Doctor Login ---
        hospital_doc = tbl_hospital_doctor_register.objects.filter(email=email, password=password).first()
        if hospital_doc:
            if hospital_doc.status != 'approved':
                return Response(
                    {'message': 'Hospital doctor account not approved yet. Please wait for admin approval.'},
                    status=status.HTTP_403_FORBIDDEN
                )

            return Response({
                'id': hospital_doc.id,
                'name': hospital_doc.name,
                'email': hospital_doc.email,
                'phone': hospital_doc.hospital_phone,
                'role': hospital_doc.role,
                'password': hospital_doc.password,
            }, status=status.HTTP_200_OK)

        # --- Normal User Login ---
        user = Register.objects.filter(email=email, password=password).first()
        if user:
            return Response({
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'password': user.password,
                'phone':user.phone,
                'role': user.role
            }, status=status.HTTP_200_OK)

        # --- Invalid Credentials ---
        return Response({'message': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)


#  Hospital Doctor ViewSet
class HospitalDoctorRegisterViewSet(viewsets.ModelViewSet):
    queryset = tbl_hospital_doctor_register.objects.all()
    serializer_class = HospitalDoctorRegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    











# views.py
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from django.conf import settings
import joblib
import numpy as np
import os

from .models import DepressionPrediction
from .serializers import DepressionPredictionSerializer
from userapp.encoding_map import ENCODING

MODEL_PATH = os.path.join(settings.BASE_DIR, "userapp/ml_assets/rf_model.joblib")
ENCODER_PATH = os.path.join(settings.BASE_DIR, "userapp/ml_assets/label_encoder.joblib")

pipeline = joblib.load(MODEL_PATH)
label_encoder = joblib.load(ENCODER_PATH)
# print("Label Encoder Classes:", label_encoder.classes_)

LABEL_MAP = {
    0: "Bipolar Type-2",
    1: "Bipolar Type-2",
    2: "Depression",
    3: "Normal"
}

@api_view(['POST'])
def depression_predict(request):

    try:
        fields = [
            "sadness", "euphoric", "exhausted", "sleep_disorder",
            "mood_swing", "suicidal_thoughts", "anorexia",
            "authority_respect", "try_explanation", "aggressive_response",
            "ignore_move_on", "nervous_breakdown", "admit_mistakes", "overthinking"
        ]

        encoded_values = []
        for f in fields:
            val = request.data.get(f)
            if val is None:
                return Response({"error": f"{f} is required"}, status=400)

            encoded_values.append(ENCODING.get(val.lower(), 0))

        input_array = np.array([encoded_values])

        pred_encoded = pipeline.predict(input_array)
        pred_value = int(pred_encoded[0])

        # Manual mapping
        pred_label = LABEL_MAP.get(pred_value, f"Unknown class: {pred_value}")

        serializer = DepressionPredictionSerializer(data={
            **request.data,
            "prediction_result": pred_label
        })

        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": "success",
                "prediction": pred_label,
                "data": serializer.data
            }, status=201)   
        return Response(serializer.errors, status=400)

    except Exception as e:
        return Response({"error": str(e)}, status=500)

from userapp.adhd_encoding import ADHD_ENCODING

gender_map = {
    "Male": 0,
    "Female": 1,
    "Other": 2
}

@api_view(['POST'])
def adhd_predict(request):

    try:
        # ML FILE PATHS (UPDATED)
        model_path = os.path.join(settings.BASE_DIR, "sereneapp/ml_assets/adhd_model1.pkl")
        scaler_path = os.path.join(settings.BASE_DIR, "sereneapp/ml_assets/scaler1.pkl")
        gender_encoder_path = os.path.join(settings.BASE_DIR, "sereneapp/ml_assets/gender_encoder1.pkl")

        # Load ML components
        model = joblib.load(model_path)
        scaler = joblib.load(scaler_path)
        gender_encoder = joblib.load(gender_encoder_path)

        data = request.data

        # Gender mapping
        gender_value = gender_map.get(data["gender"], 2)

        # Convert text → integer using ADHD_ENCODING
        easily = ADHD_ENCODING[data["easily_distracted"].lower()]
        forget = ADHD_ENCODING[data["forgetful_daily_tasks"].lower()]
        poor_org = ADHD_ENCODING[data["poor_organization"].lower()]
        diff = ADHD_ENCODING[data["difficulty_sustaining_attention"].lower()]
        restless = ADHD_ENCODING[data["restlessness"].lower()]
        impulsive = ADHD_ENCODING[data["impulsivity_score"].lower()]

        # Symptom scoring
        symptom_score = easily + forget + poor_org + diff + restless + impulsive

        # ML Input Array
        input_features = np.array([[
            int(data["age"]),
            gender_value,
            float(data["sleep_hour_avg"]),
            easily,
            forget,
            poor_org,
            diff,
            restless,
            impulsive,
            float(data["screen_time_daily"]),
            int(data["phone_unlocks_per_day"]),
            int(data["working_memory_score"])
        ]])

        # Scale input features
        scaled_input = scaler.transform(input_features)

        # Predict ADHD using ML model
        prediction = model.predict(scaled_input)[0]

        # Final output label
        adhd_result = "ADHD" if prediction == 1 else "No ADHD"

        # Data to save in DB
        save_data = {
            "user": data["user"],
            "age": data["age"],
            "gender": data["gender"],
            "sleep_hour_avg": data["sleep_hour_avg"],

            "easily_distracted": easily,
            "forgetful_daily_tasks": forget,
            "poor_organization": poor_org,
            "difficulty_sustaining_attention": diff,
            "restlessness": restless,
            "impulsivity_score": impulsive,

            "screen_time_daily": data["screen_time_daily"],
            "phone_unlocks_per_day": data["phone_unlocks_per_day"],
            "working_memory_score": data["working_memory_score"],

            "symptom_score": symptom_score,
            "adhd_result": adhd_result,
        }

        serializer = ADHDPredictionSerializer(data=save_data)

        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": "success",
                "adhd_prediction": adhd_result,
                "symptom_score": symptom_score,
                "data": serializer.data
            }, status=201)

        return Response(serializer.errors, status=400)

    except Exception as e:
        return Response({"error": str(e)}, status=500)



