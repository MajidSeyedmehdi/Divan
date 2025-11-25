from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def inf_manager_view(request):

    context = {
        'title': 'مدیر آمار و اطلاعات',
    }
    return render(request, 'main/includes/inf_manager/inf_manager.html', context)
