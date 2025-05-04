from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
from django.utils import timezone
from django import forms
from .models import QuickSession
 
class NameForm(forms.Form):
     name = forms.CharField(
         max_length=100,
         widget=forms.TextInput(attrs={
             'placeholder': 'Enter your name',
             'class': 'name-input'
         }),
         label=''
     )
def start_session(request):
     if request.method == 'POST':
         form = NameForm(request.POST)
         if form.is_valid():
             session = QuickSession.objects.create(
                 name=form.cleaned_data['name'],
                 data={}
             )
             request.session['quick_session_id'] = session.id
             return redirect('quickstart:dashboard')
     else:
         form = NameForm()
     
     return render(request, 'quickstart/start.html', {'form': form})
 
def dashboard(request):
     session_id = request.session.get('quick_session_id')
     if not session_id:
         return redirect('quickstart:start')
     
     try:
         session = QuickSession.objects.get(id=session_id)
         if session.is_expired():
             session.delete()
             del request.session['quick_session_id']
             return redirect('quickstart:start')
     except QuickSession.DoesNotExist:
         del request.session['quick_session_id']
         return redirect('quickstart:start')
     
     return render(request, 'quickstart/dashboard.html', {'session': session})

def create_list(request):
    session_id = request.session.get('quick_session_id')
    if not session_id:
        return redirect('quickstart:start')
    
    try:
        session = QuickSession.objects.get(id=session_id)
        if session.is_expired():
            session.delete()
            del request.session['quick_session_id']
            return redirect('quickstart:start')
    except QuickSession.DoesNotExist:
        del request.session['quick_session_id']
        return redirect('quickstart:start')
    
    # Create a new list in the session's data
    if 'lists' not in session.data:
        session.data['lists'] = []
    
    new_list = {
        'id': len(session.data['lists']) + 1,
        'name': f'New List {len(session.data["lists"]) + 1}',
        'items': []
    }
    session.data['lists'].append(new_list)
    session.save()
    
    return redirect('quickstart:dashboard')

def view_lists(request):
    session_id = request.session.get('quick_session_id')
    if not session_id:
        return redirect('quickstart:start')
    
    try:
        session = QuickSession.objects.get(id=session_id)
        if session.is_expired():
            session.delete()
            del request.session['quick_session_id']
            return redirect('quickstart:start')
    except QuickSession.DoesNotExist:
        del request.session['quick_session_id']
        return redirect('quickstart:start')
    
    # Get lists from session data
    lists = session.data.get('lists', [])
    
    return render(request, 'quickstart/view_lists.html', {
        'session': session,
        'lists': lists
    })