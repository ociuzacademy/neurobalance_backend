from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .models import Admin
from userapp.models import  Register
from django.shortcuts import get_object_or_404
# Create your views here.
@require_http_methods(["GET", "POST"])
def admin_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        try:
            admin = Admin.objects.get(username=username, password=password)
            request.session['admin_id'] = admin.id
            request.session['admin_username'] = admin.username
            messages.success(request, f"Welcome, {admin.username}!")
            return redirect('admin_dashboard')
        except Admin.DoesNotExist:
            messages.error(request, "Invalid username or password")
    
    return render(request, 'login.html')

from django.shortcuts import render, redirect
from userapp.models import (
    Register,
    ADHDPrediction,
    DepressionPrediction,
    tbl_hospital_doctor_register,
    HospitalBooking
)

def admin_dashboard(request):
    if 'admin_id' not in request.session:
        return redirect('admin_login')

    context = {
        # OVERVIEW COUNTS
        "total_users": Register.objects.filter(role='user').count(),
        "total_bookings": HospitalBooking.objects.count(),
        "adhd_predictions": ADHDPrediction.objects.count(),
        "depression_predictions": DepressionPrediction.objects.count(),

        # DOCTOR COUNTS
        "pending_doctors_count": tbl_hospital_doctor_register.objects.filter(status='pending').count(),
        "approved_doctors_count": tbl_hospital_doctor_register.objects.filter(status='approved').count(),
        "rejected_doctors_count": tbl_hospital_doctor_register.objects.filter(status='rejected').count(),

        # TABLE DATA
        "users": Register.objects.filter(role='user').order_by('-id'),
        "pending_doctors": tbl_hospital_doctor_register.objects.filter(status='pending'),
        "approved_doctors": tbl_hospital_doctor_register.objects.filter(status='approved'),
        "rejected_doctors": tbl_hospital_doctor_register.objects.filter(status='rejected'),
        "bookings": HospitalBooking.objects.select_related('user', 'doctor').order_by('-date'),
        "total_books": Book.objects.count(),
    }

    return render(request, 'admin_dashboard.html', context)

def admin_logout(request):
    request.session.flush()
    messages.success(request, "Logged out successfully!")
    return redirect('admin_login')




def view_users(request):
    users = Register.objects.all()
    return render(request, 'view_users.html', {'users': users})

def delete_user(request, user_id):
    user = get_object_or_404(Register, id=user_id)
    user.delete()
    return redirect('view_users')



from django.shortcuts import render
from userapp.models import  tbl_hospital_doctor_register
from django.shortcuts import render, redirect, get_object_or_404

# ✅ View all pending doctors
def view_pending_doctors(request):
    hospital_pending = tbl_hospital_doctor_register.objects.filter(status='pending')
    return render(request, 'pending_doctors.html', {
        'hospital_pending': hospital_pending
    })



# ✅ Approve hospital doctor
def approve_hospital_doctor(request, doctor_id):
    doctor = get_object_or_404(tbl_hospital_doctor_register, id=doctor_id)
    doctor.status = 'approved'
    doctor.save()
    return redirect('view_pending_doctors')


# ✅ Reject hospital doctor
def reject_hospital_doctor(request, doctor_id):
    doctor = get_object_or_404(tbl_hospital_doctor_register, id=doctor_id)
    doctor.status = 'rejected'
    doctor.save()
    return redirect('view_pending_doctors')



def view_approved_doctors(request):
   
    hospital_approved = tbl_hospital_doctor_register.objects.filter(status='approved')
    return render(request, 'approved_doctors.html', {
        
        'hospital_approved': hospital_approved
    })


def view_rejected_doctors(request):
    hospital_rejected = tbl_hospital_doctor_register.objects.filter(status='rejected')
    return render(request, 'rejected_doctors.html', {
        'hospital_rejected': hospital_rejected
    })




def admin_view_hospital_bookings(request):
    hospital_bookings = (
        HospitalBooking.objects
        .select_related('user', 'doctor')
        
        .order_by('-date', '-id')
    )

    return render(request, 'view_all_bookings.html', {
        'hospital_bookings': hospital_bookings
    })







from django.shortcuts import render, redirect, get_object_or_404
from .models import Book

#  Add Book
def add_book(request):
    if request.method == "POST":
        title = request.POST.get("title")
        author = request.POST.get("author")
        description = request.POST.get("description")
        category = request.POST.get("category")
        publisher = request.POST.get("publisher")
        publication_date = request.POST.get("publication_date")
        cover_image = request.FILES.get("cover_image")

        Book.objects.create(
            title=title,
            author=author,
            description=description,
            category=category,
            publisher=publisher,
            publication_date=publication_date if publication_date else None,
            cover_image=cover_image
        )
        return redirect("view_books")
    return render(request, "add_book.html")


#  List Books
def view_books(request):
    category = request.GET.get('category')

    books = Book.objects.all()

    if category:
        books = books.filter(category=category)

    categories = Book.objects.values_list('category', flat=True).distinct()

    return render(request, 'view_books.html', {
        'books': books,
        'categories': categories,
        'selected_category': category,
    })



#  Edit Book
def edit_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == "POST":
        book.title = request.POST.get("title")
        book.author = request.POST.get("author")
        book.description = request.POST.get("description")
        book.category = request.POST.get("category")
        book.publisher = request.POST.get("publisher")
        book.publication_date = request.POST.get("publication_date")
        if request.FILES.get("cover_image"):
            book.cover_image = request.FILES.get("cover_image")
        book.save()
        return redirect("view_books")
    return render(request, "edit_book.html", {"book": book})


#  Delete Book
def delete_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    book.delete()
    return redirect("view_books")

