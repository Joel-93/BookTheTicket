from django.db import models
from django.contrib.auth.models import User
import re
from django.utils import timezone
from datetime import timedelta

class Movie(models.Model):
    GENRE_CHOICES = [
        ('Action', 'Action'),
        ('Comedy', 'Comedy'),
        ('Drama', 'Drama'),
        ('Romance', 'Romance'),
        ('Thriller', 'Thriller'),
    ]

    LANGUAGE_CHOICES = [
        ('English', 'English'),
        ('Hindi', 'Hindi'),
        ('Tamil', 'Tamil'),
        ('Telugu', 'Telugu'),
    ]

    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='movies/')
    rating = models.DecimalField(max_digits=3, decimal_places=1)
    cast = models.TextField()
    description = models.TextField()

    genre = models.CharField(max_length=50, choices=GENRE_CHOICES)
    language = models.CharField(max_length=50, choices=LANGUAGE_CHOICES)

    # 🎬 YouTube Trailer URL
    trailer_url = models.URLField(
        blank=True,
        help_text="Paste any YouTube trailer link"
    )

    def __str__(self):
        return self.name

    # ✅ SAFE YouTube embed URL generator
    def get_trailer_embed_url(self):
        if not self.trailer_url:
            return ""

        match = re.search(
            r"(?:v=|youtu\.be/)([^&?/]+)",
            self.trailer_url
        )

        if not match:
            return ""

        video_id = match.group(1)

        return (
            f"https://www.youtube-nocookie.com/embed/{video_id}"
            f"?rel=0&modestbranding=1"
        )


class Theater(models.Model):
    name = models.CharField(max_length=225)
    movie = models.ForeignKey(
        Movie,
        on_delete=models.CASCADE,
        related_name='theaters'
    )
    time = models.TimeField()

    def __str__(self):
        return f"{self.name} - {self.movie.name} at {self.time}"


class Seat(models.Model):
    theater = models.ForeignKey(
        Theater,
        on_delete=models.CASCADE,
        related_name='seats'
    )
    seat_number = models.CharField(max_length=10)
    time = models.TimeField()

    # FINAL STATES
    is_booked = models.BooleanField(default=False)

    # 🔐 TEMP RESERVATION
    reserved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    reserved_until = models.DateTimeField(null=True, blank=True)

    def is_reserved(self):
        if self.reserved_until and self.reserved_until > timezone.now():
            return True
        return False

    def release_if_expired(self):
        if self.reserved_until and self.reserved_until <= timezone.now():
            self.reserved_by = None
            self.reserved_until = None
            self.save()

    def __str__(self):
        return f"{self.seat_number} - {self.theater.movie.name}"


class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    seat = models.OneToOneField(Seat, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    theater = models.ForeignKey(Theater, on_delete=models.CASCADE)
    booked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.movie.name}"
