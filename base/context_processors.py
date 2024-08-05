# myapp/context_processors.py

from .models import Log,ScholarShip

def unread_logs_count(request):
    count = 0
    if request.user.is_authenticated:
        count = Log.objects.filter(user=request.user, is_viewed=False).count()
    return {'unread_logs_count': count}

