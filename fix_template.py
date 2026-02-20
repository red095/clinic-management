import re

fpath = 'templates/dashboards/admin_create_doctor.html'
with open(fpath, encoding='utf-8') as f:
    content = f.read()

# Fix all instances of ==" to == " in Django template if tags
content = re.sub(r'(\w)==\"', r'\1 == "', content)

with open(fpath, 'w', encoding='utf-8') as f:
    f.write(content)

# Verify
remaining = [i+1 for i, line in enumerate(content.splitlines()) if '==\"' in line]
print('Lines with ==": ', remaining, '(should be empty)')
print('Done.')
