from master.number_parser import *

ASK = 0
RE_ASK = 1

def parse_time1 (params, args):
    return parse_time_(params=params, time_name='time1', time_hour='time1_1', time_minute='time1_2', args=args)

def parse_time2 (params, args):
    return parse_time_(params=params, time_name='time2', time_hour='time2_1', time_minute='time2_2', args=args)

def parse_time_ (params, time_name, time_hour, time_minute, args):
    is_minute_time = (time_hour in params and time_minute in params)

    if not time_name in params and not is_minute_time:
        return ASK

    if is_minute_time:
        params[time_name] = parse_time(params[time_hour], params[time_minute], args.language)
        if params[time_name] is None:
            return RE_ASK
    else:
        params[time_name] = get_text_digit(params[time_name], args.language)
        if params[time_name] is None:
            return RE_ASK

    # Correct format
    if not is_minute_time and not params[time_name].endswith(':00:00'):
        params[time_name] += ':00:00'
    
    return params