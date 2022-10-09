import re
list = {
    'result_decimal_points': 12
}

items = list.items()
for k,v in items:
    text = '<label for = "answer" > Round to {{ result_decimal_points }} decimal points < /label > <br >'
    print(k)
    pattern = r'\{\{\s' + k + r'\s\}\}'
    print(pattern)
    print(text)
    print(re.findall(pattern, text))


