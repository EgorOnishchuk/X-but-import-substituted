# Tweeter (X) — импортозамещённая версия популярной соцсети

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)
![Pytest](https://img.shields.io/badge/pytest-%23ffffff.svg?style=for-the-badge&logo=pytest&logoColor=2f9fe3)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

## Из этого руководства Вы узнаете:

1. Как быстро начать работу — запустить проект «из коробки»
2. Как использовать продвинутую конфигурацию (требуются знания из ч. 1)

## Быстрый старт

Установка предельно проста:

```bash
git clone https://github.com/EgorOnishchuk/X-but-import-substituted
```

После клонирования репозитория Вам необходимо создать файл **.env** в корне проекта по шаблону из **.env.template**. 
Также клиентам могут потребоваться статические файлы: их можно разместить в папке **static**.
Далее — проверьте наличие актуальной версии **Docker** (настоятельно рекомендую воспользоваться 
[официальной инструкцией](https://docs.docker.com/engine/install/ "Документация Docker")). 

Хорошей практикой будет тестирование проекта перед каждым его развёртыванием — сделаем это:

```bash
docker compose --profile test up
```

> Не приступайте к следующим шагам, если хотя бы один из тестов будет провален, это может обернуться серьёзными 
> ошибками, в т.ч. «тихими» (например, бреши в безопасности, которые будут незаметны от Вас, но которыми могут 
> воспользоваться злоумышленники).

После прохождения всех проверок снова отредактируйте **.env** (если необходимо) и выполните самую важную команду:

```bash
docker compose --profile prod up
```

Теперь Ваш проект должен быть доступен по адресу **http://localhost:<указанный порт>**. Журналы событий пишутся в
_/var/lib/docker/containers/<ID контейнера>/*.log_, откуда могут быть собраны централизованными системами
(например, _ELK_).

## Продвинутая конфигурация

Прежде чем дорабатывать модули приложения под себя следует кратко описать архитектуру. Моей целью было 
создание веб-сервиса, который:

* полностью соответствует идеологии _серверного MVC_
* разделён на слои _репозиторий — сервис — контроллер_, общающиеся через _DTO_
* совместим с различными _ORM_ (и другими хранилищами данных), а также _валидаторами_
* не перегружен абстракциями: присутствует только то, в чём действительно есть необходимость

Рассмотрим три основных сценария написания собственной функциональности для нашего отечественного Твиттера.

### Как перейти на другое хранилище данных?

Перейдём к **repositories.py**, расположенному в _src_: здесь находится репозиторий _SQLAlchemy_ (но Вы можете 
называть его _DAO_ или как-то ещё — разница между ними весьма условная) с уже реализованным типовым функционалом для
CRUD. В **models.py** находятся _модели_, которые используются как _Data Mapper_ в самих репозиториях.

Сервисы в папках для каждой из сущностей следуют принципу _инверсии зависимостей_, а это значит, что для перехода на 
другое хранилище данных (например, SQLModel, TortoiseORM и т.д.) достаточно:

1. Создать новую модель — поможет документация соответствующей технологии
2. Создать новый репозиторий
3. Изменить конфигурацию сервиса через _инъекцию зависимости_ FastAPI

Более того, хранилище может и не быть _реляционным_. Так сделано, например, для изображений, которые хранятся в 
файловой системе (**FileSystemMediaRepository** из _src/medias/services.py_) и моделей для них вообще не предусмотрено.

### Как перейти на другого поставщика схем (Attrs, Marshmallow и т.д.)?

1. Создать новую схему — наследника Schema в **schemas.py**
2. Применить её к выходным и/или входным данным репозитория через соответствующие декораторы

Отметим, что схемы Pydantic используются в FastAPI для генерации документации OpenAPI: скорее всего, сохранить их в 
проекте всё равно придётся.

### Как создать новую доменную модель?

Я рекомендую придерживаться такой файловой структуры, в которой каждой сущности API соответствует своя папка как минимум
с пятью файлами: маршруты, сервисы, репозитории, схемы и зависимости. Это позволяет облегчить переход в будущем с
монолита на микросервисную архитектуру (шаблон _Strangler Fig_ и т.д.).

### Авторы

* [Егор Онищук](https://github.com/EgorOnishchuk "Профиль в GitLab") — разработка, тестирование и
  документирование
* [Skillbox](https://skillbox.ru/ "Платформа") — кураторство
