t= {'test': [''],
'test1': None,
'test2': 0}
for k,v in t.items():
    if v:
        print(f'{k} +')
    else:
        print(f'{k} -')
