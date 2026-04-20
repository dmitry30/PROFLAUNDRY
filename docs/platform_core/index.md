# platform_core — Ядро платформы

`platform_core` — Django-приложение, содержащее всю платформенную логику: модели организаций, сотрудников, ролей, абстрактные базовые классы для модулей, общие справочники и три AdminSite.

---

## Структура моделей

### Организация и мультиарендность

| Модель | Описание | 1С-аналог |
|--------|----------|-----------|
| `Organization` | Организация/арендатор. Поле `slug` используется для роутинга. | Организация в ИБ |
| `OrganizationModule` | Список включённых модулей для каждой организации. | — |

Все данные организации изолированы через FK `organization`. Запросы фильтруются автоматически через `OrgFilteredMixin` в AdminSite.

### Пользователи и роли

| Модель | Описание | 1С-аналог |
|--------|----------|-----------|
| `Employee` | Заменяет `django.contrib.auth.User`. Уникален по `(organization, username)`. `organization=None` — платформенный суперадмин. | Пользователь ИБ |
| `MetaRole` | Шаблон роли на уровне платформы. | Шаблон профиля пользователя |
| `OrgRole` | Роль внутри конкретной организации. M2M на `Permission`. | Профиль пользователя |

**Три уровня доступа:**
- `/platform/` — платформенный AdminSite, только `is_superuser` с `organization=None`
- `/app/` — AdminSite организации, `Employee` с активной ролью
- `/portal/` — портал клиентов (в разработке)

### Константы

| Модель | Описание | 1С-аналог |
|--------|----------|-----------|
| `OrgConstant` | Ключ-значение (JSONField) на уровне организации. Методы `get()`/`set()`. | Константы |

### Общие справочники платформы

Эти справочники **не привязаны к организации** — они общие для всей платформы:

| Модель | Описание |
|--------|----------|
| `Currency` | Валюты (ISO 4217): RUB, USD, EUR и др. |
| `UnitOfMeasure` | Единицы измерения: шт, кг, м², л и др. |
| `Bank` | Банки: БИК, наименование, кор. счёт, город. |

### Справочник счетов

| Модель | Описание | 1С-аналог |
|--------|----------|-----------|
| `ChartOfAccountsItem` | Иерархический план счетов организации. Поля: `code`, `name`, `parent`, `is_group`, `account_type` (active/passive/ap). | План счетов |

---

## Абстрактные базовые классы

Все модели модулей **наследуются** от этих классов. Менять их нужно осторожно — изменения затронут все наследников.

### `TimeStampedModel`
```python
created_at = DateTimeField(auto_now_add=True)
updated_at = DateTimeField(auto_now=True)
```
Добавляет поля аудита времени ко всем моделям.

### `OrgScopedModel(TimeStampedModel)`
```python
organization = ForeignKey(Organization, ...)
```
Базовый класс для всего, что принадлежит организации.

### `CatalogItem(OrgScopedModel)` — Справочник
```python
code       = CharField(max_length=50, blank=True)   # Код элемента
name       = CharField(max_length=500)               # Наименование
description = TextField(blank=True)                  # Описание
is_group   = BooleanField(default=False)             # Это группа?
is_deleted = BooleanField(default=False)             # Пометка удаления
parent     = ForeignKey('self', null=True)           # Родительская группа
sort_order = PositiveIntegerField(default=0)         # Порядок сортировки
```
**Методы:** `mark_deleted()`, `restore()`

Используется для: `Counterparty`, `Client`, `Contract`, `Nomenclature`.

### `Document(OrgScopedModel)` — Документ
```python
number    = CharField(max_length=50, blank=True)  # Номер документа
date      = DateField()                           # Дата
status    = CharField(choices=DocumentStatus)     # draft / posted / cancelled
posted_at = DateTimeField(null=True)              # Когда проведён
posted_by = ForeignKey(Employee, null=True)       # Кем проведён
comment   = TextField(blank=True)
```
**Статусы:** `DRAFT` (черновик), `POSTED` (проведён), `CANCELLED` (отменён)

**Методы проведения:**
- `post(user)` — проводит документ, вызывает `_make_movements()`
- `unpost(user)` — отменяет проведение, вызывает `_reverse_movements()`
- `_make_movements()` — переопределяется в модуле для создания движений в регистрах
- `_reverse_movements()` — переопределяется для удаления движений

Используется для: `Order`, `Invoice`, `Payment`.

### `AccumulationRegisterMovement(OrgScopedModel)` — Регистр накопления
```python
period       = DateTimeField(db_index=True)        # Период записи
recorder_type = ForeignKey(ContentType, null=True)  # Тип документа-регистратора
recorder_id  = PositiveBigIntegerField(null=True)   # ID документа-регистратора
recorder     = GenericForeignKey(...)               # Документ-регистратор
activity     = BooleanField(default=True)           # True=приход, False=расход
```
**Метод:** `reverse()` — создаёт обратную запись (для отмены проведения).

Используется для: `OrdersRegister`, `SettlementsRegister`.

### `InformationRegisterRecord(OrgScopedModel)` — Регистр сведений
```python
period       = DateTimeField(null=True)  # null для непериодических
recorder_type/recorder_id/recorder = GenericForeignKey
```
Используется для: `PriceRegister`.

### `AccountingEntry(OrgScopedModel)` — Регистр бухгалтерии
```python
period         = DateTimeField()
recorder       = GenericForeignKey
debit_account  = ForeignKey(ChartOfAccountsItem)
credit_account = ForeignKey(ChartOfAccountsItem)
amount         = DecimalField(18,2)
currency       = ForeignKey(Currency, null=True)
```
Абстрактный базовый класс для бухгалтерских проводок (двойная запись).

---

## История изменений

Все модели платформы зарегистрированы в `django-auditlog` через `apps.py::ready()`. Auditlog автоматически записывает:
- кто изменил (`actor`)
- что изменилось (`changes` — JSON diff)
- когда (`timestamp`)
- откуда (`remote_addr`)

Просмотр истории доступен в `/platform/` через стандартный интерфейс auditlog.
