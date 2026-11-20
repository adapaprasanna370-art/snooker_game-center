
from django.contrib import admin
from django.urls import path

from views import (
    home,
    register_page,
    login_page,
    logout_page,
    game,
    book_table,
    my_bookings,
    cancel_booking,
    leaderboard,
)

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', home, name='home'),

    path('register/', register_page, name='register'),
    path('login/', login_page, name='login'),
    path('logout/', logout_page, name='logout'),

    path('game/', game, name='game'),

    path('book-table/', book_table, name='book_table'),
    path('my-bookings/', my_bookings, name='my_bookings'),
    path(
        'cancel-booking/<int:booking_id>/',
        cancel_booking,
        name='cancel_booking'
    ),

    path('leaderboard/', leaderboard, name='leaderboard'),
]
