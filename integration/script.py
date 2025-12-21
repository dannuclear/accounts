# Для создания и начала согласования бухгалтерского локумента используется функция "create_script" принимающая
# два обязательных именованных аргумента: "document: dict" (пример фотмата объекта "document_data_example")
# и "files: list" (пример формата объекта "file_list_example")
#
# Данная функция возвращает словарь в формате представленном ниже
#
# success_create_example_dict = {
#     'sucess': True
# }
# error_create_example_dict = {
#     'sucess': False,
#     'error': {error_text}
# }
#
# Для удаления бухгалтерского документа используется функция "remove_script" принимающая один обязательный
# именованный атрибут "document: dict" (пример фотмата объекта "remove_document_example")
#
# Данная функция возвращает словарь в формате представленном ниже
#
# success_remove_doc = {
#     'success': True,
# }
# error_remove_doc = {
#     'success': False,
#     'error': {error_text}
# }
#
# document_data_example = {
#         'login': 'z00000', # str, Логин пользователя исполнителя документа
#         'div_no': '079', # str, Номер подразделения - откуда документ
#         'document_number': '000', # str, Номер бухгалтерского документа
#         'document_date': '17.11.0000', # str, Дата бухгалтерского документа
#         'template': 'ADVANCE_REPORT', # str, Название шаблона
#         'document_id_old': '', # str, Предыдущий документ, используется для копирования переписки/замечаний
#         'document_characteristics': 'О запросе денег' # str, Информация о документе
# }
#
# file_list_example = [
#     {
#         'file_path': os.path.join('test_data', 'Схема Лесного.pdf'), # str, Путь к файлу
#         'sign': 'Ф', # str, Признак, Ф - pdf содержание бухгалтерского документа, О - основные приложения, Д - дополнительные файлы для согласования
#         'file_name': 'Схема Лесного.pdf', # str, Имя основного файла
#         'serial_number': 1, # int, Порядковый номер, в рамках признака, начинается с 1
#         'app_description': 'some description', # str, Описание приложения
#     },
#     {
#         'file_path': os.path.join('test_data', 'Схема Лесного.pdf'),
#         'sign': 'О',
#         'file_name': 'Схема Лесного.pdf',
#         'serial_number': 1,
#         'app_description': 'some description',
#     },
# ]
#
# remove_document_example = {
#     'document_id': 000000000, # Union(str, int), ID удаляемого бухгалтерского документа
#     'login': 'z00000' # str, Логин
# }


import os
import subprocess

import pyodbc
import uuid
import hashlib
from dotenv import load_dotenv
from operator import itemgetter

# Указать расположение .env файла
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')

if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
else:
    raise Exception('Could not find .env file.')

DB_SERVER_NAME = os.getenv('DB_SERVER_NAME')
DB_SERVER_PORT = os.getenv('DB_SERVER_PORT')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
FILESTORE_DB_NAME = os.getenv('FILESTORE_DB_NAME')
ESESD_DB_NAME = os.getenv('ESESD_DB_NAME')

MS_connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={DB_SERVER_NAME},{DB_SERVER_PORT};DATABASE={FILESTORE_DB_NAME};UID={DB_USER};PWD={DB_PASSWORD}'
string = f'DRIVER=ODBC Driver 17 for SQL Server; SERVER={DB_SERVER_NAME}; DATABASE=ЕСЭСД; UID={DB_USER}; PWD={DB_PASSWORD};'

file_procedure_name = '_файл_ins'
doc_procedure_name = '_бд_ins'
doc_remove_procedure_name = '_бд_del'


def __get_connection_string(database):
    return (f'DRIVER={{ODBC Driver 17 for SQL Server}};'
            f'SERVER={DB_SERVER_NAME};'
            f'DATABASE={database};'
            f'UID={DB_USER};'
            f'PWD={DB_PASSWORD};'
            )


def __compress_file(input_file_path, password, archieve_name):
    if os.path.exists(archieve_name):
        os.remove(archieve_name)
    cmd = [
        '7z', 'a', archieve_name, f'-si{archieve_name}', '-p' + password, '-mhe=on'
    ]

    with open(input_file_path, 'rb') as f:
        file_data = f.read()

        process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        stdout_data, stderr_data = process.communicate(input=file_data)

        if process.returncode != 0:
            raise Exception(stderr_data.decode('utf-8'))

    if os.path.exists(archieve_name):
        try:
            with open(archieve_name, 'rb') as f:
                return f.read()
        finally:
            os.remove(archieve_name)


