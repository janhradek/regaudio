def totaltostr(total, edit=False):
    mm,ss,ms = totaltotime(total)
    return timetostr(mm,ss,ms, edit)

def timetostr(mm, ss, ms, edit=False):
    if edit:
        return "{0:02d}:{1:02d}:{2:02d}".format(mm,ss,ms)
    else: # view only
        return "{0:02d}:{1:02d}".format(mm, ss if ms < 500 else ss + 1)

def strtototal(timestr):
    mm,ss,ms,ok = strtotime(timestr)
    if not ok:
        return 0, False
    else:
        return timetototal(mm,ss,ms), True

def strtotime(timestr):
    """
    two valid inputs MM:SS:MS and MM:SS
    return mm,ss,ms,ok
    """
    fail = (0,0,0,False)
    spl = timestr.split(":")

    if len(spl) < 2 or len(spl) > 3:
        return fail
    try:
        mm = int(spl[0])
        ss = int(spl[1])
        ms = int(spl[2]) if len(spl) == 3 else 0
        return mm,ss,ms,True
    except:
        return fail

def totaltotime(total):
    """ ii is the total miliseconds """
    ms = total % 1000
    total = total // 1000
    ss = total % 60
    mm = total // 60
    return (mm,ss,ms)

def timetototal(mm, ss, ms):
    return (mm * 60 + ss) * 1000 + ms

