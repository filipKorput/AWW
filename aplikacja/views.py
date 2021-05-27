from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from django.shortcuts import render

from .models import Directory, User, File
from .forms import DirectoryForm, FileForm, ProversForm, VCsForm
from .obslugaFramy import *

import logging
from django.utils import timezone


def ekran_logowania(request):
    return render(request, 'aplikacja/login.html')

def authentication(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    user = authenticate(request, username=username, password=password)

    if user is not None:
        login(request, user)
        print("zalogowano: " + username)
        return HttpResponseRedirect('..')
    return render(request, 'aplikacja/login.html')


def index(request):
    context = {
        'directory_list': Directory.objects.filter(availability=True),
        'file_list': File.objects.filter(availability=True)
    }
    return render(request, 'aplikacja/index.html', context)

logger = logging.getLogger(__name__)

def detail(request, name):
    file = File.objects.get(pk=name)
    logger.error(file)
    with open(file.blob.path, 'r', encoding='UTF-8') as fileObject:
        data = fileObject.read().replace('\n', '</br>')
    summary = file.summary.replace('\n', '<br>')
    sectionList = getSectionsOfFile(file)
    context = {
        'directory_list': Directory.objects.filter(availability=True),
        'file_list': File.objects.filter(availability=True),
        'file': file,
        'fileContent': data,
        'sectionList': sectionList,
        'proverForm': ProversForm(),
        'VCForm': VCsForm(),
        'summary': summary
    }
    return render(request, 'aplikacja/index.html', context)


def add_dir(request):
    form = DirectoryForm(request.POST)
    form.instance.creation_date = timezone.now()
    form.instance.availability = True
    u = User.objects.get(login="U2")
    form.instance.owner = u
    if form.is_valid():
        form.instance.save()
        return HttpResponseRedirect('..')
    return render(request, 'aplikacja/add_dir.html', {'form': form})

def add_file(request):
    form = FileForm(request.POST, request.FILES)
    form.instance.creation_date = timezone.now()
    form.instance.availability = True
    u = User.objects.get(login="U2")
    form.instance.owner = u
    if form.is_valid():
        form.instance.blob = request.FILES['blob']
        form.instance.save()
        file = File.objects.get(name=form.instance.name)
        prover = None
        VCs = []
        addSectionsOfFile(file, prover, VCs)
        return HttpResponseRedirect('..')
    return render(request, 'aplikacja/add_file.html', {'form': form})

def delete_dir(request):
    context = {
        'directory_list': Directory.objects.filter(availability=True),
    }
    if request.POST.get("name"):
        name = request.POST.get("name")
        d = Directory.objects.get(name=name)
        d.availability = False
        d.save()
        return HttpResponseRedirect('..')
    return render(request, 'aplikacja/delete_dir.html', context)

def delete_file(request):
    context = {
        'file_list': File.objects.filter(availability=True),
    }
    if request.POST.get("name"):
        name = request.POST.get("name")
        f = File.objects.get(name=name)
        f.availability = False
        f.save()
        return HttpResponseRedirect('..')
    return render(request, 'aplikacja/delete_file.html', context)


def rerun_frama(request, name):
    file = File.objects.get(name=name)
    prover = request.session.get('prover', '')
    VCs = request.session.get('VCs', [])
    updateFramaOfFile(file, prover, VCs)
    return HttpResponseRedirect('/aplikacja/detail/' + name)

def change_prover(request, name):
    prover = request.POST['prover']
    request.session['prover'] = prover
    print('Wybrano prover: ' + request.session['prover'])
    return HttpResponseRedirect('/aplikacja/detail/' + name + '/')

def change_VC(request, name):
    VCs = dict(request.POST).get('conditions', [])
    request.session['VCs'] = VCs
    print('Wybrano verification conditions:')
    print(request.session['VCs'])
    return HttpResponseRedirect('/aplikacja/detail/' + name + '/')

