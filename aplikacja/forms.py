from django.forms import ModelForm, Form
from django import forms
from .models import Directory, File, Section


class DirectoryForm(ModelForm):
    class Meta:
        model = Directory
        fields = ['name', 'description', 'parent']


class FileForm(ModelForm):
    class Meta:
        model = File
        fields = ['name', 'description', 'parent', 'blob']


class ProversForm(Form):
    CHOICES = [('alt-ergo', 'Alt-Ergo'),
               ('z3', 'Z3'),
               ('cvc4', 'CVC4')]
    prover = forms.CharField(label='Wybierz Prover',
                             widget=forms.RadioSelect(choices=CHOICES),
                             initial=CHOICES[0])


class VCsForm(Form):
    conditions = forms.MultipleChoiceField(
        label='Wybierz Verfication Condition',
        choices=[('requires', 'Requires'),
        ('ensures', 'Ensures'),
        ('variant', 'Variant'),
        ('invariant', 'Invariant'),
        ('predicate', 'Predicate'),
        ('ghost', 'Ghost'),
        ('assert', 'Assert'),
        ('lemma', 'Lemma'),
        ('assigns', 'Assigns'),
        ('exits', 'Exits'),
        ('check', 'Check'),
        ('breaks', 'Breaks'),
        ('continues', 'Continues'),
        ('returns', 'Returns')],
        widget=forms.CheckboxSelectMultiple()
    )