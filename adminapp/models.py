from django.db import models

# Create your models here.
class Admin(models.Model):
    username = models.CharField(max_length=100)
    email = models.EmailField()
    password = models.CharField(max_length=100)

    def __str__(self):
        return self.username




class Book(models.Model):
    title = models.CharField(max_length=255)              # Book title
    author = models.CharField(max_length=255, blank=True) # Author
    description = models.TextField(blank=True, null=True) # Summary
    category = models.CharField(max_length=100, default="Menstrual Health")
    publisher = models.CharField(max_length=255, blank=True, null=True)
    publication_date = models.DateField(blank=True, null=True)
    cover_image = models.ImageField(upload_to="book_covers/", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
