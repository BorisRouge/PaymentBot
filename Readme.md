Пример платежного телеграм-бота
===============================

Работающий образец можно пощупать здесь: https://t.me/KkerkerBot


### Порядок запуска

* Собран на Ubuntu 22.04 LTS
* Подразумеваются установленные Python и Postgresql

1. Внести учетные данные (телеграм, киви, постгрес) в тестовый файл окружения sample.env
2. 
```shell 
pip install -r requirements.txt
```
3. 
```shell 
python main.py
```

### Планы
Изменить структуру проекта. Разгрузить main.py - вынести обработчики сообщений в отдельные модули. 