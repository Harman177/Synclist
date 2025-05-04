# userauth/views.py
from django.shortcuts import render, redirect,get_object_or_404
from .forms import SignUpForm
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from .forms import EmployeeCreationForm,TicketCreationForm
from django.db.models import Count
from.models import Ticket,Profile
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import models

# Create your views here.
def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.profile.is_admin = form.cleaned_data['is_admin']
            user.profile.save()
            login(request, user)
            if user.profile.is_admin:
                return redirect('choose-mode')  # Redirect admin users to choose-mode
            else:
                return redirect('choose-mode')  # Send non-admin users to choose-mode
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})
@login_required
def add_employee_view(request):
    if not request.user.profile.is_admin:
        messages.error(request, "Only admins can add employees.")
        return redirect('employee_dashboard')
    
    if request.method == 'POST':
        form = EmployeeCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.profile.is_admin = False
            user.profile.save()
            messages.success(request, f"Employee {user.username} created successfully.")
            return redirect('choose-mode')  # Go to choose-mode after adding employee
    else:
        form = EmployeeCreationForm()
    return render(request, 'add_employee.html', {'form': form})
@login_required
def choose_mode_view(request):
    return render(request, 'choose_mode.html')
@login_required
def choose_role_view(request):
    if request.method == 'POST':
        role = request.POST.get('role')

        if role == 'admin' and request.user.profile.is_admin:
            # ✅ Mark onboarding complete
            request.user.profile.has_onboarded = True
            request.user.profile.save()
            return redirect('admin_dashboard')

        elif role == 'team':
            return redirect('employee_dashboard')

    return render(request, 'choose_role.html')

@login_required
def dashboard(request):
    if request.user.profile.is_admin:
        if not request.user.profile.has_onboarded:
            return redirect('add_employee')
        return redirect('admin_dashboard')
    else:
        return redirect('employee_dashboard')

    
@login_required
def admin_dashboard(request):
    if not request.user.profile.is_admin:
        return redirect('employee_dashboard')
    
    # Get search query from request
    search_query = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    
    # Base queryset
    tickets = Ticket.objects.all().order_by('-created_at')
    
    # Apply search filter if query exists
    if search_query:
        tickets = tickets.filter(
            models.Q(title__icontains=search_query) |
            models.Q(description__icontains=search_query) |
            models.Q(ticket_number__icontains=search_query)
        )
    
    # Apply status filter if selected
    if status_filter and status_filter != 'all':
        tickets = tickets.filter(status=status_filter)
    
    # Get counts for all tickets (not just filtered ones)
    all_tickets = Ticket.objects.all()
    open_count = all_tickets.filter(status='open').count()
    in_progress_count = all_tickets.filter(status='in_progress').count()
    resolved_count = all_tickets.filter(status='resolved').count()
    closed_count = all_tickets.filter(status='closed').count()
    
    context = {
        'tickets': tickets,
        'open_count': open_count,
        'in_progress_count': in_progress_count,
        'resolved_count': resolved_count,
        'closed_count': closed_count,
        'search_query': search_query,
        'status_filter': status_filter,
    }
    
    return render(request, 'admin_dashboard.html', context)
@login_required
def employee_dashboard(request):
    if request.user.profile.is_admin:
        return redirect('admin_dashboard')
    
    # Get tickets assigned to the employee
    tickets = Ticket.objects.filter(assigned_to=request.user).order_by('-created_at')
    
    # Count tickets by status
    to_do_count = tickets.filter(status='open').count()
    in_progress_count = tickets.filter(status='in_progress').count()
    completed_count = tickets.filter(status__in=['resolved', 'closed']).count()
    
    context = {
        'tickets': tickets,
        'to_do_count': to_do_count,
        'in_progress_count': in_progress_count,
        'completed_count': completed_count,
    }
    
    return render(request, 'employee_dashboard.html', context)
@login_required
def create_ticket(request):
    if not request.user.profile.is_admin:
        messages.error(request, "Only admins can create tickets")
        return redirect('employee_dashboard')
    
    if request.method == 'POST':
        form = TicketCreationForm(request.POST, user=request.user)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.created_by = request.user
            ticket.save()
            messages.success(request, f"Ticket '{ticket.title}' created successfully")
            return redirect('admin_dashboard')
    else:
        form = TicketCreationForm(user=request.user)
    
    return render(request, 'create_ticket.html', {'form': form})
