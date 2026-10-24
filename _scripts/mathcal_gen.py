'''
generate math calendar pages from templates
outputs a main page and a directory with month pages (in current work dir)
mathcal_gen.py <year>
'''

import calendar
import datetime
import jinja2
import os
import sys

MONTHS_SHORT = (
    'Jan','Feb','Mar','Apr','May','Jun',
    'Jul','Aug','Sep','Oct','Nov','Dec'
)
MONTHS_FULL = (
    'January','February','March','April','May','June',
    'July','August','September','October','November','December'
)

def compute_month_day_count(year:int,month_index:int) -> int:
    '''
    number of days in a month
    '''
    return calendar.monthrange(year,month_index+1)[1]

def compute_month_day_counts(year:int) -> list[int]:
    '''
    array of how many days are in each month of the year
    '''
    return [compute_month_day_count(year,month_index) for month_index in range(12)]

def create_main_file_path(year:int) -> str:
    '''
    path for the main page
    '''
    return f'{year}-math-calendar.html'

def create_month_dir_path(year:int) -> str:
    return f'{year}-math-calendar'

def create_month_file_path(year:int,month_index:int) -> str:
    '''
    file path for a single month
    '''
    return f'{year}-math-calendar/{month_index+1:02d}-{MONTHS_SHORT[month_index].lower()}.html'

def create_month_file_paths(year:int) -> list[str]:
    '''
    list of file paths for the months
    '''
    return [create_month_file_path(year,month_index) for month_index in range(12)]

def create_month_table(year:int,month_index:int,in_month_page:bool) -> list[list[tuple[str,str]]]:
    '''
    create the table for a single month
    use in_month_page=True for only the anchor links (on month pages)
    use in_month_page=False for the relative path (on main page)
    '''
    month_short = MONTHS_SHORT[month_index]
    month_path = create_month_file_path(year,month_index)

    day_table = calendar.monthcalendar(year,month_index+1)
    while len(day_table) < 6:
        day_table.append([0,0,0,0,0,0,0])
    assert len(day_table) == 6

    return [
        [
            ('&nbsp;','') if day == 0
            else (
                f'{day:02d}',
                f'#{month_short.lower()}{day:02d}' if in_month_page
                else f'{month_path}#{month_short.lower()}{day:02d}'
            )
            for day in row
        ]
        for row in day_table
    ]

def create_month_tables(year:int,in_month_page:bool) -> list[list[list[tuple[str,str]]]]:
    '''
    create the tables which will display the calendar months
    returned array is 12x6x7 (6 rows 7 cols for each month)
    each value is (text,link), link may be empty to display text only
    use in_month_page=True for only the anchor links (on month pages)
    use in_month_page=False for the relative path (on main page)
    '''
    return [create_month_table(year,month_index,in_month_page) for month_index in range(12)]

def render_main(year:int):
    '''
    renders the main page
    '''

    # setup jinja environment
    jinja_env = jinja2.Environment(
        lstrip_blocks=True,
        trim_blocks=True,
        loader=jinja2.FileSystemLoader('.')
    )

    # load template and render
    main_template = jinja_env.get_template('mathcal_main.jinja')
    with open(f'{create_main_file_path(year)}.tmp','w',encoding='utf-8') as file:
        print('writing',create_main_file_path(year))
        file.write(main_template.render(
            year=year,
            data=list(zip(
                create_month_tables(year,False),
                MONTHS_FULL,
                create_month_file_paths(year)
            ))
        ))
        file.write('\n')
    os.replace(f'{create_main_file_path(year)}.tmp',
            create_main_file_path(year))

def render_month(year:int,month_index:int):
    '''
    renders a month page
    '''

    # setup jinja environment
    jinja_env = jinja2.Environment(
        lstrip_blocks=True,
        trim_blocks=True,
        loader=jinja2.FileSystemLoader('.')
    )

    # array with the day identifiers, example ('jan01','Jan 01','2026_JAN_01')
    month_short = MONTHS_SHORT[month_index]
    month_day_count = compute_month_day_count(year,month_index)
    days = [
        (
            f'{month_short.lower()}{day:02d}',
            f'{month_short} {day:02d}',
            f'{year}_{month_short.upper()}_{day:02d}'
        )
        for day in range(1,month_day_count+1)
    ]

    # load template and render
    month_template = jinja_env.get_template('mathcal_month.jinja')
    with open(f'{create_month_file_path(year,month_index)}.tmp','w',encoding='utf-8') as file:
        print('writing',create_month_file_path(year,month_index))
        file.write(month_template.render(
            year=year,
            month_full=MONTHS_FULL[month_index],
            month_short=MONTHS_SHORT[month_index],
            month_table=create_month_table(year,month_index,True),
            day_data=days,
            main_link=f'../{create_main_file_path(year)}',
            today=str(datetime.date.today())
        ))
        file.write('\n')
    os.replace(f'{create_month_file_path(year,month_index)}.tmp',
            create_month_file_path(year,month_index))

def main():
    calendar.setfirstweekday(calendar.MONDAY)
    year = int(sys.argv[1])
    assert 1900 <= year < 2200
    os.makedirs(create_month_dir_path(year),exist_ok=True)

    render_main(year)
    for month_index in range(12):
        render_month(year,month_index)

if __name__ == '__main__':
    main()
