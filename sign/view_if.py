from django.http import JsonResponse
from sign.models import Event, Guest
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db.utils import IntegrityError
import time


# 添加发布会接口
def add_event(request):
    eid = request.POST.get('eid', '')  # 发布会id
    name = request.POST.get('name', '')  # 发布会标题
    limit = request.POST.get('limit', '')  # 限制人数
    status = request.POST.get('status', '')  # 状态
    address = request.POST.get('address', '')  # 地址
    start_time = request.POST.get('start_time', '')  # 发布会时间

    if not eid and name and limit and address and start_time:
        return JsonResponse({'status': 10021,
                             'message': 'parameter error'})

    result = Event.objects.filter(id=eid)
    if result:
        return JsonResponse({'status': 10022,
                             'message': 'event id already exist'})

    result = Event.objects.filter(name=name)
    if result:
        return JsonResponse({'status': 10023,
                             'message': 'event name already exist'})

    if not status:
        status = 1

    try:
        Event.objects.create(id=eid, name=name, limit=limit, address=address,
                             status=int(status), start_time=start_time)
    except ValidationError:
        error = 'start_time format error. It must be in YYYY-MM-DD HH:MM:SS format.'
        return JsonResponse({'status': 10024,
                             'message': error})
    return JsonResponse({'status': 200,
                         'message': 'add event success'})


# 查询发布会接口
def get_event_list(request):
    eid = request.GET.get('eid', '')  # 发布会id
    name = request.GET.get('name', '')  # 发布会标题

    if not eid or name:
        return JsonResponse({'status': 10021,
                             'message': 'parameter error'})

    if eid:
        event = {}
        try:
            result = Event.objects.get(id=eid)
        except ObjectDoesNotExist:
            return JsonResponse({'status': 10022,
                                 'message': 'query result is empty'})
        else:
            event['name'] = result.name
            event['limit'] = result.limit
            event['status'] = result.status
            event['address'] = result.address
            event['start_time'] = result.start_time
            return JsonResponse({'status': 200,
                                 'message': 'success',
                                 'data': event})

    if name:
        data = []
        results = Event.objects.filter(name__contains=name)
        if results:
            for r in results:
                event = {}
                event['name'] = r.name
                event['limit'] = r.limit
                event['status'] = r.status
                event['address'] = r.address
                event['start_time'] = r.start_time
                data.append(event)
            return JsonResponse({'status': 200,
                                 'message': 'success',
                                 'data': data})
        else:
            return JsonResponse({'status': 10022,
                                 'message': 'query result is empty'})


# 添加嘉宾接口
def add_guest(request):
    eid = request.POST.get('eid', '')  # 关联发布会id
    realname = request.POST.get('realname', '')  # 姓名
    phone = request.POST.get('phone', '')  # 手机号
    email = request.POST.get('email', '')  # 邮箱

    if not eid and realname and phone:
        return JsonResponse({'status': 10021,
                             'message': 'parameter error'})

    result = Event.objects.filter(id=eid)
    if not result:
        return JsonResponse({'status': 10022,
                             'message': 'event id null'})

    result = Event.objects.get(id=eid).status
    if not result:
        return JsonResponse({'status': 10023,
                             'message': 'event status is not available'})

    event_limit = Event.objects.get(id=eid).limit  # 发布会限制人数
    guest_limit = len(Guest.objects.filter(event_id=eid))  # 发布会已添加的嘉宾数

    if guest_limit >= event_limit:
        return JsonResponse({'status': 10024,
                             'message': 'event number is full'})

    event_time = Event.objects.get(id=eid).start_time  # 发布会时间
    e_time = int(time.mktime(time.strptime(str(event_time), '%Y-%m-%d %H:%M:%S')))  # 发布会时间戳
    n_time = int(time.time())  # 当前时间戳

    if n_time >= e_time:
        return JsonResponse({'status': 10025,
                             'message': 'event has started'})

    try:
        Guest.objects.create(realname=realname, phone=int(phone), email=email,
                             sign=0, event_id=int(eid))
    except IntegrityError:
        return JsonResponse({'status': 10026,
                             'message': 'the event guest phone number repeat'})
    return JsonResponse({'status': 200,
                         'message': 'add guest success'})


# 嘉宾签到接口
def user_sign(request):
    eid = request.POST.get('eid', '')  # 发布会id
    phone = request.POST.get('phone', '')  # 嘉宾手机号

    if not eid and phone:
        return JsonResponse({'status': 10021,
                             'message': 'parameter error'})

    result = Event.objects.filter(id=eid)
    if not result:
        return JsonResponse({'status': 10022,
                             'message': 'event id full'})

    result = Event.objects.get(id=eid).status
    if not result:
        return JsonResponse({'status': 10023,
                             'message': 'event status is not available'})

    event_time = Event.objects.get(id=eid).start_time  # 发布会时间
    e_time = int(time.mktime(time.strptime(str(event_time), '%Y-%m-%d %H:%M:%S')))  # 发布会时间戳
    n_time = int(time.time())  # 当前时间戳

    if n_time >= e_time:
        return JsonResponse({'status': 10024,
                             'message': 'event has started'})

    result = Guest.objects.filter(phone=phone)
    if not result:
        return JsonResponse({'status': 10025,
                             'message': 'user phone full'})

    result = Guest.objects.filter(event_id=eid, phone=phone)
    if not result:
        return JsonResponse({'status': 10026,
                             'message': 'user did not participate in the conference'})

    result = Guest.objects.get(event_id=eid, phone=phone).sign
    if result:
        return JsonResponse({'status': 10027,
                             'message': 'user has sign in'})
    else:
        Guest.objects.filter(event_id=eid, phone=phone).update(sign='1')
        return JsonResponse({'status': 200,
                             'message': 'sign success'})
