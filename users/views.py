from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import login, authenticate, update_session_auth_hash, logout
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone

from movies.models import Movie, Booking
from .forms import UserRegisterForm, UserUpdateForm


# =========================
# HOME
# =========================
def home(request):
    movies = Movie.objects.all()
    return render(request, 'home.html', {'movies': movies})


# =========================
# AUTH
# =========================
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)

        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')

            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('profile')
    else:
        form = UserRegisterForm()

    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():
            login(request, form.get_user())
            return redirect('home')
    else:
        form = AuthenticationForm()

    return render(request, 'users/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    return redirect('home')


# =========================
# PROFILE
# =========================
@login_required
def profile(request):
    bookings = Booking.objects.filter(user=request.user)

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        if u_form.is_valid():
            u_form.save()
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)

    return render(
        request,
        'users/profile.html',
        {
            'u_form': u_form,
            'bookings': bookings
        }
    )


@login_required
def reset_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)

        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            return redirect('login')
    else:
        form = PasswordChangeForm(user=request.user)

    return render(request, 'users/reset_password.html', {'form': form})


def contact(request):
    return render(request, 'users/contact.html')


# =========================
# ADMIN SECTION
# =========================
def is_admin(user):
    return user.is_staff


def admin_login(request):
    """
    Always use Django's built-in admin login.
    """
    return redirect('/admin/login/')


@user_passes_test(is_admin, login_url='/admin/login/')
def admin_dashboard(request):
    from django.db.models import Count
    from movies.models import Booking
    
    # Total bookings
    total_bookings = Booking.objects.count()

    # Revenue (₹200 per booking)
    SEAT_PRICE = 200
    total_revenue = total_bookings * SEAT_PRICE

    # Most popular movie
    popular_movie_data = (
        Booking.objects
        .values("movie__name")
        .annotate(count=Count("id"))
        .order_by("-count")
        .first()
    )
    popular_movie = popular_movie_data['movie__name'] if popular_movie_data else None

    # Busiest theater
    busiest_theater_data = (
        Booking.objects
        .values("theater__name")
        .annotate(count=Count("id"))
        .order_by("-count")
        .first()
    )
    busiest_theater = busiest_theater_data['theater__name'] if busiest_theater_data else None

    # Recent bookings
    recent_bookings = Booking.objects.select_related(
        "movie", "theater", "user"
    ).order_by("-booked_at")[:10]

    return render(request, 'users/admin_dashboard.html', {
        "total_bookings": total_bookings,
        "total_revenue": total_revenue,
        "popular_movie": popular_movie,
        "busiest_theater": busiest_theater,
        "recent_bookings": recent_bookings,
    })
