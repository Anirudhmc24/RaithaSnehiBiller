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

def add_next_month():
    import datetime
    from config.settings import MONTHS
    last_mk = MONTHS[-1][0]
    m, y = int(last_mk.split('-')[0]), int(last_mk.split('-')[1])
    m += 1
    if m > 12: m = 1; y += 1
    next_mk = f'{m:02d}-{y}'
    next_fp = f'{m:02d}{y}'
    next_name = datetime.date(y, m, 1).strftime('%B %Y')

    with open('config/settings.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()

    in_months = False
    in_fp = False
    new_lines = []
    for line in lines:
        if line.startswith('MONTHS = ['):
            in_months = True
        elif in_months and line.strip() == ']':
            new_lines.append(f'    ("{next_mk}", "{next_name}"),\n')
            in_months = False
        
        if line.startswith('MONTH_FP = {'):
            in_fp = True
        elif in_fp and line.strip() == '}':
            new_lines.append(f'    "{next_mk}":"{next_fp}",\n')
            in_fp = False
            
        new_lines.append(line)

    with open('config/settings.py', 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
