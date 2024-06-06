import csv
from .models import Employee
from datetime import datetime

def load (path): 
    with open(path, encoding="utf-8" ,mode ='r') as file:
        dialect = csv.Sniffer().sniff(file.read(1024))
        file.seek(0)
        reader = csv.DictReader(file, fieldnames=['empOrgNo', 'divNo', 'persId', 
                                                    'pfnSurname', 'pfnName', 'pfnPatronymic', 
                                                    'pqlfName', 'profName', 'empChangesDate', 
                                                    'empDismissDate'], dialect=dialect)
        for row in reader:
            employee = Employee(**replace_empty_str_with_none(row))
            employee.save()

            
def replace_empty_str_with_none(some_dict):
    return { k: (None if v == '' else v) for k, v in some_dict.items() }




