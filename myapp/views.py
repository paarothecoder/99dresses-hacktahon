from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.http import JsonResponse
from .models import ClothingItem, Wishlist, Message
from django.contrib.auth.models import User
from django.db.models import Q

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def home(request):
    user_items = ClothingItem.objects.filter(user=request.user).order_by('-created_at')
    other_items = ClothingItem.objects.exclude(user=request.user).order_by('-created_at')
    
    query = request.GET.get('q')
    search_results = other_items.filter(Q(name__icontains=query) | Q(brand__icontains=query)) if query else other_items

    # Chat Inbox Logic: Find people you have messaged
    sent_to = Message.objects.filter(sender=request.user).values_list('receiver', flat=True)
    received_from = Message.objects.filter(receiver=request.user).values_list('sender', flat=True)
    chat_partner_ids = set(list(sent_to) + list(received_from))
    chat_partners = User.objects.filter(id__in=chat_partner_ids)

    context = {
        'items': other_items,
        'search_results': search_results,
        'user_items': user_items,
        'wishlist_items': Wishlist.objects.filter(user=request.user).select_related('item'),
        'chat_partners': chat_partners,
        'query': query
    }
    return render(request, 'index.html', context)

@login_required
def chat_room(request, user_id):
    partner = get_object_or_404(User, id=user_id)
    if request.method == "POST":
        content = request.POST.get('content')
        if content:
            Message.objects.create(sender=request.user, receiver=partner, content=content)
        return redirect('chat_room', user_id=user_id)

    messages = Message.objects.filter(
        (Q(sender=request.user) & Q(receiver=partner)) | 
        (Q(sender=partner) & Q(receiver=request.user))
    )
    return render(request, 'chat_room.html', {'partner': partner, 'messages': messages})

@login_required
def start_buy_chat(request, item_id):
    item = get_object_or_404(ClothingItem, id=item_id)
    if item.user != request.user:
        Message.objects.get_or_create(
            sender=request.user,
            receiver=item.user,
            content=f"Hi! I'm interested in buying your {item.name} for ${item.price}."
        )
    return redirect('chat_room', user_id=item.user.id)

@login_required
def item_detail(request, item_id):
    item = get_object_or_404(ClothingItem, id=item_id)
    return render(request, 'detail.html', {'item': item})
@login_required
def delete_item(request, item_id):
    if request.method == "POST":
        item = get_object_or_404(ClothingItem, id=item_id, user=request.user)
        item.delete()
        return JsonResponse({'status': 'deleted'})
    return redirect('home')
@login_required
def upload_item(request):
    if request.method == 'POST':
        ClothingItem.objects.create(
            user=request.user,
            name=request.POST.get('name'),
            brand=request.POST.get('brand'),
            price=request.POST.get('price'),
            image=request.FILES.get('image')
        )
        return JsonResponse({'status': 'success'})
    return redirect('home')

@login_required
def toggle_wishlist(request, item_id):
    if request.method == 'POST':
        item = get_object_or_404(ClothingItem, id=item_id)
        wish_item, created = Wishlist.objects.get_or_create(user=request.user, item=item)
        if not created:
            wish_item.delete()
            return JsonResponse({'status': 'removed'})
        return JsonResponse({'status': 'added'})