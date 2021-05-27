import logging
from fileinput import filename

from django.http import HttpResponseRedirect
from django.shortcuts import render
from .models import Directory, User, File, Section, Status_Data

from .forms import DirectoryForm, FileForm, ProversForm, VCsForm

from django.utils import timezone

import subprocess
from django.conf import settings


def getFramaSectionsFromFile(file, prover, VCs):
    command = ['frama-c', '-wp', '-wp-print', '-wp-log=r:result.txt']
    border = '------------------------------------------------------------'
    if prover:
        command.append('-wp-prover')
        command.append(prover)
    for condition in VCs:
        command.append('-wp-prop=@' + condition)
    command.append(file.blob.path)
    print("Running frama-c with command:")
    print(command)
    p = subprocess.run(command, capture_output=True, text=True)
    with open(str(settings.BASE_DIR) + "/result.txt") as f:
        file.summary = f.read()
    file.save()
    section_list = p.stdout.split(border)
    section_list.pop(0)
    section_list.pop(len(section_list) - 1)
    return section_list


def addSectionsOfFile(file, prover, VCs):
    section_list = getFramaSectionsFromFile(file, prover, VCs)
    print(section_list[0])
    used_lines = set()
    for s in section_list:
        words = s.split()
        if not words or words[0] == 'Function':
            continue
        index = words.index('line')
        line_num = words[index + 1]
        line_num = int(line_num[:line_num.index(')')])
        if line_num in used_lines:
            continue
        used_lines.add(line_num)

        index = words.index('returns')
        status = words[index + 1]
        section.save()

        section = Section(line=line_num,
                          creation_date=timezone.now(),
                          category="Postcondition",
                          status=status,
                          parent=file)
        section.status_data = Status_Data(field=s, user=file.owner)
        section.status_data.save()
        section.save()


def getSectionsOfFile(file):
    sections = list()
    sectionList = Section.objects.filter(parent=file)
    for s in sectionList:
        if s.status_data:
            sections.append((s.status_data.field, s.status, s.category))
    return sections


def updateFramaOfFile(file, prover, VCs):
    Section.objects.filter(parent=file).delete()
    addSectionsOfFile(file, prover, VCs)



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

