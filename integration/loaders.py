import csv
from datetime import datetime
from decimal import Decimal
from .helper import FileType

from .models import Employee, Estimate, Prepayment

estimateFields = ['xv26eicYear', 'xv26eiId', 'xv26eihDateBegin', 'xv26eihDateEnd', 'xv26eihName', 'xv26eirSumPlan']
employeeFields = ['empOrgNo', 'divNo', 'persId', 'pfnSurname', 'pfnName', 'pfnPatronymic', 'pqlfName', 'profName', 'empChangesDate', 'empDismissDate']
prepaymentFields = ['pdId', 'pdSource', 'empOrgNo', 'xv26eiId', 'orderId', 'orderIdUpd', 'orderNo', 'orderDate', 'bic', 'sum', 'acplAccount', 'acplSubaccount']

def load (path, type):
    with open(path, encoding="utf-8" ,mode ='r') as file:
        dialect = csv.Sniffer().sniff(file.read(1024))
        file.seek(0)
        fields = estimateFields if type == FileType.ESTIMATE else employeeFields if type == FileType.EMPLOYEE else prepaymentFields if type == FileType.PREPAYMENT else None
        if fields == None:
            exit
        reader = csv.DictReader(file, fieldnames=fields, dialect=dialect)
        for row in reader:
            replacedRow = replace_empty_str_with_none(row)
            obj = Estimate(**replacedRow) if type == FileType.ESTIMATE else Employee(**replacedRow) if type == FileType.EMPLOYEE else Prepayment(**replacedRow) if type == FileType.PREPAYMENT else None
            obj.save()

def replace_empty_str_with_none(some_dict):
    return { k: (None if v == '' else v) for k, v in some_dict.items() }
