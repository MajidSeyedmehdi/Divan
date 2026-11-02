from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def live_program_audit(request):

    context = {
        'title': 'حسابرسی برنامه زنده',
    }
    return render(request, 'main/includes/sound_recorders/sound_recorder_manager/soundrecorder_manager.html', context)

