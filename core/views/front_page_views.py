from django.shortcuts import render_to_response, render, redirect

def index(request):
    """
    :param request:
    :return: The home page
    """
    return render(request, 'core/index.html', {'stats': 'hello'})