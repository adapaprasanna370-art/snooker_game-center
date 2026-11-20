
from datetime import datetime, timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail
from django.utils import timezone

from snooker_config.models import SnookerTable, Booking


# HOME PAGE
def home(request):
    tables = SnookerTable.objects.filter(is_active=True)
    return render(request, 'home.html', {'tables': tables})


# PLAYER REGISTRATION
def register_page(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')

        if not username or not email or not password:
            messages.error(request, 'Please fill in all fields.')
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered.')
            return redirect('register')

        User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        messages.success(request, 'Registration successful! Please log in.')
        return redirect('login')

    return render(request, 'register.html')


# PLAYER LOGIN
def login_page(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            messages.success(request, 'Welcome to Snooker Elite!')
            return redirect('game')

        messages.error(request, 'Invalid username or password.')

    return render(request, 'login.html')


# PLAYER LOGOUT
@login_required(login_url='/login/')
def logout_page(request):
    logout(request)
    return redirect('home')


# SNOOKER GAME
@login_required(login_url='/login/')
def game(request):
    return render(request, 'game.html')


# FREE TABLE BOOKING
@login_required(login_url='/login/')
def book_table(request):
    tables = SnookerTable.objects.filter(is_active=True)

    if request.method == 'POST':
        try:
            table = SnookerTable.objects.get(
                id=request.POST.get('table'),
                is_active=True
            )

            booking_date = datetime.strptime(
                request.POST.get('booking_date', ''),
                '%Y-%m-%d'
            ).date()

            start_time = datetime.strptime(
                request.POST.get('start_time', ''),
                '%H:%M'
            ).time()

            duration = int(request.POST.get('duration_hours', '1'))

            if duration not in (1, 2, 3):
                raise ValueError('Invalid duration')

            if booking_date < timezone.localdate():
                messages.error(
                    request,
                    'Please choose today or a future date.'
                )
                return redirect('book_table')

            new_start = datetime.combine(booking_date, start_time)
            new_end = new_start + timedelta(hours=duration)

            existing_bookings = Booking.objects.filter(
                table=table,
                booking_date=booking_date,
                status='Confirmed'
            )

            for old_booking in existing_bookings:
                old_start = datetime.combine(
                    old_booking.booking_date,
                    old_booking.start_time
                )

                old_end = old_start + timedelta(
                    hours=old_booking.duration_hours
                )

                if new_start < old_end and new_end > old_start:
                    messages.error(
                        request,
                        'Sorry! This table is already booked at that time.'
                    )
                    return redirect('book_table')

            # SAVE BOOKING
            booking = Booking.objects.create(
                player=request.user,
                table=table,
                booking_date=booking_date,
                start_time=start_time,
                duration_hours=duration
            )

            # SEND BOOKING CONFIRMATION EMAIL
            if request.user.email:
                try:
                    send_mail(
                        subject='Snooker Elite - Booking Confirmed',
                        message=f"""
Hello {request.user.username},

Your snooker table booking is confirmed!

Table: {table.name}
Date: {booking.booking_date}
Time: {booking.start_time}
Duration: {booking.duration_hours} hour(s)
Booking Fee: FREE

Thank you for choosing Snooker Elite!

Regards,
Snooker Elite Team
""",
                        from_email=None,
                        recipient_list=[request.user.email],
                        fail_silently=False
                    )

                    messages.success(
                        request,
                        'Booking confirmation email sent successfully!'
                    )

                except Exception as email_error:
                    print('EMAIL ERROR:', email_error)
                    messages.warning(
                        request,
                        'Booking successful, but email could not be sent. Check Gmail settings.'
                    )
            else:
                messages.warning(
                    request,
                    'Booking successful! No email address is registered for your account.'
                )

            messages.success(
                request,
                'Your table has been booked successfully!'
            )

            return redirect('my_bookings')

        except (ValueError, TypeError, SnookerTable.DoesNotExist):
            messages.error(
                request,
                'Please enter valid booking details.'
            )

    return render(request, 'book_table.html', {'tables': tables})


# MY BOOKINGS
@login_required(login_url='/login/')
def my_bookings(request):
    bookings = Booking.objects.filter(
        player=request.user
    ).order_by('-booking_date', '-start_time')

    return render(
        request,
        'my_bookings.html',
        {'bookings': bookings}
    )


# CANCEL BOOKING
@login_required(login_url='/login/')
def cancel_booking(request, booking_id):
    if request.method == 'POST':
        booking = get_object_or_404(
            Booking,
            id=booking_id,
            player=request.user
        )

        booking.status = 'Cancelled'
        booking.save(update_fields=['status'])

        messages.success(
            request,
            'Your booking has been cancelled.'
        )

    return redirect('my_bookings')


# LEADERBOARD
@login_required(login_url='/login/')
def leaderboard(request):
    players = User.objects.filter(
        is_active=True
    ).order_by('username')

    return render(
        request,
        'leaderboard.html',
        {'players': players}
    )
