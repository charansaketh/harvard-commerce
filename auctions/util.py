from .models import User

def watchlist_total(request):
    if request.user.is_authenticated:
        user = User.objects.get(pk=request.user.id)
        watchlistcount = user.watching_user.count()
    else:
        watchlistcount = ''
    return watchlistcount    