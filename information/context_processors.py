import jdatetime

def roles_context(request):
    if not request.user.is_authenticated:
        return {}

    is_info_manager = (
            request.user.is_superuser or
            request.user.groups.filter(name="مدیر آمار و اطلاعات فنی").exists() or
            request.user.groups.filter(name="کارشناس آمار و اطلاعات فنی").exists()
    )
    is_sound_engineer = (
            request.user.is_superuser or
            request.user.groups.filter(name="صدابرداران").exists()
    )

    return {
        'is_info_manager': is_info_manager,
        'is_sound_engineer': is_sound_engineer,
    }
def common_context(request):
    if request.user.username and request.user.password:
        full_name = f"{request.user.first_name} {request.user.last_name}"
        role = f"{request.user.groups.first().name}"
    else:
        full_name = request.user.username
        role = 'کاربر'
    
    today = jdatetime.datetime.now()
    persian_date = today.strftime("%Y/%m/%d")
    day_mapping = {
        'Saturday': 'شنبه',
        'Sunday': 'یکشنبه',
        'Monday': 'دوشنبه',
        'Tuesday': 'سه‌شنبه',
        'Wednesday': 'چهارشنبه',
        'Thursday': 'پنج‌شنبه',
        'Friday': 'جمعه'
    }
    persian_day = day_mapping[today.strftime("%A")]
    
    return {
        'full_name': full_name,
        'role': role,
        'persian_date': persian_date,
        'persian_day': persian_day,
    } 