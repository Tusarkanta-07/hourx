from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Skill
from django import forms

class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ['title', 'description', 'category']

def skill_list(request):
    query = request.GET.get('q')
    selected_categories = request.GET.getlist('category')
    skills = Skill.objects.all().order_by('-created_at')
    
    if query:
        skills = skills.filter(title__icontains=query) | skills.filter(description__icontains=query)
        skills = skills.distinct()
        
    if selected_categories:
        skills = skills.filter(category__in=selected_categories)

    return render(request, 'skills/list.html', {
        'skills': skills,
        'query': query,
        'selected_categories': selected_categories
    })

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

from django.contrib import messages
from django.views.decorators.http import require_POST

@login_required
@require_POST
def skill_delete(request, pk):
    skill = get_object_or_404(Skill, pk=pk, user=request.user)
    skill.delete()
    messages.success(request, f"Skill '{skill.title}' deleted successfully.")
    return redirect('skill_list')
