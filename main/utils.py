import re


def get_emp_num(user):
    m = re.search(r'\d+', user.username or '')
    return m.group() if m else None
