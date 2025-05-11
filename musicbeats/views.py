# Create your views here.
from django.shortcuts import render
from musicbeats.models import Song, Watchlater, History, Channel
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from django.db.models import Case, When


def search(request):
	query = request.GET.get("query")

	song = Song.objects.all()
	qs = song.filter(name__icontains = query)

	return render(request, 'musicbeats/search.htm', {"songs": qs, "query": query})
	

def history(request):
	if request.method == "POST":
		user = request.user
		music_id = request.POST['music_id']
		history = History(user = user, music_id = music_id)
		history.save()

		return redirect(f"/musicbeats/songs/{music_id}")

	history = History.objects.filter(user = request.user)
	ids = []
	for i in history:
		ids.append(i.music_id)

	preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(ids)])
	song = Song.objects.filter(song_id__in = ids).order_by(preserved)		
	return render(request, 'musicbeats/history.htm', {"history": song})



def watchlater(request):
	if request.method == "POST":
		user = request.user
		video_id = request.POST['video_id']

		watch = Watchlater.objects.filter(user = user)

		for i in watch:
			if video_id == i.video_id:
				message = "Your Video is Already Added"
				break
		else:
			watchlater = Watchlater(user = user, video_id = video_id)
			watchlater.save()
			message = "Your Video is Successfully Added"

		song = Song.objects.filter(song_id = video_id).first()	
		return render(request, f"musicbeats/songpost.htm", {'song': song, "message": message})

	wl = Watchlater.objects.filter(user = request.user)
	ids = []
	for i in wl:
		ids.append(i.video_id)

	preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(ids)])
	song = Song.objects.filter(song_id__in = ids).order_by(preserved)	

	return render(request, "musicbeats/watchlater.htm", {'song': song})

# def index(request):
# 	song = Song.objects.all()
# 	return render(request, 'index.htm', {'song': song})


def songs(request):
	song = Song.objects.all()
	return render(request, 'musicbeats/songs.htm', {'song': song})


def songpost(request, id):
	song = Song.objects.filter(song_id = id).first()
	return render(request, 'musicbeats/songpost.htm', {'song': song})


def login(request):
  if request.method == "POST":
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password = password)
    if user is not None:
      from django.contrib.auth import login
      login(request, user)
      return redirect("/")  # ĐẶT return ở đây
    else:
      # Có thể thêm thông báo lỗi nếu muốn
      return render(request, 'musicbeats/login.htm', {'error': 'Invalid username or password'})
  return render(request, 'musicbeats/login.htm')

def signup(request):
    if request.method == "POST":
        email = request.POST['email']
        username = request.POST['username']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']

        # Kiểm tra bắt buộc nhập email
        if not email.strip():
            from django.contrib import messages
            messages.error(request, "Email is required!")
            return redirect("/musicbeats/signup")  # hoặc redirect lại trang đăng ký

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username is already taken. Plz try another one!")
            return redirect("/musicbeats/signup")

        if len(username) > 15:
            messages.error(request, "Username must be less than 14 characters!")
            return redirect("/musicbeats/signup")

        if not username.isalnum():
            messages.error(request, "Username should be contain Characters and Number!")
            return redirect("/musicbeats/signup")

        if pass1 != pass2:
            messages.error(request, "Password do not match. Plz sign up again!")
            return redirect("/musicbeats/signup")

        myuser = User.objects.create_user(username, email, pass1)
        myuser.first_name = first_name
        myuser.last_name = last_name
        myuser.save()
        user = authenticate(username=username, password=pass1)
        from django.contrib.auth import login
        login(request, user)

        channel = Channel(name=username)
        channel.save()

        return redirect('/')
    return render(request, 'musicbeats/signup.htm')
    

def logout_user(request):
    logout(request)
    return redirect("/")


def channel(request, channel):
	chan = Channel.objects.filter(name=channel).first() 
	video_ids = [id for id in str(chan.music).split(" ") if id]

	preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(video_ids)])
	song = Song.objects.filter(song_id__in = video_ids).order_by(preserved)	

	return render(request, "musicbeats/channel.htm", {"channel": chan, "song": song})  


def upload(request):
	if request.method == "POST":
		name = request.POST['name']
		singer = request.POST['singer']
		tag = request.POST['tag']
		image = request.POST['image']
		movie = request.POST['movie'] 
		credit = request.POST['credit']
		song = request.FILES['file']

		song_model = Song(name=name, singer = singer, tags = tag, image = image, movie = movie, credit = credit, song = song)
		song_model.save()

		music_id = song_model.song_id
		channel_find = Channel.objects.filter(name = str(request.user))
		print(channel_find)


		for i in channel_find:
			i.music += f" {music_id} "
			i.save()


	return render(request, "musicbeats/upload.htm")  


from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect

@login_required
def remove_watchlater(request, song_id):
    if request.method == "POST":
        item = Watchlater.objects.filter(user=request.user, video_id=str(song_id)).first()
        if item:
            item.delete()
    return redirect('watchlater')


from .models import Favourite

from django.contrib.auth.decorators import login_required

@login_required
def favourite(request):
    if request.method == "POST":
        user = request.user
        song_id = request.POST['song_id']

        fav = Favourite.objects.filter(user=user, song_id=song_id)
        if fav.exists():
            message = "This song is already in your Favourites"
        else:
            Favourite(user=user, song_id=song_id).save()
            message = "Song added to Favourites"
        song = Song.objects.filter(song_id=song_id).first()
        return render(request, "musicbeats/songpost.htm", {'song': song, 'message': message})

    favs = Favourite.objects.filter(user=request.user)
    ids = [i.song_id for i in favs]
    preserved = Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(ids)])
    song = Song.objects.filter(song_id__in=ids).order_by(preserved)
    return render(request, "musicbeats/favourite.htm", {'song': song})

@login_required
def remove_favourite(request, song_id):
    if request.method == "POST":
        item = Favourite.objects.filter(user=request.user, song_id=str(song_id)).first()
        if item:
            item.delete()
    return redirect('favourite')  
    
def song_info(request, song_id):
    song = Song.objects.filter(song_id=song_id).first()
    return render(request, 'musicbeats/song_info.htm', {'song': song})
