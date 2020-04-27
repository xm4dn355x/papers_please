from django.shortcuts import render

def handler404(request, exception):
    return render(request, 'errs/404.html')

def handler403(request, exception):
    return render(request, 'errs/403.html')

def handler500(request):
    return render(request, 'errs/500.html')