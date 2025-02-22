--- Python
# 1. Проверка версии и запуск Python
python --version                                # Проверить версию Python
python script.py                                # Запустить скрипт Python
python -m module_name                           # Запустить модуль (например, venv, http.server)
python -m http.server 8000                      # Запустить встроенный HTTP-сервер на порту 8000
exit() or Ctrl+D                                # Выйти из интерактивного режима Python
python -i script.py                             # Запустить скрипт и войти в интерактивный режим после выполнения

# 2. Виртуальное окружение (venv)
python -m venv venv                             # Создать виртуальное окружение
source venv/bin/activate                        # Активировать виртуальное окружение (Linux/macOS)
deactivate                                      # Выйти из виртуального окружения

# 3. Работа с пакетами (pip)
pip install package                             # Установить пакет
pip install package==1.2.3                      # Установить конкретную версию пакета
pip install -U package                          # Обновить пакет
pip uninstall package                           # Удалить пакет
pip list                                        # Показать установленные пакеты
pip freeze                                      # Вывести список установленных пакетов с версиями
pip freeze > requirements.txt                   # Сохранить список зависимостей в файл
pip install -r requirements.txt                 # Установить зависимости из файла
pip show package                                # Показать информацию о пакете
pip check                                       # Проверить зависимости на наличие конфликтов
pip cache purge                                 # Очистить кеш pip

# 4. Запуск тестов (pytest, unittest)
pytest                                          # Запустить тесты с Pytest
pytest -v                                       # Подробный вывод тестов
pytest tests/                                   # Запустить тесты в папке tests
pytest -k "test_name"                           # Запустить конкретный тест
python -m unittest discover                     # Найти и запустить тесты Unittest

# 5. Отладка и профилирование
python -m pdb script.py                         # Запустить отладчик
black script.py                                 # Автоформатирование кода
flake8 script.py                                # Анализ кода (поиск ошибок)
mypy script.py                                  # Проверка типов с помощью MyPy
cProfile.run('script_function()')               # Запустить профилирование кода
time python script.py                           # Измерить время выполнения скрипта

# 6. Работа с процессами
ps aux | grep python                            # Найти процесс Python (Linux/macOS)
kill -9 PID                                     # Завершить процесс (Linux/macOS)

# 7. Генерация документации
pydoc module_name                               # Просмотр документации модуля
pydoc -w module_name                            # Генерация HTML-документации модуля
sphinx-quickstart                               # Инициализация документации Sphinx