def create_script(files: list, document: dict):
    result = subprocess.run(['7z', '--help'], capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception('7z не найден.')
    sorted_files = sorted(files, key=itemgetter('sign', 'serial_number'))
    files_sql = f'''
        DECLARE @return_value int,
		@файл_ID varchar(20)
        {{CALL {file_procedure_name} 
        (@структура_архива=?, @номер_блока=?, @данные=?, @код_доступа=?, @пароль=?, @файл_ID=@файл_ID OUTPUT)}}
        SELECT @файл_ID as N'@файл_ID'
        SELECT  'Return Value' = @return_value
    '''
    files_info = []
    for file in sorted_files:
        with open(file['file_path'], 'rb') as f:
            md_5_hash = hashlib.md5(f.read()).hexdigest()
        access_code = uuid.uuid4().hex
        binary_file = __compress_file(file['file_path'], access_code, file['file_name'])
        file_size = os.path.getsize(file['file_path'])
        # md_5_hash = hashlib.md5(binary_file).hexdigest()
        with pyodbc.connect(__get_connection_string(FILESTORE_DB_NAME)) as conn:
            params = (
                f'{file["file_name"]}>{md_5_hash}',
                0,
                binary_file,
                access_code,
                access_code,
            )
            cursor = conn.cursor()
            cursor.execute(files_sql, params)
            file_id = cursor.fetchone()[0]
            file_info = {
                'file_id': file_id,
                'file_name': file['file_name'],
                'file_md5': md_5_hash,
                'file_size': str(file_size),
                'sign': file['sign'],
                'access_code': access_code,
                'app_description': file['app_description'],
            }
            files_info.append(file_info)

    with pyodbc.connect(__get_connection_string(ESESD_DB_NAME)) as conn:
        doc_sql = f'''
                DECLARE @документ_ID varchar(20)
                {{CALL {doc_procedure_name}
                (@подразделение=?, @характеристики=?, @файлы=?, @логин=?, @документ_ID=@документ_ID OUTPUT)}}
                SELECT @документ_ID as N'@документ_ID'
                '''
        specifications = f'''
            <?xml version="1.0" encoding="WINDOWS-1251" standalone="yes"?>
            <Param>
                <ParamData характеристика_код = "номер_бухгалтерского_документа" значение =
                 "{document.get('document_number')}"/>
                <ParamData характеристика_код = "дата_бухгалтерского_документа" значение =
                 "{document.get('document_date')}"/>
                <ParamData характеристика_код = "шаблон_ID" значение =
                 "{os.environ.get(document.get('template'))}"/>
                <ParamData характеристика_код = "документ_ID_old" значение =
                 "{document.get('document_id_old')}"/>
                <ParamData характеристика_код = "характеристика_документа" значение =
                 "{document.get('document_characteristics')}" />
            </Param>
        '''
        param_data_string = ''
        for file in files_info:
            param_data = (f'<ParamData файл_ID = "{file["file_id"]}"'
                          f' размер = "{file["file_size"]}"'
                          f' признак = "{file["sign"]}"'
                          f' код_доступа = "{file["access_code"]}"'
                          f' имя_файла = "{file["file_name"]}"'
                          f' хэш_MD5 = "{file["file_md5"]}"'
                          f' описание_приложения = "{file["app_description"]}" />'
                          )
            param_data_string += param_data
        files_xml = f'<?xml version="1.0" encoding="WINDOWS-1251" standalone="yes"?><Param>{param_data_string}</Param>'
        params = (
            document['div_no'],
            specifications,
            files_xml,
            document['login']
        )
        try:
            cursor = conn.cursor()
            cursor.execute(doc_sql, params)
            if not cursor.description:
                cursor.nextset()
            document_id = cursor.fetchone()[0]
            return {
                'success': True,
                'document_id': document_id,
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
            }


def remove_script(document: dict) -> dict:
    try:
        with pyodbc.connect(__get_connection_string(ESESD_DB_NAME)) as conn:
            remove_sql = f'''
                {{CALL {doc_remove_procedure_name} (@документ_ID=?, @логин=?)}}
            '''
            params = (
                document['document_id'] if isinstance(document['document_id'], str) else (str(document['document_id'])),
                document['login']
            )
            cursor = conn.cursor()
            cursor.execute(remove_sql, params)
        return {
            'success': True,
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

