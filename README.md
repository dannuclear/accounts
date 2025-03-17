Работаем с Python 3.6

Требования по версиям библиотек requirements.txt
pip install -r requirements.txt

под nix системами вместо psycopg2 -> psycopg2-binary

для прода надо удалить
    request.META['KRB5CCNAME'] = 'admin'
в файле wsgi.py


Для решения проблем с загрузкой файлов на сервере AstraLinux
изменить /etc/apache2/envvars
раскоментировать строчку . /etc/default/locale