from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.utils import timezone
from datetime import timedelta
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count
from .models import Movie, Theater, Seat, Booking
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings



def movie_list(request):
    search_query = request.GET.get('search')
    genre = request.GET.get('genre')
    language = request.GET.get('language')

    movies = Movie.objects.all()

    if search_query:
        movies = movies.filter(name__icontains=search_query)

    if genre:
        movies = movies.filter(genre=genre)

    if language:
        movies = movies.filter(language=language)

    genres = ['Action', 'Comedy', 'Drama', 'Romance', 'Thriller']
    languages = ['English', 'Hindi', 'Tamil', 'Telugu']

    return render(
        request,
        'movies/movie_list.html',
        {
            'movies': movies,
            'genres': genres,
            'languages': languages,
            'selected_genre': genre,
            'selected_language': language,
        }
    )


def theater_list(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    theaters = Theater.objects.filter(movie=movie)

    return render(
        request,
        'movies/theater_list.html',
        {'movie': movie, 'theaters': theaters}
    )


@login_required(login_url='/users/login/')
def book_seats(request, theater_id):
    theater = get_object_or_404(Theater, id=theater_id)

    # 🔄 CLEAN EXPIRED RESERVATIONS
    seats = Seat.objects.filter(theater=theater)
    for seat in seats:
        seat.release_if_expired()

    if request.method == "POST":
        seat_ids = request.POST.getlist("seats")

        if not seat_ids:
            return render(
                request,
                "movies/seat_selection.html",
                {
                    "theater": theater,
                    "seats": seats,
                    "error": "Please select at least one seat."
                }
            )

        # 🔐 RESERVE SEATS FOR 5 MINUTES
        reserved_until = timezone.now() + timedelta(minutes=5)

        for seat_id in seat_ids:
            seat = get_object_or_404(Seat, id=seat_id, theater=theater)

            # ❌ BLOCK if already booked or reserved by someone else
            if seat.is_booked or (
                seat.is_reserved() and seat.reserved_by != request.user
            ):
                return render(
                    request,
                    "movies/seat_selection.html",
                    {
                        "theater": theater,
                        "seats": seats,
                        "error": "Some seats are no longer available."
                    }
                )

            seat.reserved_by = request.user
            seat.reserved_until = reserved_until
            seat.save()

        # ⏳ Store session for payment
        request.session["seat_ids"] = seat_ids
        request.session["theater_id"] = theater_id
        request.session["reservation_expires"] = reserved_until.isoformat()

        return redirect("payment_success")  # you can keep your Razorpay/Stripe stub

    return render(
        request,
        "movies/seat_selection.html",
        {
            "theater": theater,
            "seats": seats
        }
    )
@login_required
def payment_success(request):
    seat_ids = request.session.get("seat_ids")
    theater_id = request.session.get("theater_id")

    if not seat_ids or not theater_id:
        return redirect("movie_list")

    theater = get_object_or_404(Theater, id=theater_id)
    booked_seats = []

    for seat_id in seat_ids:
        seat = get_object_or_404(Seat, id=seat_id)

        # ❌ EXPIRED RESERVATION
        if not seat.is_reserved() or seat.reserved_by != request.user:
            continue

        Booking.objects.create(
            user=request.user,
            seat=seat,
            movie=theater.movie,
            theater=theater
        )

        seat.is_booked = True
        seat.reserved_by = None
        seat.reserved_until = None
        seat.save()

        booked_seats.append(seat.seat_number)

    # EMAIL (reuse your existing email logic)
    if booked_seats:
        subject = "🎟 Ticket Booking Confirmation"
        html = render_to_string("movies/booking_email.html", {
            "user": request.user,
            "movie": theater.movie,
            "theater": theater,
            "seats": ", ".join(booked_seats),
            "booking_date": timezone.now()

        })

        email = EmailMultiAlternatives(
            subject,
            "Booking Confirmed",
            settings.DEFAULT_FROM_EMAIL,
            [request.user.email],
        )
        email.attach_alternative(html, "text/html")
        email.send()

    return redirect("profile")


@staff_member_required
def admin_dashboard(request):
    # Total bookings
    total_bookings = Booking.objects.count()

    # Revenue (₹200 per booking)
    SEAT_PRICE = 200
    total_revenue = total_bookings * SEAT_PRICE

    # Most popular movie
    popular_movie = (
        Booking.objects
        .values("movie__name")
        .annotate(count=Count("id"))
        .order_by("-count")
        .first()
    )

    # Busiest theater
    busiest_theater = (
        Booking.objects
        .values("theater__name")
        .annotate(count=Count("id"))
        .order_by("-count")
        .first()
    )

    # Recent bookings
    recent_bookings = Booking.objects.select_related(
        "movie", "theater", "user"
    ).order_by("-booked_at")[:10]

    return render(
        request,
        "movies/admin_dashboard.html",
        {
            "total_bookings": total_bookings,
            "total_revenue": total_revenue,
            "popular_movie": popular_movie,
            "busiest_theater": busiest_theater,
            "recent_bookings": recent_bookings,
        }
    )
