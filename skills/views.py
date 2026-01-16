from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Skill
from django import forms

class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ['title', 'description']

def skill_list(request):
    skills = Skill.objects.all().order_by('-created_at')
    return render(request, 'skills/list.html', {'skills': skills})

def skill_detail(request, pk):
    skill = get_object_or_404(Skill, pk=pk)
    return render(request, 'skills/detail.html', {'skill': skill})

from django.db import transaction

@login_required
def skill_create(request):
    if request.method == 'POST':
        form = SkillForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                skill = form.save(commit=False)
                skill.user = request.user
                skill.save()
            return redirect('skill_list')
    else:
        form = SkillForm()
    return render(request, 'skills/add.html', {'form': form})

@login_required
def skill_edit(request, pk):
    skill = get_object_or_404(Skill, pk=pk, user=request.user)
    if request.method == 'POST':
        form = SkillForm(request.POST, instance=skill)
        if form.is_valid():
            with transaction.atomic():
                form.save()
            return redirect('skill_detail', pk=pk)
    else:
        form = SkillForm(instance=skill)
    return render(request, 'skills/add.html', {'form': form, 'is_edit': True})
