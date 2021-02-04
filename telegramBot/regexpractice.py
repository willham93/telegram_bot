import re

date = "2021-01-06"
match = re.search(r'\d{4}-\d{2}-\d{2}', date)

print(match)