@login_required
def update_ticket_status(request, ticket_id, new_status):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    
    # Ensure proper permissions
    if request.user.profile.is_admin:
        # Admin can update any status
        ticket.status = new_status
        ticket.save()
        return redirect('admin_dashboard')
    else:
        # Employee can only update specific statuses
        if ticket.assigned_to != request.user:
            messages.error(request, "You can only update tickets assigned to you")
            return redirect('employee_dashboard')
        
        if new_status in ['in_progress', 'on_hold', 'resolved']:
            ticket.status = new_status
            ticket.save()
        else:
            messages.error(request, "You don't have permission to set this status")
        
        return redirect('employee_dashboard')

@login_required
def reassign_ticket(request, ticket_id):
    if not request.user.profile.is_admin:
        messages.error(request, "Only admins can reassign tickets")
        return redirect('employee_dashboard')
    
    ticket = get_object_or_404(Ticket, id=ticket_id)
    
    if request.method == 'POST':
        new_assignee_id = request.POST.get('assigned_to')
        if new_assignee_id:
            new_assignee = get_object_or_404(User, id=new_assignee_id)
            if not new_assignee.profile.is_admin:  # Only allow assigning to non-admin users
                ticket.assigned_to = new_assignee
                ticket.save()
                messages.success(request, f"Ticket has been reassigned to {new_assignee.username}")
            else:
                messages.error(request, "Cannot assign tickets to admin users")
        else:
            ticket.assigned_to = None
            ticket.save()
            messages.success(request, "Ticket has been unassigned")
        return redirect('admin_dashboard')
    
    # Get all non-admin users for the dropdown
    employees = User.objects.filter(profile__is_admin=False)
    context = {
        'ticket': ticket,
        'employees': employees,
    }
    return render(request, 'reassign_ticket.html', context)

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_datetime
import json
from .models import TodoItem

@login_required
def personal_dashboard(request):
    # Get the user's todo items to display initially
    todos = TodoItem.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'personal_dashboard.html', {'todos': todos})

@login_required
def get_todos(request):
    todos = TodoItem.objects.filter(user=request.user).order_by('-created_at')
    todos_list = []
    
    for todo in todos:
        todos_list.append({
            'id': todo.id,
            'title': todo.title,
            'description': todo.description or '',
            'createdAt': todo.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'priority': todo.priority,
            'deadline': todo.deadline.strftime('%Y-%m-%dT%H:%M') if todo.deadline else '',
            'category': todo.category or ''
        })
    
    return JsonResponse({'todos': todos_list})

@login_required
@csrf_exempt
def add_todo(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        
        deadline = None
        if data.get('deadline'):
            deadline = parse_datetime(data.get('deadline'))
        
        todo = TodoItem.objects.create(
            user=request.user,
            title=data.get('title'),
            description=data.get('description'),
            priority=data.get('priority'),
            deadline=deadline,
            category=data.get('category')
        )
        
        return JsonResponse({
            'success': True,
            'todo': {
                'id': todo.id,
                'title': todo.title,
                'description': todo.description or '',
                'createdAt': todo.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'priority': todo.priority,
                'deadline': todo.deadline.strftime('%Y-%m-%dT%H:%M') if todo.deadline else '',
                'category': todo.category or ''
            }
        })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
@csrf_exempt
def update_todo(request, todo_id):
    if request.method == 'POST':
        try:
            todo = TodoItem.objects.get(id=todo_id, user=request.user)
            data = json.loads(request.body)
            
            todo.title = data.get('title')
            todo.description = data.get('description')
            todo.priority = data.get('priority')
            
            if data.get('deadline'):
                todo.deadline = parse_datetime(data.get('deadline'))
            else:
                todo.deadline = None
                
            todo.category = data.get('category')
            todo.save()
            
            return JsonResponse({'success': True})
            
        except TodoItem.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Todo not found'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
@csrf_exempt
def delete_todo(request, todo_id):
    if request.method == 'POST':
        try:
            todo = TodoItem.objects.get(id=todo_id, user=request.user)
            todo.delete()
            return JsonResponse({'success': True})
        except TodoItem.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Todo not found'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('choose-mode')  # Redirect to choose-mode after login
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'login.html')




