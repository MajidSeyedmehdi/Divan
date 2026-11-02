from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Avg
from django.utils import timezone
from datetime import timedelta
import json

@login_required
def information_view(request):


    context = {

    }

    return render(request, 'information/information.html', context)
