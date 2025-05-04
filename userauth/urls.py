from django.urls import path
from . import views
from django.contrib.auth import views as auth_views


    

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('add-employee/', views.add_employee_view, name='add_employee'),
    path('choose-mode/', views.choose_mode_view, name='choose-mode'),
    path('choose-role/', views.choose_role_view, name='choose-role'),
    path('login/', views.login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    
    # Dashboard URLs
    path('dashboard/', views.dashboard, name='dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('employee-dashboard/', views.employee_dashboard, name='employee_dashboard'),
    
    # Ticket management
    path('create-ticket/', views.create_ticket, name='create_ticket'),
    path('ticket/<int:ticket_id>/status/<str:new_status>/', views.update_ticket_status, name='update_ticket_status'),
    path('ticket/<int:ticket_id>/reassign/', views.reassign_ticket, name='reassign_ticket'),

    path('personal-dashboard/', views.personal_dashboard, name='personal_dashboard'),
    path('api/todos/', views.get_todos, name='get_todos'),
    path('api/todos/add/', views.add_todo, name='add_todo'),
    path('api/todos/update/<int:todo_id>/', views.update_todo, name='update_todo'),
    path('api/todos/delete/<int:todo_id>/', views.delete_todo, name='delete_todo'),
    path('diary/', views.diary_view, name='diary'),
]






