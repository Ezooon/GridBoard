def ffloat(arg):
    try:
        return float(arg)
    except:
        return 0


def iffloat(arg, to=1):
    i = str(arg).find('.')
    if i > 0:
        if int(str(arg)[i+1:i+to+1]) > 0:  # if float
            return round(float(arg), to)
    return int(float(arg))
