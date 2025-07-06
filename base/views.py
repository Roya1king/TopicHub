from django.shortcuts import render,redirect
from django.db.models import Q
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Room
from .models import Topic,Message
from .forms import RoomForm, UserForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone
from datetime import timedelta

# Create your views here.
# rooms = [
#     {'id': 1, 'name': "Let's play Holi"},
#     {'id': 2, 'name': "Let's play Cricket"},
#     {'id': 3, 'name': "Let's play Diwali"}
# ]

def ready(self):
    import base.signals  # assuming your app is named "base"


def loginPage(request):
    page='login'
    if request.user.is_authenticated:
        # return HttpResponse("Already logged In.")
        return redirect('home')


    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            user=User.objects.get(username=username)
        except:
            messages.error(request, "User Doesnot exists.")
        user = authenticate(request,username=username,password=password)
        if user is not None:
            login(request,user)
            flag=True
            messages.success(request, "You have successfully logged in!")
            return redirect('home')
        else:
            messages.error(request, "User or Password Incorrect.")
    context={'page':page}
    return render(request, "base/login_register.html", context)


def logoutuse(request):
    logout(request)
    return redirect('home')

# def registerPage(request):
#     page='register'
#     form = UserCreationForm()
#     context={'form':form,'page':page}
#     return render(request, "base/login_register.html",context)

def registerPage(request):
    page = 'register'
    form = UserCreationForm()

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "An error occurred during registration.")

    context = {'form': form, 'page': page}
    return render(request, "base/login_register.html", context)


# def home(request):
#     q=request.GET.get('q') if request.GET.get('q')!=None else ''
#     rooms=Room.objects.filter(
#         Q(topic__name__icontains=q) |
#         Q(description__icontains=q) |
#         Q(name__icontains=q)
#     )
#     user = request.user
#     user_rooms = Room.objects.filter(participants=user)
#     topics=Topic.objects.all()
#     room_count=rooms.count()
#     now = timezone.now()

#     # room_messages=Message.objects.all().order_by('-created')
#     room_messages = Message.objects.filter(
#         Q(room__in=user_rooms) | Q(user=user),
#         created__gte=now - timedelta(days=1)
#     ).distinct().order_by('-created')

#     content = {'rooms': rooms, 'topics': topics,'room_count':room_count,'room_messages':room_messages}
#     return render(request, 'base/home.html', content)

def home(request):
    q = request.GET.get('q') if request.GET.get('q') is not None else ''
    
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(description__icontains=q) |
        Q(name__icontains=q)
    )
    
    topics = Topic.objects.all()
    room_count = rooms.count()
    now = timezone.now()

    room_messages = Message.objects.none()  # Initialize with an empty queryset

    if request.user.is_authenticated:
        user = request.user
        user_rooms = Room.objects.filter(participants=user)
        room_messages = Message.objects.filter(
            Q(room__in=user_rooms) | Q(user=user),
            created__gte=now - timedelta(days=1)
        ).distinct().order_by('-created').filter(Q(room__name__icontains=q))

    content = {
        'rooms': rooms, 
        'topics': topics, 
        'room_count': room_count, 
        'room_messages': room_messages
    }
    return render(request, 'base/home.html', content)

def room(request,pk):
    room = Room.objects.get(id=pk)
    messages=room.message_set.all().order_by('-created')
    participants=room.participants.all()
    if request.method == 'POST':
        message=Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room',pk=room.id)


    context = {"room":room, "messages":messages,"participants":participants}
    return render(request, 'base/room.html',context)

# @login_required(login_url='login')      
# def createroom(request):
#     form=RoomForm()
#     topics=Topic.objects.all()
#     if request.method=='POST':
#         form=RoomForm(request.POST)
#         if form.is_valid():
#             room=form.save(commit='False')
#             room.host=request.user
#             room.save()
#             return redirect('home')

#     context={'form':form,"topics":topics}
#     return render(request,'base/room_form.html',context)

@login_required(login_url='login')
def createroom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)

        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description'),
        )
        return redirect('home')

    context = {'form': form, 'topics': topics}
    return render(request,'base/room_form.html',context)

# def updateroom(request,pk):
#     room=Room.objects.get(id=pk)
#     form=RoomForm(initial=room)
#     context={'form':form}
#     return render (request,'base/room_form.html',context)
@login_required(login_url='login')   
def updateroom(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse("Go to hell")

    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = RoomForm(instance=room)

    context = {'form': form}
    return render(request, 'base/room_form.html', context)

def userProfile(request,username):
    user=User.objects.get(username=username)
    rooms=user.room_set.all()
    room_messages=user.message_set.all()
    topics = Topic.objects.all()
    context={'user': user,'rooms':rooms,'room_messages':room_messages,'topics':topics}
    return render(request,'base/profile.html',context)

@login_required(login_url='login')   
def deleteroom(request,pk):
    room=Room.objects.get(id=pk)
    if request.user != room.host:
        return HttpResponse("Go to hell")
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request,'base/delete.html',{'obj':room})


@login_required(login_url='login')   
def deletemessage(request,pk):
    message=Message.objects.get(id=pk)
    room = message.room
    if request.user != message.user and request.user != room.host:
        return HttpResponse("Go to hell")
    if request.method == 'POST':
        message.delete()
        return redirect('room',pk=room.pk)
    return render(request,'base/delete.html',{'obj':message})

@login_required(login_url='login')
def updateUser(request):
    profile = request.user.profile
    form = UserForm(instance=profile)

    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('user-profile', username=request.user.username)

    return render(request, 'base/update-user.html', {'form': form})


def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=q)  # Corrected the query

    return render(request, 'base/topics.html', {'topics': topics})



def activityPage(request):
    room_messages = Message.objects.filter(created__gte=datetime.now()-timedelta(days=1)) 
    
    # Optional: Order by the latest messages first
    room_messages = room_messages.order_by('-created')
    
    return render(request, 'base/activity.html', {'room_messages': room_messages})
