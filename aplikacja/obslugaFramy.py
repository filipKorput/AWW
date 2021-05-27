from .models import Section, Status_Data

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

        category = ""
        index = words.index('Goal')
        if words[index + 1] == "Post-condition":
            category = "Post-condition"
        elif words[index + 3] == "Invariant":
            category = "Invariant"
        elif words[index + 4] == "variant":
            category = "Variant"
        elif words[index + 3] == "\'Pre-condition":
            category = "Pre-condition"

        section = Section(line=line_num,
                          creation_date=timezone.now(),
                          category=category,
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
