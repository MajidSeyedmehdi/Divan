from django.shortcuts import render
from django.http.response import HttpResponse

def recordpage(request):
    return HttpResponse("salam")