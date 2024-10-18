from django.shortcuts import render
from django.http import HttpResponse


def home(self, request):
    return HttpResponse("Hello World")