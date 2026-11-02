from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def setting_view(request):


    context = {

    }

    return render(request, 'information/information.html', context)
