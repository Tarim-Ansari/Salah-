from django.shortcuts import render

def role(request):
    return render(request, 'accounts/role.html')

def login_view(request):
    role = request.GET.get('role', '')
    return render(request, 'accounts/login.html', {'role': role})

def signup_view(request):
    role = request.GET.get('role', '')
    return render(request, 'accounts/signup.html', {'role': role})

def home(request):
    return render(request, 'accounts/home.html')

def services(request):
    return render(request, 'accounts/services.html')

def experts(request):
    return render(request, 'accounts/experts.html')
