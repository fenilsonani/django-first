from django.contrib import messages
from django.shortcuts import redirect, render
from django.db.models import Q
from .models import Room, Topic, Message
from django.contrib.auth.decorators import login_required
from .forms import RoomForm,UserForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login,logout
# import HTTPResponse
from django.http import HttpResponse
# Create your views here.

# rooms = [
#     {
#         "id": 1,
#         "name": 'Room 1',
#     },
#     {
#         "id": 2,
#         "name": 'Room 2',
#     },
#     {
#         "id": 3,
#         "name": 'Room 3',
#     },
# ]





# login view
def loginUser(request):
    if request.user.is_authenticated:
        messages.info(request, 'You are already logged in')
        return redirect('home')

    page = 'login'
    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username OR password is incorrect')

    context = {'page': page}
    return render(request, 'base/login_register.html', context)




# logout view
def logoutUser(request):
    logout(request)
    return redirect('home')




# user registration view
def registerUser(request):
    form = UserCreationForm()
    if request.user.is_authenticated:
        messages.info(request, 'You are already logged in')
        return redirect('home')
    
    if request.method =="POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request,user)
            return redirect('home')
        else:
            messages.error(request, 'An error has occured during registration')


    return render(request, 'base/login_register.html',{'form':form} )






# home view
def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    rooms = Room.objects.filter(Q(name__icontains=q) | Q(description__icontains=q) | Q(
        topic__name__icontains=q) | Q(host__username__icontains=q))
    topics = Topic.objects.all()

    room_count = rooms.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))

    context = {'rooms': rooms, 'topic': topics ,'room_count':room_count,'room_messages':room_messages}
    return render(request, 'base/home.html', context)





# user profile view
def userProfile(request,pk):
    user = User.objects.get(id=pk)
    rooms  = user.room_set.all()
    topics = Topic.objects.all()
    room_messages = Message.objects.filter(user=user)
    context={ 'user':user , 'rooms':rooms , 'topic': topics  ,'room_messages':room_messages}
    return render(request, 'base/profile.html', context)






# room view
def room(request, pk):
    room = Room.objects.get(id=pk)
    messages = room.message_set.all().order_by('-created')
    participants=room.participants.all()
    if request.method=='POST':
        message = Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)

    context = {'room': room ,'messages1':messages ,'participants':participants}
    return render(request, 'base/room.html', context)





# room create view
@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':

        topic_name = request.POST.get('topic')
        topic = Topic.objects.get_or_create(name=topic_name)

        # print(request.POST)
        # form = RoomForm(request.POST)
        Room.objects.create(
            host=request.user,
            name=request.POST.get('name'),
            description=request.POST.get('description'),
            topic=topic
        )
        return redirect('home')
    form = RoomForm()
    context = {'form': form , 'topic': topics}
    return render(request, 'base/room_form.html', context)





# update room view
@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()
    if request.user != room.host:
        return redirect('home')


    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect('home')
    context = {'form': form , 'topic': topics}
    return render(request, 'base/room_form.html', context)





# delete room view
@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    context = {'item': room}
    return render(request, 'base/delete.html', context)





# delete message view
@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse('Your are not allowed here!!')

    if request.method == 'POST':
        message.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': message})

@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)
    return render(request, 'base/update_user.html', {'form': form})