import re
from datetime import datetime

from django.db.models import Q

def normalize_query(query_string,
                    findterms=re.compile(r'"([^"]+)"|(\S+)').findall,
                    normspace=re.compile(r'\s{2,}').sub):
    ''' Splits the query string in invidual keywords, getting rid of unecessary spaces
        and grouping quoted words together.
        Example:
        
        >>> normalize_query('  some random  words "with   quotes  " and   spaces')
        ['some', 'random', 'words', 'with quotes', 'and', 'spaces']
    
    '''
    return [normspace(' ', (t[0] or t[1]).strip()) for t in findterms(query_string)] 

def get_query(query_string, search_fields):
    ''' Returns a query, that is a combination of Q objects. That combination
        aims to search keywords within a model by testing the given search fields.
    
    '''
    query = None # Query to search for every search term        
    terms = normalize_query(query_string)
    for term in terms:
        or_query = None # Query to search for a given term in each field
        for field_name in search_fields:
            q = Q(**{"%s__icontains" % field_name: term})
            if or_query is None:
                or_query = q
            else:
                or_query = or_query | q
        if query is None:
            query = or_query
        else:
            query = query & or_query
    return query


from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from main.models import Service, UserProfile

def home(request):
    return render(request, 'home.html')

def profile_view(request, uid):
    params = {}
    user = get_object_or_404(UserProfile, pk=uid)
    params['skillsTeach'] = user.getObjects(user.skillsTeach)
    params['skillsLearn'] = user.getObjects(user.skillsLearn)
    params['servicesOffered'] = user.getObjects(user.servicesOffered)
    params['servicesWanted'] = user.getObjects(user.servicesWanted)
    return render(request, 'profile.html', params)


# http://julienphalip.com/post/2825034077/adding-search-to-a-django-site-in-a-snap
def search_view(request):
    start = datetime.now()
    query_string = ''
    found_entries = None
    params = {}
    if ('q' in request.GET) and request.GET['q'].strip():
        query_string = request.GET.get('q')
        
        entry_query = get_query(query_string, ['name', 'description',
            'category'])
        
        found_entries = Service.objects.filter(entry_query).order_by('-name')
    params['q'] = query_string
    params['results'] = found_entries
    params['latency'] = (datetime.now() - start).total_seconds()
    params['n'] = len(found_entries)
    return render(request, 'search.html', params)

@csrf_exempt
def edit_view(request):
    params = {}
    anonymous = request.user.is_anonymous()
    user = request.user.get_profile()
    params['anonymous'] = anonymous

    if request.method == 'POST' and not anonymous:
        params['data'] = request.POST
        if 'skillsTeach' in request.POST:
            skillsTeach = request.POST['skillsTeach']
        if 'skillsLearn' in request.POST:
            skillsLearn = request.POST['skillsLearn']
        if 'servicesOffered' in request.POST:
            servicesOffered = request.POST['servicesOffered']
        if 'servicesWanted' in request.POST:
            servicesWanted = request.POST['servicesWanted']
    return render(request, 'edit.html', params)

def service_view(request, sid):
    params = {'service': Service.objects.get(pk=sid)}
    return render(request, 'service.html', params)
