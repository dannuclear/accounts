import csv
from .models import Estimate
from datetime import datetime
from decimal import Decimal

def load (path): 
    with open(path, encoding="utf-8" ,mode ='r') as file:
        dialect = csv.Sniffer().sniff(file.read(1024))
        file.seek(0)
        reader = csv.DictReader(file, fieldnames=['xv26eicYear', 'xv26eiId', 'xv26eihDateBegin', 'xv26eihDateEnd', 'xv26eihName', 'xv26eirSumPlan'], dialect=dialect)
        for row in reader:
            estimate = Estimate(**replace_empty_str_with_none(row))
            estimate.save()

            
def replace_empty_str_with_none(some_dict):
    return { k: (None if v == '' else v) for k, v in some_dict.items() }




