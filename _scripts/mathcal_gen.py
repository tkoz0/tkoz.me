# make a template for math calendar

from datetime import date
import os

import jinja2

year = 2025
months_short = ('Jan','Feb','Mar','Apr','May','Jun',
                'Jul','Aug','Sep','Oct','Nov','Dec')
months_full = ('January','February','March','April','May','June',
               'July','August','September','October','November','December')

os.makedirs(f'{year}-math-calendar',exist_ok=True)

month_tables: list[list[list[tuple[str,str]]]] = []
month_days: list[int] = []

for m,mt in enumerate(months_short):
    mtl = mt.lower()
    # ensure a nonbreaking spacee in each row, may be overwritten
    # each is a tuple (text,link)
    table = [[('&nbsp;',''),*(('','') for _ in range(6))] for _ in range(6)]
    d = date(year,m+1,1)
    r = 0
    c = d.isoweekday()-1 # starting on monday=0
    while True:
        link = f'{year}-math-calendar/{d.month:02d}-{mtl}.html#{mtl}{d.day:02d}'
        if table[r][0] == ('&nbsp;',''):
            table[r][0] = ('','')
        table[r][c] = (f'{d.day:02d}',link)
        c += 1
        if c == 7:
            c = 0
            r += 1
        try:
            d = d.replace(day=d.day+1)
        except:
            month_days.append(d.day)
            break
    month_tables.append(table)
    print(mt,table)

month_links = [f'{year}-math-calendar/{m+1:02d}-{mt.lower()}.html'
               for m,mt in enumerate(months_short)]

jenv = jinja2.Environment(lstrip_blocks=True,trim_blocks=True,
                          loader=jinja2.FileSystemLoader('.'))
jtemp = jenv.get_template('mathcal_main.jinja')

with open(f'{year}-math-calendar.html','w') as f:
    f.write(jtemp.render(year=year,
                         data=zip(month_tables,months_full,month_links)))

jtemp = jenv.get_template('mathcal_month.jinja')

# adjust links for month pages
for month_table in month_tables:
    for week_row in month_table:
        for i in range(len(week_row)):
            text,link = week_row[i]
            j = link.find('#')
            link = link[j:]
            week_row[i] = (text,link)

for m,mt in enumerate(months_full):
    ms = months_short[m]
    md = month_days[m]
    days = ((f'{ms.lower()}{d:02d}',f'{ms} {d:02d}') for d in range(1,md+1))
    with open(month_links[m],'w') as f:
        f.write(jtemp.render(year=year,
                             month_full=mt,
                             month_table=month_tables[m],
                             day_data=days))
