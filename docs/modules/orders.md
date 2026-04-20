# Модуль: Заказы (`orders`)

Модуль управляет заказами клиентов и ведёт регистр накопления заказанных объёмов.

---

## Модели

### `Order` — Заказ клиента

**1С-аналог:** документ «Заказ клиента» в 1С:УТ

Наследуется от `Document` (номер, дата, статус проведения, кем/когда проведён, комментарий).

Содержит шапку заказа. Строки заказа хранятся в `OrderItem`. При проведении создаёт движения в `OrdersRegister`.

| Поле | Тип | Описание |
|------|-----|----------|
| `client` | FK → Client | Клиент |
| `counterparty` | FK → Counterparty | Контрагент (юрлицо клиента) |
| `contract` | FK → Contract | Договор |
| `currency` | FK → Currency | Валюта заказа |
| `order_status` | CharField | Рабочий статус заказа |

**Статусы документа** (из `DocumentStatus`):
- `draft` — Черновик (не проведён, движений нет)
- `posted` — Проведён (движения в регистре созданы)
- `cancelled` — Отменён

**Статусы заказа** (`order_status` — рабочий статус, не зависит от проведения):
- `new` — Новый
- `in_progress` — В работе
- `ready` — Готов
- `delivered` — Выдан
- `cancelled` — Отменён

**Проведение:**
```python
order.post(user=request.user)   # создаёт движения в OrdersRegister
order.unpost(user=request.user) # удаляет движения из OrdersRegister
```

**Реализация `_make_movements()`:**
Для каждой строки заказа создаётся запись в `OrdersRegister` с `activity=True` (приход), содержащая клиента, номенклатуру, количество и сумму.

---

### `OrderItem` — Строка заказа

**1С-аналог:** табличная часть «Товары» документа «Заказ клиента»

Наследуется от `OrgScopedModel`. Хранит одну позицию номенклатуры в заказе.

| Поле | Тип | Описание |
|------|-----|----------|
| `order` | FK → Order | Заказ |
| `nomenclature` | FK → Nomenclature | Товар/услуга |
| `quantity` | DecimalField(14,3) | Количество |
| `unit` | FK → UnitOfMeasure | Единица измерения |
| `price` | DecimalField(18,2) | Цена |
| `discount` | DecimalField(6,2) | Скидка (%) |
| `amount` | DecimalField(18,2) | Сумма (рассчитывается автоматически) |
| `vat_rate` | CharField | Ставка НДС |
| `vat_amount` | DecimalField(18,2) | Сумма НДС |

**Автоматический расчёт суммы** при `save()`:
```python
self.amount = self.quantity * self.price * (1 - self.discount / 100)
```

---

### `OrdersRegister` — Регистр накопления «Заказы клиентов»

**1С-аналог:** регистр накопления «Заказы клиентов» в 1С:УТ

Наследуется от `AccumulationRegisterMovement` (период, регистратор как GenericForeignKey, признак прихода/расхода).

Фиксирует движения по заказанному количеству и суммам.

| Измерение/Ресурс | Поле | Описание |
|------------------|------|----------|
| Измерение | `client` | Клиент |
| Измерение | `nomenclature` | Номенклатура |
| Ресурс | `quantity` | Заказанное количество |
| Ресурс | `amount` | Заказанная сумма |
| (из базового) | `period` | Дата движения |
| (из базового) | `recorder` | Документ-регистратор (Order) |
| (из базового) | `activity` | True=приход, False=расход |

**Индексы:** `(organization, client, period)` и `(organization, nomenclature, period)` для быстрых отчётов.

**Получение остатков заказов по клиенту:**
```python
from django.db.models import Sum, Case, When, F
from modules.orders.models import OrdersRegister

balance = OrdersRegister.objects.filter(
    organization=org, client=client,
).aggregate(
    quantity=Sum(Case(
        When(activity=True, then=F('quantity')),
        When(activity=False, then=-F('quantity')),
        default=0,
    )),
    amount=Sum(Case(
        When(activity=True, then=F('amount')),
        When(activity=False, then=-F('amount')),
        default=0,
    )),
)
```

---

## Процесс работы с заказом

```
Создать Order (status=draft)
    ↓
Добавить OrderItem (строки)
    ↓
order.post(user)
    → создаёт OrdersRegister записи (activity=True)
    → status → posted
    ↓
Изменить order_status: new → in_progress → ready → delivered
    ↓
При необходимости: order.unpost(user)
    → удаляет OrdersRegister записи
    → status → draft
```
