from django.shortcuts import render
from musicbeats.models import Song, Watchlater, Favourite  # Thêm Favourite vào import
from django.contrib.auth.models import User
from django.db.models import Case, When

def index(request):
    song = Song.objects.all()[0:3]

    # Listen Later
    if request.user.is_authenticated:
        wl = Watchlater.objects.filter(user=request.user)
        ids = []
        for i in wl:
            ids.append(i.video_id)

        preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(ids)])
        watch = Song.objects.filter(song_id__in=ids).order_by(preserved)
    else:
        watch = Song.objects.all()[0:3]

    # Favourite Songs
    if request.user.is_authenticated:
        fav_objs = Favourite.objects.filter(user=request.user)
        fav_ids = [i.song_id for i in fav_objs]
        fav_preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(fav_ids)])
        fav = Song.objects.filter(song_id__in=fav_ids).order_by(fav_preserved)
    else:
        fav = []

    return render(request, 'index.htm', {
        'song': song,
        'watch': watch,
        'fav': fav,
    })