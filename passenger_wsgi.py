# -*- coding: utf-8 -*-
import os, sys
#project directory
sys.path.insert(0, '/home/g/g982257e/inmovery.ru/IoTServer')
sys.path.insert(1, '/home/g/g982257e/inmovery.ru/venv/lib/python3.6/site-packages')

from IoTServer import app as application # когда Flask стартует, он ищет application. Если не указать 'as application', сайт не заработает
from werkzeug.debug import DebuggedApplication # Опционально: подключение модуля отладки
application.wsgi_app = DebuggedApplication(application.wsgi_app, True) # Опционально: включение модуля отадки
application.debug = False  # Опционально: True/False устанавливается по необходимости в отладке
