from __future__ import unicode_literals
from .models import User, Poke
from django.shortcuts import render,redirect
from django.contrib import messages
from django.db.models import Count, Sum
from django.utils import timezone
from datetime import datetime


def index(request):
  return render(request,'index.html')

def register(request):
    result = User.objects.validate_registration(request.POST)
    if type(result) == list:
        for err in result:
            messages.error(request, err)
        return redirect('/')
    request.session['user_id'] = result.id
    return redirect('/pokes')



def login(request):
    result = User.objects.validate_login(request.POST)
    if type(result) == list:
        for err in result:
            messages.error(request, err)
        return redirect('/')
    request.session['user_id'] = result.id
    return redirect('/pokes')

def logout(request):
    for key in request.session.keys():
        del request.session[key]
    return redirect('/')

def pokes(request):
    context = {
		'user':User.objects.get(id=request.session['user_id']),
		'total_pokers':User.objects.filter(id=request.session['user_id']).annotate(counter=Count("receives_the_poke__pokes")),
		'all_pokes':User.objects.exclude(id=request.session['user_id']).annotate(counter=Sum("receives_the_poke__pokes")),
		'my_pokes':Poke.objects.filter(receiver=request.session['user_id']),
		}
    return render(request, 'dashboard.html', context)


def poke_someone(request):
	senderid = User.objects.get(id=request.session['user_id'])
	receiverid = User.objects.get(id=request.POST['receiver'])
	poking = Poke.objects.filter(sender=senderid, receiver=receiverid)
	if not poking:
		Poke.objects.create(sender=senderid, receiver=receiverid, pokes=1)
		return redirect('/pokes')
	else:
		poking[0].pokes += 1
		poking[0].save()
		return redirect('/pokes')
