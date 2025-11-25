import json
import os
from datetime import datetime, timedelta

from django.http import JsonResponse
from django.shortcuts import render
from django.templatetags.static import static
from persiantools import jdatetime
from stimulsoft_reports import StiLicense
from stimulsoft_reports.report import StiReport
from stimulsoft_reports.viewer import StiViewer
from khayyam import JalaliDate
from testpro import settings
from utils.db_connection import connect_db


def set_params(request):
    if request.method == "POST":
        body = json.loads(request.body)

        request.session["report_params"] = {
            "start_date": body.get("date"),
            "id_network": body.get("network"),
            "id_sound_recorder": body.get("recorder"),
            "end_date": body.get("date")  # یا تاریخی دیگر
        }

        return JsonResponse({"status": "ok"})


def report_viewer(request):
    params = request.session.get("report_params", {})

    return render(request, "main/includes/sound_recorders/report/report_viewer.html", {"params": params})


def report_shift(request):
    if request.method == "POST":
        body = json.loads(request.body)

        start_date = body.get("start_date")
        end_date = body.get("end_date")
        id_network = body.get("id_network")
        id_sound_recorder = body.get("id_sound_recorder")

        return JsonResponse({
            "variables": {
                "start_date": start_date,
                "end_date": end_date,
                "id_network": id_network,
                "id_sound_recorder": id_sound_recorder
            }
        })
