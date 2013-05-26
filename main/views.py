import re
from datetime import datetime

from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render_to_response

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
from django.shortcuts import render, get_object_or_404, redirect
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
    params['userer'] = user
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
    if anonymous:
        return redirect('/')
    user = request.user.get_profile()

    if request.method == 'POST' and not anonymous:
        params['data'] = request.POST
        if 'name' in request.POST and 'description' in request.POST and 'category' in request.POST:
            name = request.POST['name']
            description = request.POST['description']
            category = request.POST['category']
            service = Service()
            service.name = name
            service.description = description
            service.category = category
            service.owner = user
            service.save()
            user.addPK(category, service.pk)

        if 'skillsTeachRemove' in request.POST:
            pk = request.POST['skillsTeachRemove']
            service = Service.objects.get(pk=pk)
            service.delete()
        if 'skillsLearnRemove' in request.POST:
            pk = request.POST['skillsLearnRemove']
            service = Service.objects.get(pk=pk)
            service.delete()
        if 'servicesOfferedRemove' in request.POST:
            pk = request.POST['servicesOfferedRemove']
            service = Service.objects.get(pk=pk)
            service.delete()
        if 'servicesWantedRemove' in request.POST:
            pk = request.POST['servicesWantedRemove']
            service = Service.objects.get(pk=pk)
            service.delete()

        if 'city' in request.POST:
            user.city = request.POST['city']
            user.save()
        if 'state' in request.POST:
            user.state = request.POST['state']
            user.save()
        if 'phone' in request.POST:
            user.phone = request.POST['phone']
            user.save()

    params['skillsTeach'] = user.getObjects(user.skillsTeach)
    params['skillsLearn'] = user.getObjects(user.skillsLearn)
    params['servicesOffered'] = user.getObjects(user.servicesOffered)
    params['servicesWanted'] = user.getObjects(user.servicesWanted)
    return render(request, 'edit.html', params)

def service_view(request, sid):
    params = {'service': Service.objects.get(pk=sid)}
    return render(request, 'service.html', params)

@csrf_exempt
def login_view(request):
    state = "Please log in below..."
    username = password = ''
    if request.user.is_authenticated():
        return redirect('/')
    if request.POST:
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                state = "You're successfully logged in!"
                return redirect('/')
            else:
                state = "Your account is not active, please contact the site admin."
        else:
            state = "Your username and/or password were incorrect."

    return render(request, 'auth.html',{'state':state, 'username': username})

def logout_view(request):
    logout(request)
    return redirect('/')

from django.contrib.auth.models import User

@csrf_exempt
def register_view(request):
    password = request.POST.get('newpassword')
    if password != request.POST.get('passcheck'):
        password = None
        return HttpResponse('passwords dont match! auth failed!')
    user = User()
    user.email = request.POST.get('email')
    user.username = user.email
    user.set_password(password)
    user.first_name = request.POST.get('first')
    user.last_name = request.POST.get('last')
    user.save()
    
    userProfile = UserProfile()
    userProfile.user = user
    userProfile.state = request.POST.get('state')
    userProfile.city = request.POST.get('city')
    userProfile.phone = request.POST.get('phone')
    userProfile.save()
    return redirect('/')

