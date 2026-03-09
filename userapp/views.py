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

LABEL_MAP = {
    0: "Bipolar Type-1",
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
                return Response(
                    {"error": f"{f} is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            encoded_values.append(ENCODING.get(val.lower(), 0))

        # -------------------------------
        # ✅ NORMAL OVERRIDE LOGIC
        # -------------------------------
        # most-often = 0, seldom = 1
        # If ALL values are <= 1 → Normal
        if all(v <= 1 for v in encoded_values):
            pred_label = "Normal"
        else:
            input_array = np.array([encoded_values])
            pred_encoded = pipeline.predict(input_array)
            pred_value = int(pred_encoded[0])
            pred_label = LABEL_MAP.get(pred_value, "Unknown")

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
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# --- PORTED FROM FLASK app.py ---

ADV_MODEL_PATH = os.path.join(settings.BASE_DIR, "userapp/ml_assets/depression_model.pkl")
ADV_SCALER_PATH = os.path.join(settings.BASE_DIR, "userapp/ml_assets/scaler.pkl")

adv_model = joblib.load(ADV_MODEL_PATH)
adv_scaler = joblib.load(ADV_SCALER_PATH)

FEATURE_COLS = [
    "Gender", "Age", "Education_Level", "Employment_Status",
    "Depression_Type", "Symptoms", "Low_Energy", "Low_SelfEsteem",
    "Search_Depression_Online", "Worsening_Depression", "Your overeating level",
    "How many times you eat ", "SocialMedia_Hours", "SocialMedia_WhileEating",
    "Sleep_Hours", "Nervous_Level", "Depression_Score", "Coping_Methods",
    "Self_Harm", "Mental_Health_Support", "Suicide_Attempts",
    "Risk_Score", "Sleep_Deficit", "High_Nervousness",
    "Excessive_SocialMedia", "No_Support", "SocialMedia_x_Eating",
    "Nervousness_x_Energy", "Score_x_Nervous",
]

def engineer_features(data_dict):
    full = dict(data_dict)
    full["Risk_Score"] = (
        full.get("Low_Energy", 0)
        + full.get("Low_SelfEsteem", 0)
        + full.get("Worsening_Depression", 0)
        + full.get("Self_Harm", 0)
    )
    full["Sleep_Deficit"] = int(full.get("Sleep_Hours", 8) < 6)
    full["High_Nervousness"] = int(full.get("Nervous_Level", 0) >= 7)
    full["Excessive_SocialMedia"] = int(full.get("SocialMedia_Hours", 0) > 6)
    full["No_Support"] = int(full.get("Mental_Health_Support", 0) == 0)
    full["SocialMedia_x_Eating"] = full.get("SocialMedia_Hours", 0) * full.get("SocialMedia_WhileEating", 0)
    full["Nervousness_x_Energy"] = full.get("Nervous_Level", 0) * full.get("Low_Energy", 0)
    full["Score_x_Nervous"] = full.get("Depression_Score", 0) * full.get("Nervous_Level", 0)
    return full

RECOVERY_SUGGESTIONS = {
    "sleep": {
        "condition": lambda d: d.get("Sleep_Hours", 8) < 6,
        "title": "🛌 Improve Sleep Hygiene",
        "tips": ["Aim for 7-9 hours of sleep.", "Maintain a consistent schedule.", "Avoid screens before bed."]
    },
    "energy": {
        "condition": lambda d: d.get("Low_Energy", 0) == 1,
        "title": "⚡ Boost Energy Levels",
        "tips": ["Exercise daily.", "Eat balanced meals.", "Stay hydrated."]
    },
    "self_harm": {
        "condition": lambda d: d.get("Self_Harm", 0) == 1,
        "title": "🆘 SEEK IMMEDIATE SUPPORT",
        "tips": ["Reach out to a professional immediately.", "Contact AASRA (India): 9820466726."]
    },
    "general": {
        "condition": lambda d: True,
        "title": "🌟 General Well-being",
        "tips": ["Spend time outdoors.", "Connect with loved ones.", "Keep a positive mindset."]
    }
}

ADV_DEP_TYPE_MAP = {
    0: "Major Depressive Disorder", 1: "Persistent Depressive Disorder", 2: "Bipolar Disorder",
    3: "Cyclothymic Disorder", 4: "Postpartum Depression", 5: "Premenstrual Dysphoric Disorder",
    6: "Seasonal Affective Disorder", 7: "Atypical Depression", 8: "Psychotic Depression",
    9: "Situational Depression", 10: "Melancholic Depression", 11: "Catatonic Depression"
}

import pandas as pd

class AdvancedDepressionPredictView(APIView):
    def post(self, request):
        try:
            data = request.data
            full_data = engineer_features(data)
            
            input_df = pd.DataFrame([full_data])
            input_scaled = adv_scaler.transform(input_df[FEATURE_COLS])
            
            prob = adv_model.predict_proba(input_scaled)[0][1]
            is_depressed = prob >= 0.5
            
            active_suggestions = []
            for s in RECOVERY_SUGGESTIONS.values():
                if s["condition"](full_data):
                    active_suggestions.append({
                        "title": s["title"],
                        "tips": s["tips"]
                    })
            
            potential_type = ADV_DEP_TYPE_MAP.get(full_data.get("Depression_Type", 0), "None")
            
            prediction_label = potential_type if is_depressed else "None"
            
            # Map underscores to spaces for model mapping if needed, or just use raw data
            save_data = {
                "user": data.get("user"),
                "gender": data.get("Gender"),
                "age": data.get("Age"),
                "education_level": data.get("Education_Level"),
                "employment_status": data.get("Employment_Status"),
                "depression_type": data.get("Depression_Type"),
                "symptoms": data.get("Symptoms"),
                "low_energy": data.get("Low_Energy"),
                "low_self_esteem": data.get("Low_SelfEsteem"),
                "search_depression_online": data.get("Search_Depression_Online"),
                "worsening_depression": data.get("Worsening_Depression"),
                "overeating_level": data.get("Your overeating level"),
                "eating_frequency": data.get("How many times you eat "),
                "social_media_hours": data.get("SocialMedia_Hours"),
                "social_media_while_eating": data.get("SocialMedia_WhileEating"),
                "sleep_hours": data.get("Sleep_Hours"),
                "nervous_level": data.get("Nervous_Level"),
                "depression_score": data.get("Depression_Score"),
                "coping_methods": data.get("Coping_Methods"),
                "self_harm": data.get("Self_Harm"),
                "mental_health_support": data.get("Mental_Health_Support"),
                "suicide_attempts": data.get("Suicide_Attempts"),
                
                "is_depressed": bool(is_depressed),
                "probability": float(prob),
                "potential_type": prediction_label,
                "suggestions": active_suggestions
            }
            
            serializer = AdvancedDepressionPredictionSerializer(data=save_data)
            if serializer.is_valid():
                serializer.save()
                return Response({
                    "status": "success",
                    "is_depressed": bool(is_depressed),
                    "probability": float(prob),
                    "potential_type": prediction_label,
                    "suggestions": active_suggestions,
                    "id": serializer.data.get("id")
                }, status=status.HTTP_201_CREATED)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
        model_path = os.path.join(settings.BASE_DIR, "userapp/ml_assets/adhd_model1.pkl")
        scaler_path = os.path.join(settings.BASE_DIR, "userapp/ml_assets/scaler1.pkl")
        gender_encoder_path = os.path.join(settings.BASE_DIR, "userapp/ml_assets/gender_encoder1.pkl")

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





@api_view(['GET'])
def view_hospital_doctor_profile(request, doctor_id):
    try:
        doctor = tbl_hospital_doctor_register.objects.get(id=doctor_id)
    except tbl_hospital_doctor_register.DoesNotExist:
        return Response({'error': 'Doctor not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = HospitalDoctorRegisterSerializer(doctor)
    return Response(serializer.data, status=status.HTTP_200_OK)




class HospitalDoctorProfileViewSet(viewsets.ViewSet):
    """
    A ViewSet for updating hospital doctor profiles (partial or full updates).
    """

    def partial_update(self, request, pk=None):
        try:
            doctor = tbl_hospital_doctor_register.objects.get(pk=pk)
        except tbl_hospital_doctor_register.DoesNotExist:
            return Response({'error': 'Doctor not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = HospitalDoctorProfileUpdateSerializer(doctor, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Profile updated successfully', 'data': serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




from rest_framework import viewsets
from .models import HospitalDoctorTimeSlotGroup
from .serializers import HospitalDoctorTimeSlotGroupSerializer

class HospitalDoctorTimeSlotGroupViewSet(viewsets.ModelViewSet):
    queryset = HospitalDoctorTimeSlotGroup.objects.all().order_by('-date')
    serializer_class = HospitalDoctorTimeSlotGroupSerializer







# ✅ View all available hospital doctor time slots
@api_view(['GET'])
def view_hospital_doctor_timeslots(request, doctor_id):
    """
    Get all time slot groups for a hospital doctor with booking info.
    """
    try:
        groups = HospitalDoctorTimeSlotGroup.objects.filter(doctor_id=doctor_id).order_by('date')

        if not groups.exists():
            return Response({"message": "No time slots found for this doctor."}, status=status.HTTP_404_NOT_FOUND)

        result = []
        for group in groups:
            # ✅ Already booked times for that date
            booked_times = list(
                HospitalBooking.objects.filter(
                    doctor_id=doctor_id,
                    date=group.date
                ).values_list('time', flat=True)
            )

            # Normalize booked times (e.g. "10:00:00" → "10:00")
            booked_times = [t[:5] for t in booked_times]

            result.append({
                "id": group.id,
                "doctor": group.doctor.id,
                "doctor_name": group.doctor.name,
                "date": group.date,
                "start_time": group.start_time.strftime("%H:%M:%S"),
                "end_time": group.end_time.strftime("%H:%M:%S"),
                "timeslots": [
                    {"time": t, "is_booked": t in booked_times}
                    for t in group.timeslots
                ],
            })

        return Response(result, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)







@api_view(['POST'])
def update_hospital_doctor_availability(request, doctor_id):
    try:
        doctor = tbl_hospital_doctor_register.objects.get(id=doctor_id)
    except tbl_hospital_doctor_register.DoesNotExist:
        return Response({"error": "Doctor not found"}, status=status.HTTP_404_NOT_FOUND)
    
    available = request.data.get('available')

    if available is None:
        return Response({"error": "Availability value required (true/false)"}, status=status.HTTP_400_BAD_REQUEST)

    # Convert to boolean
    if isinstance(available, str):
        available = available.lower() in ['true', '1', 'yes']

    doctor.available = available
    doctor.save()

    return Response({
        "message": "Availability updated successfully",
        "doctor_id": doctor.id,
        "available": doctor.available
    }, status=status.HTTP_200_OK)




@api_view(['GET'])
def view_nearby_hospital_doctors(request, user_id):
    """
    Get all approved and available hospital doctors 
    who are in the same place as the user.
    """
    try:
        user = Register.objects.get(id=user_id)
    except Register.DoesNotExist:
        return Response({"error": "User not found"}, status=404)

    if not user.place:
        return Response({"error": "User place not available"}, status=400)

    # ✅ Only approved & available doctors
    doctors = tbl_hospital_doctor_register.objects.filter(
        status='approved', available=True
    )
    
    # Try filtering by place first
    nearby_doctors_query = doctors.filter(place__iexact=user.place)
    
    if nearby_doctors_query.exists():
        doctors_to_show = nearby_doctors_query
    else:
        # Fallback: Show all approved/available if none in the specific place
        doctors_to_show = doctors

    if not doctors_to_show.exists():
        return Response({"message": "No hospital doctors found."}, status=200)

    nearby_doctors = []
    for doctor in doctors_to_show:
        nearby_doctors.append({
            "id": doctor.id,
            "name": doctor.name,
            "qualification": doctor.qualification,
            "specialization": doctor.specialization,
            "experience": doctor.experience,
            "phone": doctor.hospital_phone,
            "hospital_name": doctor.hospital_name,
            "hospital_address": doctor.hospital_address,
            "place": doctor.place,
            "available": doctor.available,
            "image": doctor.image.url if doctor.image else None,
            "status": doctor.status,
        })

    return Response({"nearby_hospital_doctors": nearby_doctors})




# ✅ Book a hospital doctor time slot (same logic as clinic)
@api_view(['POST'])
def book_hospital_doctor_slot(request):
    """
    Book a specific time slot for a hospital doctor.

    Expected JSON:
    {
        "user": 1,
        "doctor": 3,
        "timeslot_group": 5,
        "date": "2025-11-01",
        "time": "09:30"
    }
    """
    data = request.data

    try:
        user = Register.objects.get(id=data['user'])
        doctor = tbl_hospital_doctor_register.objects.get(id=data['doctor'])
        timeslot_group = HospitalDoctorTimeSlotGroup.objects.get(id=data['timeslot_group'])
    except (Register.DoesNotExist, tbl_hospital_doctor_register.DoesNotExist, HospitalDoctorTimeSlotGroup.DoesNotExist):
        return Response({"error": "Invalid doctor, user, or timeslot group."}, status=404)

    # ✅ Check if time is in available slots
    timeslots = timeslot_group.timeslots
    if data['time'] not in timeslots:
        return Response({"error": "Invalid time slot."}, status=400)

    # ✅ Check if already booked
    if HospitalBooking.objects.filter(
        doctor=doctor,
        date=data['date'],
        time=data['time'],
        is_booked=True
    ).exists():
        return Response({"error": "This time slot is already booked."}, status=400)

    # ✅ Create booking
    booking = HospitalBooking.objects.create(
        user=user,
        doctor=doctor,
        timeslot_group=timeslot_group,
        date=data['date'],
        time=data['time'],
        is_booked=True
    )

    return Response({
        "message": "Slot booked successfully!",
        "booking_id": booking.id,
        "doctor": doctor.name,
        "date": data['date'],
        "time": data['time']
    }, status=201)



# 🧠 User Adds Feedback
@api_view(['POST'])
def add_hospital_doctor_feedback(request):
    user_id = request.data.get('user')
    doctor_id = request.data.get('doctor')
    booking_id = request.data.get('booking')
    rating = request.data.get('rating')
    tension_free_level = request.data.get('tension_free_level', 0)
    comments = request.data.get('comments', '')

    try:
        user = Register.objects.get(id=user_id)
        doctor = tbl_hospital_doctor_register.objects.get(id=doctor_id)
        booking = None
        if booking_id:
            booking = HospitalBooking.objects.get(id=booking_id)
    except (Register.DoesNotExist, tbl_hospital_doctor_register.DoesNotExist, HospitalBooking.DoesNotExist):
        return Response({'error': 'Invalid user, doctor, or booking ID'}, status=status.HTTP_404_NOT_FOUND)

    feedback = HospitalDoctorFeedback.objects.create(
        user=user, 
        doctor=doctor, 
        booking=booking,
        rating=rating, 
        tension_free_level=tension_free_level,
        comments=comments
    )
    serializer = HospitalDoctorFeedbackSerializer(feedback)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


# 🧠 Doctor Views Feedback
@api_view(['GET'])
def view_hospital_doctor_feedback(request, doctor_id):
    feedbacks = HospitalDoctorFeedback.objects.filter(doctor_id=doctor_id).order_by('-created_at')
    serializer = HospitalDoctorFeedbackSerializer(feedbacks, many=True)
    return Response(serializer.data)



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import HospitalDoctorFeedback
from .serializers import HospitalDoctorFeedbackSerializer


class GetDoctorFeedbackAPI(APIView):
    def get(self, request, doctor_id):
        try:
            feedbacks = HospitalDoctorFeedback.objects.filter(doctor_id=doctor_id)

            if not feedbacks.exists():
                return Response({"message": "No feedback found for this doctor."}, status=404)

            serializer = HospitalDoctorFeedbackSerializer(feedbacks, many=True)
            return Response(serializer.data, status=200)

        except Exception as e:
            return Response({"error": str(e)}, status=400)




class user_view_booking_hospital(APIView):
    def get(self, request, user_id):
        bookings = HospitalBooking.objects.filter(user_id=user_id)
        data = []
        for booking in bookings:
            data.append({
                "id": booking.id,
                "doctor": booking.doctor.id if booking.doctor else None,
                "doctor_name": booking.doctor.name if booking.doctor else "Doctor removed",
                "patient": booking.user.id,
                "patient_name": booking.user.name if booking.user else "User removed",
                "date": booking.date,
                "time": booking.time,
                # "booked_at": getattr(booking, 'created_at', None),
            })
        return Response(data, status=status.HTTP_200_OK)


class doctor_view_booking_hospital(APIView):
    def get(self, request, doctor_id):
        bookings = HospitalBooking.objects.filter(doctor_id=doctor_id)
        data = []
        for booking in bookings:
            data.append({
                "id": booking.id,
                "user": booking.user.id,
                "user_name": booking.user.name,
                "date": booking.date,
                "time": booking.time,
                "status": booking.status,
                # "booked_at": booking.created_at,
            })
        return Response(data, status=status.HTTP_200_OK)

@api_view(['POST'])
def update_hospital_booking_status(request, booking_id):
    try:
        booking = HospitalBooking.objects.get(id=booking_id)
        new_status = request.data.get('status')
        if new_status not in ['approved', 'rejected']:
            return Response({'message': 'Invalid status. Use "approved" or "rejected".'}, status=status.HTTP_400_BAD_REQUEST)
        
        booking.status = new_status
        booking.save()
        return Response({'message': f'Booking {new_status} successfully'}, status=status.HTTP_200_OK)
    except HospitalBooking.DoesNotExist:
        return Response({'message': 'Booking not found'}, status=status.HTTP_404_NOT_FOUND)
    

class UserViewBook(APIView):
    def get(self, request, *args, **kwargs):
        books = Book.objects.all()
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from google import genai
import os
from dotenv import load_dotenv
from django.conf import settings

# -----------------------------
# Load environment variables
# -----------------------------
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("[ERROR] GOOGLE_API_KEY not found in .env file")

# -----------------------------
# Configure Gemini Client
# -----------------------------
client = genai.Client(api_key=settings.GOOGLE_API_KEY)

# -----------------------------
# Keywords
# -----------------------------

DEPRESSION_KEYWORDS = [
    "depression", "depressed", "sad", "sadness", "hopeless", "worthless",
    "lonely", "anxiety", "panic", "stress", "overthinking", "mental health",
    "mood swings", "crying", "low mood", "tired", "fatigue", "exhausted",
    "sleep disorder", "insomnia", "oversleeping",
    "loss of interest", "no motivation", "burnout",
    "self hate", "guilt", "shame",
    "therapy", "counselling", "psychologist", "psychiatrist",
    "antidepressant", "medicine", "treatment", "healing",
    "bipolar", "bipolar-type 1", "bipolar-type 2",
    "manic depression", "cyclothymic disorder",
    "bipolartype1", "bipolartype2", "bipolar-type-1", "bipolar-type-2"
]

CRISIS_KEYWORDS = [
    "kill myself", "end my life", "suicide", "self harm",
    "hurt myself", "no reason to live", "die"
]

GREETINGS = ["hi", "hello", "hey", "morning", "evening", "afternoon"]

# -----------------------------
# Chatbot API
# -----------------------------

class ChatbotAPIView(APIView):

    def post(self, request):
        user_message = request.data.get("message", "").strip()

        if not user_message:
            return Response({
                "type": "error",
                "reply": "Message cannot be empty."
            }, status=status.HTTP_400_BAD_REQUEST)

        user_message_lower = user_message.lower()
        user_words = user_message_lower.split()

        # 🚨 Crisis check (highest priority)
        if any(word in user_message_lower for word in CRISIS_KEYWORDS):
            return Response({
                "type": "crisis",
                "reply": (
                    "I'm really sorry that you're feeling this way 💔.\n"
                    "You’re not alone, and help is available.\n\n"
                    "Please reach out to someone you trust or a mental health professional.\n\n"
                    "📞 India Suicide Prevention Helpline: 9152987821\n"
                    "📞 AASRA: 91-22-27546669\n\n"
                    "If you’re in immediate danger, please contact emergency services right now."
                )
            })

        # ✅ Depression-related message
        if any(keyword in user_message_lower for keyword in DEPRESSION_KEYWORDS):

            try:
                prompt = f"""
You are a compassionate mental health support assistant focused on depression.
Respond empathetically and calmly.
Do NOT diagnose or prescribe medication.
Encourage healthy coping strategies and seeking professional help when needed.

User message: {user_message}
"""

                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )

                return Response({
                    "type": "mental_health_support",
                    "reply": response.text
                })

            except Exception as e:
                return Response({
                    "type": "error",
                    "reply": str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # 👋 Greeting
        if any(greet in user_words for greet in GREETINGS):
            return Response({
                "type": "greeting",
                "reply": (
                    "Hello 💙 I'm here to support you. "
                    "You can talk to me about stress, anxiety, sadness, or anything related to depression."
                )
            })

        # ❌ Not related
        return Response({
            "type": "not_related",
            "reply": (
                "I’m here to help with mental health topics like depression, stress, and emotional well-being."
            )
        })

import os
from dotenv import load_dotenv
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from google import genai

load_dotenv()

# Gemini configuration
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
MODEL_NAME = "models/gemini-flash-latest"


class TimetableAPIView(APIView):
    def post(self, request):
        user_input = request.data.get("message")

        if not user_input:
            return Response(
                {"error": "Message is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        prompt = f"""
You are an expert academic planner.

Create a DAILY STUDY TIMETABLE in MARKDOWN TABLE format.

Strict rules:
- Output ONLY the table (no text before or after)
- Columns must be exactly: Time | Activity | Subject
- Balanced schedule with breaks
- Allocate more study time to difficult subjects
- Realistic time slots

Student details:
{user_input}
"""

        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt
            )

            reply = response.candidates[0].content.parts[0].text

            return Response(
                {"reply": reply},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )