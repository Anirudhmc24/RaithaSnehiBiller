import calendar

def r2(n):   
    return round((n or 0)*100)/100

def fmtc(n): 
    return f"₹{r2(n):,.2f}"

def parse_mk(mk):
    m, y = mk.split("-")
    return int(m), int(y)

def ld(m, y): 
    return calendar.monthrange(y, m)[1]
