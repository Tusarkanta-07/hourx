from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Avg, Count, Q
from .models import Skill
from django import forms

class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ['title', 'description', 'category']

def skill_list(request):
    query = request.GET.get('q', '').strip()
    selected_categories = request.GET.getlist('category')
    min_rating = request.GET.get('min_rating', '').strip()

    skills = Skill.objects.select_related('user').annotate(
        avg_rating=Avg('user__reviews_received__rating'),
        review_count=Count('user__reviews_received')
    ).order_by('-created_at')
    
    if query:
        skills = skills.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(user__username__icontains=query)
        ).distinct()
        
    if selected_categories:
        skills = skills.filter(category__in=selected_categories)

    if min_rating:
        try:
            min_rating_val = float(min_rating)
            skills = skills.filter(avg_rating__gte=min_rating_val)
        except ValueError:
            pass

    # Pagination: 9 skills per page for 3x3 grid
    paginator = Paginator(skills, 9)
    page = request.GET.get('page', 1)
    try:
        skills_page = paginator.page(page)
    except PageNotAnInteger:
        skills_page = paginator.page(1)
    except EmptyPage:
        skills_page = paginator.page(paginator.num_pages)

    return render(request, 'skills/list.html', {
        'skills': skills_page,
        'query': query,
        'selected_categories': selected_categories,
        'min_rating': min_rating,
        'total_skills': paginator.count,
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
