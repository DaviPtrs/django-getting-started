from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return HttpResponse("Fala meu camarada, voce ta no indice da piscina")