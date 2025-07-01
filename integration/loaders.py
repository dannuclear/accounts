import csv
from datetime import datetime
from .helper import FileType
from .models import Employee, Estimate, Prepayment, Protocol, WC07POrder

estimateFields = ['xv26eicYear', 'xv26eiId', 'xv26eihDateBegin',
                  'xv26eihDateEnd', 'xv26eihName', 'xv26eirSumPlan']
employeeFields = ['empOrgNo', 'divNo', 'persId', 'pfnSurname', 'pfnName',
                  'pfnPatronymic', 'pqlfName', 'profName', 'empChangesDate', 'empDismissDate', 'accountNumber', 'snils']
prepaymentFields = ['pdId', 'pdSource', 'empOrgNo', 'xv26eiId', 'orderId',
                    'orderIdUpd', 'orderNo', 'orderDate', 'bic', 'sum', 'acplAccount', 'acplSubaccount']
wc07pOrderFields = ['orderName', 'orderId', 'orderNum', 'orderDate', 'empOrgNo', 'depName', 'fio', 'profName',
                    'distName', 'missionBegin', 'missionEnd', 'missionPurpose', 'estimateId', 'payDoc', 'orderIdUpd']

def get_fields(file_type):
    if file_type == FileType.ESTIMATE:
        return estimateFields
    elif file_type == FileType.EMPLOYEE:
        return employeeFields
    elif file_type == FileType.PREPAYMENT:
        return prepaymentFields
    elif file_type == FileType.WC07P_ORDER:
        return wc07pOrderFields
    return None

def create_object(file_type, data):
    if file_type == FileType.ESTIMATE:
        return Estimate(**data)
    elif file_type == FileType.EMPLOYEE:
        return Employee(**data)
    elif file_type == FileType.PREPAYMENT:
        return Prepayment(**data)
    elif file_type == FileType.WC07P_ORDER:
        return WC07POrder(**data)
    return None

def load(path, _type):
    def clean_snils(data):
        if 'snils' in data and data['snils']:
            data['snils'] = data['snils'].replace('-', '').replace(' ', '')

    with open(path, encoding="utf-8", mode='r') as file:
        dialect = csv.Sniffer().sniff(file.read(4048), delimiters='\t')
        dialect.delimiter = '\t'
        file.seek(0)
        fields = get_fields(_type)
        if fields is None:
            return
        reader = csv.DictReader(file, fieldnames=fields, dialect=dialect)
        for row in reader:
            replaced_row = replace_empty_str_with_none(row)
            if _type == FileType.EMPLOYEE:
                clean_snils(replaced_row)
            obj = create_object(_type, replaced_row)
            obj.save()
        protocol = Protocol()
        protocol.operDate = datetime.now()
        protocol.comment = 'файл %s успешно загружен' % (file.name)
        protocol.save()


def replace_empty_str_with_none(some_dict):
    return {k: (None if v == '' else v) for k, v in some_dict.items()}
