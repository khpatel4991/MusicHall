"""
Definition of views.
"""

from django.shortcuts import render
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.template import RequestContext, loader
from datetime import datetime
from .models import *
from django.core import serializers

def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/index.html',
        context_instance = RequestContext(request,
        {
            'title':'Home Page',
            'year':datetime.now().year,
        })
    )

def contact(request):
    """Renders the contact page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/contact.html',
        context_instance = RequestContext(request,
        {
            'title':'Contact',
            'message':'Your contact page.',
            'year':datetime.now().year,
        })
    )

def about(request):
    """Renders the about page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/about.html',
        context_instance = RequestContext(request,
        {
            'title':'About',
            'message':'Your application description page.',
            'year':datetime.now().year,
        })
    )

def test(request):
    topSongs = Songs.objects.order_by('-crawlDelta')[:5]
    #data = serializers.serialize('json', latest_question_list)
    print topSongs
    #return JsonResponse(latest_question_list, safe = False)
    #return HttpResponse(data, content_type='application/json')
    #template = loader.get_template('app/test.html')
    context = RequestContext(request, {
        'topSongs': topSongs,
    })
    return render(request, 'app/test.html', context)