# 8. Создание и установка пакетов
python setup.py sdist                           # Создать архив с исходниками
python setup.py bdist_wheel                     # Собрать wheel-пакет
pip install package.whl                         # Установить локальный wheel-пакет
twine upload dist/*                             # Опубликовать пакет в PyPi

# 9. Работа с виртуальными окружениями Poetry
poetry init                                     # Создать новый проект
poetry add package                              # Установить пакет
poetry remove package                           # Удалить пакет
poetry install                                  # Установить зависимости
poetry run python script.py                     # Запустить скрипт в окружении Poetry
poetry shell                                    # Активировать виртуальное окружение Poetry



--- npm
# 1. Управление проектом
npm init                                        # Инициализировать новый проект (создает package.json)
npm init -y                                     # Инициализировать проект с дефолтными настройками
npm init --scope=<scope_name>                   # Инициализировать проект с указанием scope
npm install <package>                           # Установить пакет и добавить его в dependencies
npm install <package>@<version>                 # Установить конкретную версию пакета
npm install <package> --save                    # Установить пакет и добавить его в dependencies (старый способ)
npm install <package> --save-dev                # Установить пакет и добавить его в devDependencies
npm install                                     # Установить все зависимости из package.json

# 2. Удаление пакетов
npm uninstall <package>                         # Удалить пакет
npm uninstall <package> --save                  # Удалить пакет из dependencies
npm uninstall <package> --save-dev              # Удалить пакет из devDependencies

# 3. Обновление пакетов
npm update <package>                            # Обновить указанный пакет
npm update                                      # Обновить все пакеты до последних допустимых версий
npm outdated                                    # Показать устаревшие пакеты
npm install -g npm                              # Обновить npm до последней версии

# 4. Управление зависимостями
npm list                                        # Показать все установленные зависимости в проекте
npm list --depth=0                              # Показать только верхний уровень зависимостей
npm audit                                       # Проверка на уязвимости в зависимостях
npm audit fix                                   # Исправить найденные уязвимости
npm audit fix --force                           # Принудительно исправить уязвимости
npm dedupe                                      # Удалить дубликаты зависимостей

# 5. Работа с глобальными пакетами
npm install -g <package>                        # Установить пакет глобально
npm uninstall -g <package>                      # Удалить глобальный пакет
npm list -g                                     # Показать глобальные пакеты
npm update -g                                   # Обновить глобальные пакеты
npm ls -g <package>                             # Показать информацию о глобальном пакете

# 6. Скрипты npm
npm run <script>                                # Запустить скрипт из package.json
npm run build                                   # Запустить скрипт build (если есть в package.json)
npm run start                                   # Запустить скрипт start (если есть в package.json)
npm run test                                    # Запустить тесты (если есть в package.json)
npm run <script> -- <args>                      # Передать аргументы скрипту
npm run lint                                    # Запустить линтинг (если есть в package.json)

# 7. Установка зависимостей из package.json
npm install --production                        # Установить только зависимости для продакшн
npm install --dev                               # Установить только devDependencies

# 8. Работа с кешем
npm cache clean --force                         # Очистить кеш npm
npm cache verify                                # Проверить кеш на целостность
npm cache add <package>                         # Добавить пакет в кеш

# 9. Теги и версии
npm version <new_version>                       # Обновить версию проекта в package.json
npm version major                               # Обновить мажорную версию
npm version minor                               # Обновить минорную версию
npm version patch                               # Обновить патч-версию
npm version <new_version> -m "message"          # Обновить версию с комментарием

# 10. Логирование
npm info <package>                              # Получить информацию о пакете
npm help                                        # Получить справку по команде
npm doctor                                      # Проверить установку npm и среду
npm config get <key>                            # Получить значение настройки npm
npm config set <key> <value>                    # Установить настройку npm
npm config delete <key>                         # Удалить настройку npm

# 11. Ссылки и пакеты с GitHub
npm install <github_user>/<repo>                # Установить пакет из GitHub репозитория
npm install <github_user>/<repo>#<branch>       # Установить пакет из определенной ветки

# 13. Работа с логами
npm log                                         # Показать лог ошибок установки пакетов
npm install <package> --verbose                 # Подробный вывод процесса установки пакетов



--- Docker
# 1. Установка и проверка
docker --version                                # Проверить версию Docker
docker info                                     # Вывести общую информацию о Docker
docker ps                                       # Показать запущенные контейнеры
docker ps -a                                    # Показать все контейнеры (включая остановленные)

# 2. Работа с образами (Images)
docker pull <image>                             # Скачать образ из Docker Hub
docker images                                   # Список загруженных образов
docker rmi <image>                              # Удалить образ
docker build -t <image_name> .                  # Создать образ из Dockerfile
docker tag <image> <new_image>                  # Переименовать образ
docker save -o <file.tar> <image>               # Экспортировать образ в файл
docker load -i <file.tar>                       # Импортировать образ из файла

# 3. Работа с контейнерами
docker run <image>                              # Запустить контейнер из образа
docker run -d <image>                           # Запустить контейнер в фоновом режиме (detached)
docker run --name <name> <image>                # Запустить контейнер с именем
docker run -p 8080:80 <image>                   # Проброс портов (локальный:контейнерный)
docker start <container>                        # Запустить ранее созданный контейнер
docker stop <container>                         # Остановить контейнер
docker restart <container>                      # Перезапустить контейнер
docker rm <container>                           # Удалить контейнер
docker logs <container>                         # Просмотреть логи контейнера
docker exec -it <container> bash                # Выполнить команду в работающем контейнере (Bash)
docker attach <container>                       # Подключиться к запущенному контейнеру
docker cp <container>:/path local_path          # Скопировать файл из контейнера

# 4. Работа с томами (Volumes)
docker volume create <volume>                   # Создать том
docker volume ls                                # Список томов
docker volume inspect <volume>                  # Посмотреть информацию о томе
docker volume rm <volume>                       # Удалить том

# 5. Сети (Networking)
docker network ls                               # Список сетей
docker network create <network>                 # Создать сеть
docker network connect <network> <container>    # Подключить контейнер к сети
docker network disconnect <network> <container> # Отключить контейнер от сети
docker network inspect <network>                # Посмотреть информацию о сети
docker network rm <network>                     # Удалить сеть

# 6. Docker Compose
docker-compose up -d                            # Запустить все контейнеры из docker-compose.yml
docker-compose down                             # Остановить и удалить контейнеры, созданные через compose
docker-compose ps                               # Показать контейнеры, управляемые compose
docker-compose logs                             # Логи всех контейнеров в compose
docker-compose restart                          # Перезапустить контейнеры в compose

# 7. Очистка Docker
docker system prune -a                          # Очистить неиспользуемые контейнеры, образы и кеш
docker container prune                          # Удалить все остановленные контейнеры
docker image prune                              # Удалить неиспользуемые образы
docker volume prune                             # Удалить неиспользуемые тома
docker network prune                            # Удалить неиспользуемые сети



--- Git
# 1. Основные команды для работы с репозиторием
git init                                        # Инициализировать новый git-репозиторий
git clone <repository_url>                      # Клонировать удалённый репозиторий
git status                                      # Показать статус изменений в репозитории
git add <file>                                  # Добавить файл в индекс (staging area)
git add .                                       # Добавить все изменённые файлы в индекс
git commit -m "message"                         # Сделать коммит с сообщением
git commit --amend                              # Изменить последний коммит
git commit -a                                   # Закоммитить все отслеживаемые файлы
git diff                                        # Показать изменения в рабочем каталоге
git diff --staged                               # Показать изменения, подготовленные для коммита

# 2. Работа с ветками
git branch                                      # Показать все ветки
git branch <branch_name>                        # Создать новую ветку
git checkout <branch_name>                      # Переключиться на другую ветку
git checkout -b <branch_name>                   # Создать и переключиться на новую ветку
git merge <branch_name>                         # Слить ветку с текущей
git branch -d <branch_name>                     # Удалить ветку
git branch -D <branch_name>                     # Принудительно удалить ветку

# 3. Работа с удалёнными репозиториями
git remote add <name> <repository_url>          # Добавить удалённый репозиторий
git remote -v                                   # Показать удалённые репозитории
git fetch                                       # Получить последние изменения из удалённого репозитория
git pull                                        # Вытянуть изменения и слить их с текущей веткой
git push                                        # Отправить изменения в удалённый репозиторий
git push <remote> <branch>                      # Отправить изменения в удалённый репозиторий на конкретную ветку
git push origin --delete <branch_name>          # Удалить ветку в удалённом репозитории

# 4. История изменений
git log                                         # Показать историю коммитов
git log --oneline                               # Показать историю коммитов в компактном виде
git log --graph --oneline --all                 # История с графом, показывающая все ветки
git show <commit_id>                            # Показать подробности конкретного коммита
git blame <file>                                # Показать, кто и когда изменил каждую строку файла

# 5. Работа с тегами
git tag                                         # Показать все теги
git tag <tag_name>                              # Создать тег на текущем коммите
git tag -a <tag_name> -m "message"              # Создать аннотированный тег
git push origin <tag_name>                      # Отправить тег в удалённый репозиторий
git push --tags                                 # Отправить все теги в удалённый репозиторий
git tag -d <tag_name>                           # Удалить тег локально
git push origin --delete <tag_name>             # Удалить тег в удалённом репозитории

# 6. Работа с конфигурацией
git config --global user.name "Name"            # Установить имя пользователя
git config --global user.email "email"          # Установить email пользователя
git config --list                               # Показать конфигурацию
git config --global core.editor vim             # Установить редактор для git

# 7. Работа с подмодулями
git submodule add <repository_url> <path>       # Добавить подмодуль
git submodule init                              # Инициализировать подмодуль
git submodule update                            # Обновить подмодули

# 8. Откат изменений
git checkout -- <file>                          # Отменить изменения в файле
git reset <file>                                # Убрать файл из индекса (staging area)
git reset --hard                                # Откатиться к последнему коммиту (внимание: удаляются все изменения)
git reset --soft <commit_id>                    # Вернуться к коммиту, но сохранить изменения в рабочем каталоге

# 9. Работа с конфликтами
git merge --abort                               # Отменить слияние при возникновении конфликта
git mergetool                                   # Запустить инструмент для разрешения конфликтов

# 10. Работа с ремоутами
git remote add <name> <repository_url>          # Добавить удалённый репозиторий
git remote rm <name>                            # Удалить удалённый репозиторий
git remote rename <old_name> <new_name>         # Переименовать удалённый репозиторий

# 11. Сохранение изменений без коммита
git stash                                       # Сохранить изменения в "стэш"
git stash list                                  # Показать список всех стэшей
git stash apply                                 # Применить последний стэш
git stash pop                                   # Применить последний стэш и удалить его
git stash drop                                  # Удалить последний стэш
git stash clear                                 # Удалить все стэши

# 12. Работа с различными конфигурациями
git config --global core.editor nano            # Установить nano как редактор по умолчанию
git config --global alias.co checkout           # Создать псевдоним для команды (например, co = checkout)
git config --global alias.st status             # Создать псевдоним для команды (например, st = status)

# 13. Восстановление после ошибок
git reflog                                      # Показать журнал действий (для восстановления состояния репозитория)
git fsck                                        # Проверить репозиторий на ошибки



--- Redis
# 1. Подключение и базовые операции
redis-server                                    # Запуск Redis-сервера
redis-cli                                       # Запуск клиента Redis (для взаимодействия с сервером)
redis-cli -h <host> -p <port>                   # Подключение к удалённому серверу Redis
redis-cli CONFIG GET dir                        # Показывает директорию редис сохранений
redis-cli shutdown                              # Отключает работу редис
redis-server ./src/confredis/redis.conf
ping                                            # Проверить подключение к Redis (ответ: PONG)

# 2. Операции с ключами
SET <key> <value>                               # Установить значение для ключа
GET <key>                                       # Получить значение ключа
DEL <key>                                       # Удалить ключ
EXPIRE <key> <seconds>                          # Установить время жизни ключа в секундах
TTL <key>                                       # Получить оставшееся время жизни ключа
KEYS <pattern>                                  # Найти все ключи, подходящие под шаблон (не рекомендуется на больших базах)
FLUSHALL                                        # Удалить все ключи из всех баз данных
FLUSHDB                                         # Удалить все ключи из текущей базы данных
TYPE <key>                                      # Получить тип значения по ключу

# 3. Операции со строками
APPEND <key> <value>                            # Добавить строку в конец значения
INCR <key>                                      # Увеличить значение ключа на 1 (для числовых значений)
DECR <key>                                      # Уменьшить значение ключа на 1 (для числовых значений)
MSET <key1> <value1> <key2> <value2>            # Установить несколько ключей
MGET <key1> <key2>                              # Получить несколько значений по ключам

# 4. Операции с хешами
HSET <hash> <field> <value>                     # Установить поле в хеше
HGET <hash> <field>                             # Получить значение поля в хеше
HDEL <hash> <field>                             # Удалить поле из хеша
HGETALL <hash>                                  # Получить все поля и значения из хеша
HINCRBY <hash> <field> <increment>              # Увеличить значение поля на заданную величину

# 5. Операции с множествами
SADD <set> <member>                             # Добавить элемент в множество
SREM <set> <member>                             # Удалить элемент из множества
SMEMBERS <set>                                  # Получить все элементы множества
SISMEMBER <set> <member>                        # Проверить, является ли элемент членом множества
SCARD <set>                                     # Получить количество элементов в множестве

# 6. Операции с упорядоченными множествами
ZADD <zset> <score1> <member1> ...              # Добавить элемент с оценкой в упорядоченное множество
ZREM <zset> <member>                            # Удалить элемент из упорядоченного множества
ZRANGE <zset> <start> <end>                     # Получить элементы с определённого диапазона
ZREVRANGE <zset> <start> <end>                  # Получить элементы в обратном порядке
ZINCRBY <zset> <member> <increment>             # Увеличить оценку элемента

# 7. Операции с очередями (списки)
LPUSH <list> <value>                            # Добавить элемент в начало списка
RPUSH <list> <value>                            # Добавить элемент в конец списка
LPOP <list>                                     # Удалить и получить первый элемент списка
RPOP <list>                                     # Удалить и получить последний элемент списка
LRANGE <list> <start> <end>                     # Получить подсписок с заданными индексами
LLEN <list>                                     # Получить длину списка

# 9. Публикация/Подписка (Pub/Sub)
PUBLISH <channel> <message>                     # Отправить сообщение в канал
SUBSCRIBE <channel>                             # Подписаться на канал
UNSUBSCRIBE <channel>                           # Отписаться от канала
PSUBSCRIBE <pattern>                            # Подписаться на каналы по шаблону
PUNSUBSCRIBE <pattern>                          # Отписаться от каналов по шаблону

# 11. Транзакции
MULTI                                           # Начать транзакцию
EXEC                                            # Выполнить транзакцию
DISCARD                                         # Отменить транзакцию
WATCH <key>                                     # Следить за ключом и откатить транзакцию, если он был изменен

# 12. Репликация и кластеризация
SLAVEOF <host> <port>                           # Установить текущий сервер как реплику
INFO replication                                # Получить информацию о репликации
CLUSTER INFO                                    # Получить информацию о кластере

# 13. Управление Redis-сервером
SHUTDOWN                                        # Остановить Redis-сервер
SAVE                                            # Сохранить данные в файл на диск (синхронно)
BGSAVE                                          # Сохранить данные в файл на диск (асинхронно)
CONFIG GET <parameter>                          # Получить значение параметра конфигурации
CONFIG SET <parameter> <value>                  # Установить значение параметра конфигурации