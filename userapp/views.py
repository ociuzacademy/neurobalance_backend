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

    # ✅ Only approved & available doctors in the same place
    doctors = tbl_hospital_doctor_register.objects.filter(
        status='approved', available=True, place__iexact=user.place
    )

    if not doctors.exists():
        return Response({"message": "No nearby hospital doctors found in your area."}, status=200)

    nearby_doctors = []
    for doctor in doctors:
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
    rating = request.data.get('rating')
    comments = request.data.get('comments', '')

    try:
        user = Register.objects.get(id=user_id)
        doctor = tbl_hospital_doctor_register.objects.get(id=doctor_id)
    except (Register.DoesNotExist, tbl_hospital_doctor_register.DoesNotExist):
        return Response({'error': 'Invalid user or doctor ID'}, status=status.HTTP_404_NOT_FOUND)

    feedback = HospitalDoctorFeedback.objects.create(
        user=user, doctor=doctor, rating=rating, comments=comments
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
    

class UserViewBook(APIView):
    def get(self, request, *args, **kwargs):
        books = Book.objects.all()
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data)

