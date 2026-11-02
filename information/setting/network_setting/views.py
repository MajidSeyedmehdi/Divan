from django.shortcuts import render
from .forms import HeaderForm
from utils.db_connection import connect_db
from decimal import Decimal

def network_setting(request):
    header_form = HeaderForm(request.POST or None)
    settings_rows = []

    network_id = None

    if request.method == "POST" and header_form.is_valid():
        action = request.POST.get("action")

        network = header_form.cleaned_data.get("network")
        shift_count_raw = header_form.cleaned_data.get("shift_count")
        coefficient_raw = header_form.cleaned_data.get("coefficient")

        has_live = header_form.cleaned_data.get("has_live")
        active = header_form.cleaned_data.get("active")
        payable = header_form.cleaned_data.get("payable")

        has_live = False if has_live is None else has_live
        active = False if active is None else active
        payable = False if payable is None else payable

        shift_count = int(shift_count_raw) if shift_count_raw not in ("", None) else None

        if coefficient_raw in ("", None):
            coefficient = None
        else:
            coefficient = Decimal(str(coefficient_raw).replace(",", "."))

        if network:
            network_id = network.id_network

        if action == "submit" and network_id:
            user_name = request.user.username

            with connect_db() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "EXEC Sp_Update_Network_Setting ?, ?, ?, ?, ?, ?,?",
                    [
                        network_id,
                        shift_count,
                        coefficient,
                        has_live,
                        payable,
                        active,
                        user_name
                    ]
                )
                conn.commit()
            network_id = None

    with connect_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "EXEC Sp_Network_Setting_Read @Id_network=?",
            [network_id]
        )
        cols = [c[0] for c in cursor.description]
        settings_rows = [dict(zip(cols, r)) for r in cursor.fetchall()]

    return render(request, "main/includes/setting/network_setting/network_setting.html", {
        "header_form": header_form,
        "settings_rows": settings_rows
    })
