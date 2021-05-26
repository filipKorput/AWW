from django.contrib.auth.base_user import AbstractBaseUser
from django.db import models
#from mttp.models import MTTPModel, TreeForeignKey
from django.utils import timezone


class User(AbstractBaseUser):
    name = models.CharField(max_length=50, unique=True, primary_key=True)
    login = models.CharField(max_length=50, unique=True)
    USERNAME_FIELD = 'name'
    REQUIRED_FIELDS = ['name', 'login']


class Directory(models.Model):
    name = models.CharField(max_length=100, blank=False, primary_key=True, unique=True)
    description = models.CharField(max_length=1000, blank=True)
    creation_date = models.DateTimeField('date of creation', blank=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=False)
    availability = models.BooleanField(blank=False)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, blank=True, null=True)
    timestamp = models.DateTimeField('last modified', blank=True, default=timezone.now())
    validity = models.BooleanField(blank=False, default=True)


class File(models.Model):
    name = models.CharField(max_length=100, blank=False, primary_key=True, unique=True)
    description = models.CharField(max_length=1000, blank=True)
    creation_date = models.DateTimeField('date of creation', blank=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, blank=False)
    availability = models.BooleanField(blank=False)
    parent = models.ForeignKey(Directory, on_delete=models.CASCADE)
    timestamp = models.DateTimeField('last modified', blank=True, default=timezone.now())
    validity = models.BooleanField(blank=False, default=True)
    blob = models.FileField(null=True)
    summary = models.TextField(null=True)


class Status_Data(models.Model):
    field = models.TextField(blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class Section(models.Model):
    name = models.CharField(max_length=100, blank=True)
    description = models.CharField(max_length=1000, blank=True)
    line = models.IntegerField(blank=True)
    creation_date = models.DateTimeField('date of creation', blank=False)
    CATEGORY_CHOICES = [
        ('req', 'requires'),
        ('ens', 'ensures'),
        ('var', 'variant'),
        ('invr', 'invariant'),
        ('pred', 'predicate'),
        ('ghst', 'ghost'),
        ('ass', 'assert'),
        ('lemm', 'lemma'),
        ('asgn', 'assigns'),
        ('exit', 'exits'),
        ('chck', 'check'),
        ('brk', 'breaks'),
        ('cont', 'continues'),
        ('ret', 'returns')
    ]
    category = models.CharField(max_length=4, choices=CATEGORY_CHOICES, blank=False)
    STATUS_CHOICES = [
        ('pro', 'Proved'),
        ('inv', 'Invalid'),
        ('cex', 'CounterExample'),
        ('unc', 'Unchecked')
    ]
    status = models.CharField(max_length=3, choices=STATUS_CHOICES, blank=False)
    status_data = models.ForeignKey(Status_Data, on_delete=models.CASCADE)
    parent = models.ForeignKey(File, on_delete=models.CASCADE)
    validity = models.BooleanField(blank=False, default=True)
