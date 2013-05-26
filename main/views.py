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

def search_view(request):
    params = {}
    query = request.GET.get('q')
    params['q'] = query

    results = Service.objects.filter(name__icontains=query)
    params['results'] = results
    
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
