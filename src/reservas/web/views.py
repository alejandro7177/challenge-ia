from django.shortcuts import render, redirect
from django.contrib import messages
from reservas.validation import load_inventory
from reservas.service import (
    check_availability,
    create_reservation,
    cancel_reservation,
    list_reservations
)
from reservas.models import ValidationError, ConflictError, NotFoundError

def index_view(request):
    inventory = load_inventory()
    return render(request, 'reservas/index.html', {'inventory': inventory})

def unit_list_view(request):
    inventory = load_inventory()
    return render(request, 'reservas/unit_list.html', {'inventory': inventory})

def availability_view(request):
    inventory = load_inventory()
    result = None
    checked_data = None
    if request.method == 'GET' and 'unit_id' in request.GET and 'start' in request.GET and 'end' in request.GET:
        unit_id = request.GET.get('unit_id')
        start_str = request.GET.get('start')
        end_str = request.GET.get('end')
        checked_data = {'unit_id': unit_id, 'start': start_str, 'end': end_str}
        try:
            is_free = check_availability(unit_id, start_str, end_str)
            result = {'success': True, 'is_free': is_free}
        except (ValidationError, NotFoundError) as e:
            result = {'success': False, 'error': str(e)}

    return render(request, 'reservas/availability.html', {
        'inventory': inventory,
        'result': result,
        'checked_data': checked_data
    })

def reserve_view(request):
    inventory = load_inventory()
    if request.method == 'POST':
        unit_id = request.POST.get('unit_id')
        requester = request.POST.get('requester')
        start = request.POST.get('start')
        end = request.POST.get('end')
        try:
            res = create_reservation(unit_id, requester, start, end)
            messages.success(request, f"¡Reserva creada exitosamente! ID: {res.id}")
            return redirect('reservation_list')
        except (ValidationError, ConflictError, NotFoundError) as e:
            messages.error(request, str(e))
    
    return render(request, 'reservas/reserve.html', {'inventory': inventory})

def reservation_list_view(request):
    unit_id = request.GET.get('unit') or None
    status = request.GET.get('status') or None
    reservations = list_reservations(unit_id=unit_id, status=status)
    inventory = load_inventory()
    return render(request, 'reservas/list.html', {
        'reservations': reservations,
        'inventory': inventory,
        'selected_unit': unit_id,
        'selected_status': status
    })

def cancel_view(request, reservation_id):
    if request.method == 'POST':
        try:
            cancel_reservation(reservation_id)
            messages.success(request, f"Reserva {reservation_id} cancelada correctamente.")
        except (ValidationError, NotFoundError) as e:
            messages.error(request, str(e))
    return redirect('reservation_list')
