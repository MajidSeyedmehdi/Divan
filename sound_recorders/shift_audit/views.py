from django.shortcuts import render
from django.contrib.auth.decorators import login_required
def current_affairs_view(request):


    context = {

    }

    return render(request, 'sound_recorders\current_affairs\current_affairs.html', context)