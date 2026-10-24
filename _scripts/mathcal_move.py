'''
moves math calendar content (per month pages) to new generated pages
mathcal_move.py <old_file> <new_file>
old_file is page with existing content
new_file is fresh generated page from template
'''

import calendar
import os
import pathlib
import re
import sys

MONTHS_SHORT = (
    'Jan','Feb','Mar','Apr','May','Jun',
    'Jul','Aug','Sep','Oct','Nov','Dec'
)
MONTHS_FULL = (
    'January','February','March','April','May','June',
    'July','August','September','October','November','December'
)
RE_TITLE = re.compile(r'\<title\>Math Calendar (\d+) ([A-Z][a-z]+)\<\/title\>')

def find_year_and_month(file_lines:list[str]) -> tuple[int,int,str,str,int]:
    '''
    identify year and month from page title
    returns: (year,month_number,month_full,month_short,day_count)
    example: (2026,10,'October','Oct',31)
    '''
    title_tmp = [line.strip() for line in file_lines if RE_TITLE.match(line.strip())]
    assert len(title_tmp) == 1, f'found {len(title_tmp)} occurrences of page title'
    title_tmp = title_tmp[0]
    title_match = RE_TITLE.match(title_tmp)
    assert title_match, f'title format invalid' # should never happen?
    year_tmp,month_full = title_match.groups()
    year = int(year_tmp)
    assert month_full in MONTHS_FULL, f'invalid month: {month_full}'
    month_short = [m for m in MONTHS_SHORT if month_full.startswith(m)][0]
    month_index = [i for i,m in enumerate(MONTHS_SHORT) if m == month_short][0]
    day_count = calendar.monthrange(year,month_index+1)[1]
    return (year,month_index+1,month_full,month_short,day_count)

def find_marker_indexes(file_lines:list[str],markers:list[str]) -> list[int]:
    '''
    finds the index for each marker provided
    checks that they only occur once in the file and are in increasing order
    '''
    # markers should be unique in the file
    result = []
    for marker in markers:
        indexes = [i for i,line in enumerate(file_lines) if marker in line]
        assert len(indexes) == 1, f'found {len(indexes)} occurrences of marker: {repr(marker)}'
        result.append(indexes[0])
    assert all(a < b for a,b in zip(result,result[1:]))
    return result

def all_markers(year:int,month_number:int) -> list[tuple[str,tuple[str,str]]]:
    '''
    all marker pairs that should be in the files with a type label
    example list item: ('custom latex',('MARK_BEG_...','MARK_END_...'))
    this has to change if pairs are added/removed/renamed
    further changes needed if old and new no longer match
    '''
    day_count = calendar.monthrange(year,month_number)[1]
    month_short = MONTHS_SHORT[month_number-1].upper()
    result = [
        ('custom latex', (
            f'MARK_BEG_{year}_{month_short}_CUSTOM_LATEX',
            f'MARK_END_{year}_{month_short}_CUSTOM_LATEX'
        )),
        ('custom css', (
            f'MARK_BEG_{year}_{month_short}_CUSTOM_CSS',
            f'MARK_END_{year}_{month_short}_CUSTOM_CSS'
        )),
        ('comments', (
            f'MARK_BEG_{year}_{month_short}_COMMENTS',
            f'MARK_END_{year}_{month_short}_COMMENTS'
        ))
    ]
    for day in range(1,day_count+1):
        result.append((f'{month_short.lower()}{day:02d} problem', (
            f'MARK_BEG_{year}_{month_short}_{day:02d}_PROBLEM',
            f'MARK_END_{year}_{month_short}_{day:02d}_PROBLEM'
        )))
        result.append((f'{month_short.lower()}{day:02d} solution', (
            f'MARK_BEG_{year}_{month_short}_{day:02d}_SOLUTION',
            f'MARK_END_{year}_{month_short}_{day:02d}_SOLUTION'
        )))
    return result

def check_marker_indexes(file_lines:list[str],markers:list[tuple[str,str]]):
    '''
    find indexes for all markers, verify this are in strictly increasing order
    '''
    indexes = []
    for a,b in markers:
        indexes += find_marker_indexes(file_lines,[a,b])
    assert all(a < b for a,b in zip(indexes,indexes[1:]))

def find_content_lines(file_lines:list[str],marker_begin:str,marker_end:str) -> list[str]:
    '''
    select content lines between marker lines
    '''
    index_begin,index_end = find_marker_indexes(file_lines,[marker_begin,marker_end])
    assert index_begin < index_end
    return file_lines[index_begin+1:index_end]

def insert_content_lines(content_lines:list[str],file_lines:list[str],
                         marker_begin:str,marker_end:str):
    index_begin,index_end = find_marker_indexes(file_lines,[marker_begin,marker_end])
    file_lines[index_begin+1:index_end] = content_lines

def move_content(old_file_lines:list[str],new_file_lines:list[str],
                 marker_begin:str,marker_end:str,content_type:str):
    content_lines = find_content_lines(old_file_lines,marker_begin,marker_end)
    print(f'moving {len(content_lines)} lines for {content_type}')
    insert_content_lines(content_lines,new_file_lines,marker_begin,marker_end)

def main():
    # parse args
    old_file = sys.argv[1]
    new_file = sys.argv[2]
    print('input old',old_file)
    print('input new',new_file)
    assert pathlib.Path(old_file).resolve() != pathlib.Path(new_file).resolve()

    # read contents
    old_lines = open(old_file,'r',encoding='utf-8').read().splitlines()
    new_lines = open(new_file,'r',encoding='utf-8').read().splitlines()
    print(f'read {len(old_lines)} lines in {old_file}')
    print(f'read {len(new_lines)} lines in {new_file}')

    # find year and month, ensure both files match
    year,month_number,month_full,month_short,day_count = find_year_and_month(old_lines)
    year__,month_number__,month_full__,month_short__,day_count__ = find_year_and_month(new_lines)
    assert year == year__ and month_number == month_number__ and month_full == month_full__ \
        and month_short == month_short__ and day_count == day_count__, \
        f'year/month do not match: ({year},{month_number}) != ({year__},{month_number__})'

    # ensure markers appear increasing
    markers_info = all_markers(year,month_number) # list[(type,(beg,end))]
    markers = list(a for _,a in markers_info)
    check_marker_indexes(old_lines,markers)
    check_marker_indexes(new_lines,markers)

    # perform content move
    for content_type,(marker_begin,marker_end) in markers_info:
        move_content(old_lines,new_lines,marker_begin,marker_end,content_type)

    # do a check that content is there
    for _,(marker_begin,marker_end) in markers_info:
        assert find_content_lines(old_lines,marker_begin,marker_end) \
            == find_content_lines(new_lines,marker_begin,marker_end)

    # write to a temporary and then replace with new content
    with open(f'{new_file}.tmp','w',encoding='utf-8') as file:
        for line in new_lines:
            file.write(f'{line}\n')
    os.replace(f'{new_file}.tmp',new_file)

if __name__ == '__main__':
    main()
