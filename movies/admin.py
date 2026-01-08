from django.contrib import admin
from .models import Movie, Theater, Seat, Booking


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('name', 'genre', 'language', 'rating')
    list_filter = ('genre', 'language')
    search_fields = ('name', 'cast')

    fields = (
        'name',
        'image',
        'rating',
        'genre',
        'language',
        'trailer_url',   # 🎬 ADD THIS
        'cast',
        'description',
    )


@admin.register(Theater)
class TheaterAdmin(admin.ModelAdmin):
    list_display = ('name', 'movie', 'time')


@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ('seat_number', 'theater', 'is_booked')


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'movie', 'theater', 'seat', 'booked_at')
