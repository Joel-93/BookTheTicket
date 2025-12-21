from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError

from .models import Movie, Theater, Seat, Booking


def movie_list(request):
    search_query = request.GET.get('search')

    if search_query:
        movies = Movie.objects.filter(name__icontains=search_query)
    else:
        movies = Movie.objects.all()

    return render(request, 'movies/movie_list.html', {'movies': movies})


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
    seats = Seat.objects.filter(theater=theater)

    if request.method == 'POST':
        selected_seat_ids = request.POST.getlist('seats')

        # ✅ FIX 1: correct variable check
        if not selected_seat_ids:
            return render(
                request,
                'movies/seat_selection.html',
                {
                    'theater': theater,
                    'seats': seats,
                    'error': 'Please select at least one seat.'
                }
            )

        error_seats = []

        for seat_id in selected_seat_ids:
            seat = get_object_or_404(Seat, id=seat_id, theater=theater)

            if seat.is_booked:
                error_seats.append(seat.seat_number)
                continue

            try:
                Booking.objects.create(
                    user=request.user,
                    seat=seat,
                    theater=theater,
                    movie=theater.movie
                )
                seat.is_booked = True
                seat.save()

            except IntegrityError:
                error_seats.append(seat.seat_number)

        if error_seats:
            error_message = (
                "The following seats are already booked: "
                + ", ".join(error_seats)
            )
            return render(
                request,
                'movies/seat_selection.html',
                {
                    'theater': theater,
                    'seats': seats,
                    'error': error_message
                }
            )

        # ✅ booking success
        return redirect('profile')

    return render(
        request,
        'movies/seat_selection.html',
        {'theater': theater, 'seats': seats}
    )
