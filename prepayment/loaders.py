import csv
from .models import Prepayment
from datetime import datetime
from decimal import Decimal

def load (path): 
    with open(path, encoding="utf-8" ,mode ='r') as file:
        dialect = csv.Sniffer().sniff(file.read(1024))
        file.seek(0)
        reader = csv.DictReader(file, fieldnames=['pdId', 'pdSource', 'empOrgNo', 'xv26eiId', 'orderId', 'orderIdUpd', 'orderNo', 'orderDate', 'bic', 'sum', 'acplAccount', 'acplSubaccount'], dialect=dialect)
        for row in reader:
            prepayment = Prepayment(**replace_empty_str_with_none(row))
            prepayment.save()

            
def replace_empty_str_with_none(some_dict):
    return { k: (None if v == '' else v) for k, v in some_dict.items() }




