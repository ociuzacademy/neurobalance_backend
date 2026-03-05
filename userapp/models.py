from django.db import models

# Create your models here.

class Register(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    password = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    age = models.IntegerField()
    place = models.CharField(max_length=100, null=True, blank=True)
    latitude = models.DecimalField(max_digits=11, decimal_places=9, null=True, blank=True)
    longitude = models.DecimalField(max_digits=11, decimal_places=9, null=True, blank=True)
    role = models.CharField(max_length=50, default='user')

    def __str__(self):
        return self.name


# models.py
from django.db import models
from .models import Register  # your user table

class DepressionPrediction(models.Model):
    user = models.ForeignKey(Register, on_delete=models.CASCADE)

    sadness = models.CharField(max_length=20)
    euphoric = models.CharField(max_length=20)
    exhausted = models.CharField(max_length=20)
    sleep_disorder = models.CharField(max_length=20)
    mood_swing = models.CharField(max_length=20)
    suicidal_thoughts = models.CharField(max_length=20)
    anorexia = models.CharField(max_length=20)
    authority_respect = models.CharField(max_length=20)
    try_explanation = models.CharField(max_length=20)
    aggressive_response = models.CharField(max_length=20)
    ignore_move_on = models.CharField(max_length=20)
    nervous_breakdown = models.CharField(max_length=20)
    admit_mistakes = models.CharField(max_length=20)
    overthinking = models.CharField(max_length=20)

    prediction_result = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.name} - {self.prediction_result}"

class AdvancedDepressionPrediction(models.Model):
    user = models.ForeignKey(Register, on_delete=models.CASCADE)
    
    gender = models.IntegerField()
    age = models.FloatField()
    education_level = models.IntegerField()
    employment_status = models.IntegerField()
    depression_type = models.IntegerField()
    symptoms = models.IntegerField()
    low_energy = models.IntegerField()
    low_self_esteem = models.IntegerField()
    search_depression_online = models.IntegerField()
    worsening_depression = models.IntegerField()
    overeating_level = models.FloatField()
    eating_frequency = models.IntegerField()
    social_media_hours = models.FloatField()
    social_media_while_eating = models.IntegerField()
    sleep_hours = models.FloatField()
    nervous_level = models.FloatField()
    depression_score = models.FloatField()
    coping_methods = models.IntegerField()
    self_harm = models.IntegerField()
    mental_health_support = models.IntegerField()
    suicide_attempts = models.FloatField()
    
    is_depressed = models.BooleanField()
    probability = models.FloatField()
    potential_type = models.CharField(max_length=100)
    suggestions = models.JSONField()
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.name} - {self.potential_type} ({self.probability})"



class ADHDPrediction(models.Model):
    user = models.ForeignKey(Register, on_delete=models.CASCADE)

    age = models.IntegerField()
    gender = models.CharField(max_length=10)  # Male/Female/Other
    sleep_hour_avg = models.FloatField()

    easily_distracted = models.IntegerField()
    forgetful_daily_tasks = models.IntegerField()
    poor_organization = models.IntegerField()
    difficulty_sustaining_attention = models.IntegerField()
    restlessness = models.IntegerField()
    impulsivity_score = models.IntegerField()

    screen_time_daily = models.FloatField()
    phone_unlocks_per_day = models.IntegerField()
    working_memory_score = models.IntegerField()

    symptom_score = models.IntegerField()
    adhd_result = models.CharField(max_length=50)  # ADHD / No ADHD

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.name} - {self.adhd_result}"






# ✅ Hospital Doctor Model
class tbl_hospital_doctor_register(models.Model):
    status_choices = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, unique=True)
    password = models.CharField(max_length=100)
    qualification = models.CharField(max_length=100, null=True, blank=True)
    specialization = models.CharField(max_length=100, null=True, blank=True)
    experience = models.IntegerField(null=True, blank=True)
    hospital_name = models.CharField(max_length=100, null=True, blank=True)
    hospital_address = models.TextField(null=True, blank=True)
    hospital_phone = models.CharField(max_length=15, null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    role = models.CharField(max_length=30, default='hospital_doctor')
    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=10, null=True, blank=True)
    place = models.CharField(max_length=100, null=True, blank=True)
    image = models.ImageField(upload_to='hospital_doctor_images/', null=True, blank=True)
    medical_id = models.ImageField(upload_to='hospital_medical_ids/', null=True, blank=True)
    available = models.BooleanField(default=True)
    status = models.CharField(max_length=20, choices=status_choices, default='pending')

    def __str__(self):
        return self.name









class HospitalDoctorTimeSlotGroup(models.Model):
    doctor = models.ForeignKey('tbl_hospital_doctor_register', on_delete=models.CASCADE, related_name='slot_groups')
    date = models.DateField()
    start_time = models.TimeField()   # doctor’s working start time
    end_time = models.TimeField()     # doctor’s working end time
    timeslots = models.JSONField(default=list, blank=True)  # ✅ store list of selected times

    def __str__(self):
        return f"{self.doctor.name} - {self.date} ({self.start_time} to {self.end_time})"





class HospitalBooking(models.Model):
    user = models.ForeignKey(Register, on_delete=models.CASCADE)
    doctor = models.ForeignKey(tbl_hospital_doctor_register, on_delete=models.SET_NULL, null=True, blank=True)
    timeslot_group = models.ForeignKey(HospitalDoctorTimeSlotGroup, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.CharField(max_length=20)
    status = models.CharField(max_length=20, default='booked')
    is_booked = models.BooleanField(default=True)

    def __str__(self):
        if self.doctor:
            return f"{self.user.name} booked {self.doctor.name} at {self.time} on {self.date}"
        return f"{self.user.name} booked (Doctor deleted) at {self.time} on {self.date}"






class HospitalDoctorFeedback(models.Model):
    user = models.ForeignKey(Register, on_delete=models.CASCADE, related_name='hospital_feedbacks')
    doctor = models.ForeignKey('tbl_hospital_doctor_register', on_delete=models.CASCADE, related_name='hospital_feedbacks')
    rating = models.IntegerField()  # e.g., 1–5 stars
    comments = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback by {self.user.name} for {self.doctor.name}"


