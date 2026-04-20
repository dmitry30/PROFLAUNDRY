# Модуль: Расчёты (`billing`)

Модуль управляет счетами на оплату, оплатами и регистром взаиморасчётов с клиентами.

---

## Модели

### `Invoice` — Счёт на оплату

**1С-аналог:** документ «Счёт на оплату покупателю» в 1С:УТ

Наследуется от `Document`. Счёт **не создаёт движений в регистрах** при проведении — является только основанием для оплаты. Движения создаёт только `Payment`.

| Поле | Тип | Описание |
|------|-----|----------|
| `client` | FK → Client | Клиент |
| `counterparty` | FK → Counterparty | Контрагент (юрлицо) |
| `contract` | FK → Contract | Договор |
| `currency` | FK → Currency | Валюта |
| `order` | FK → Order | Заказ-основание (необязательно) |

Строки счёта хранятся в `InvoiceItem`.

---

### `InvoiceItem` — Строка счёта

**1С-аналог:** табличная часть «Товары» документа «Счёт на оплату»

Наследуется от `OrgScopedModel`.

| Поле | Тип | Описание |
|------|-----|----------|
| `invoice` | FK → Invoice | Счёт |
| `nomenclature` | FK → Nomenclature | Товар/услуга |
| `quantity` | DecimalField(14,3) | Количество |
| `price` | DecimalField(18,2) | Цена |
| `amount` | DecimalField(18,2) | Сумма (рассчитывается автоматически) |

**Автоматический расчёт:** `amount = quantity * price` при `save()`.

---

### `Payment` — Оплата от клиента

**1С-аналог:** документ «Поступление денежных средств» в 1С:УТ

Наследуется от `Document`. При проведении создаёт запись в `SettlementsRegister` с `activity=True` (приход = погашение задолженности клиента).

| Поле | Тип | Описание |
|------|-----|----------|
| `client` | FK → Client | Клиент |
| `counterparty` | FK → Counterparty | Контрагент |
| `contract` | FK → Contract | Договор |
| `currency` | FK → Currency | Валюта |
| `amount` | DecimalField(18,2) | Сумма оплаты |
| `payment_type` | CharField | Вид оплаты |

**Виды оплаты:**
- `cash` — Наличные
- `bank` — Безналичные
- `card` — Карта
- `other` — Прочее

**Проведение:**
```python
payment.post(user=request.user)
# Создаёт SettlementsRegister(activity=True, amount=payment.amount, ...)
```

---

### `SettlementsRegister` — Регистр накопления «Взаиморасчёты с клиентами»

**1С-аналог:** регистр накопления «Взаиморасчёты с клиентами» в 1С:УТ

Наследуется от `AccumulationRegisterMovement`. Фиксирует задолженность клиента перед организацией.

| Измерение/Ресурс | Поле | Описание |
|------------------|------|----------|
| Измерение | `client` | Клиент |
| Измерение | `counterparty` | Контрагент (юрлицо) |
| Измерение | `contract` | Договор |
| Ресурс | `amount` | Сумма |
| (из базового) | `period` | Дата движения |
| (из базового) | `recorder` | Документ-регистратор (Payment) |
| (из базового) | `activity` | True=приход (оплата), False=расход (начисление) |

**Индексы:** `(organization, client, period)` и `(organization, counterparty, contract, period)`.

**Получение текущей задолженности клиента:**
```python
from django.db.models import Sum, Case, When, F
from modules.billing.models import SettlementsRegister

balance = SettlementsRegister.objects.filter(
    organization=org, client=client,
).aggregate(
    debt=Sum(Case(
        When(activity=True, then=F('amount')),
        When(activity=False, then=-F('amount')),
        default=0,
    ))
)
# balance['debt'] > 0 → клиент оплатил больше, чем должен (переплата)
# balance['debt'] < 0 → клиент в долгу (задолженность)
```

---

## Процесс взаиморасчётов

```
Order (заказ) — проведение → OrdersRegister (фиксирует объёмы)
     ↓
Invoice (счёт на оплату) — создаётся на основе Order
     ↓
Payment (оплата) — проведение → SettlementsRegister (фиксирует оплату)
```

Регистр `SettlementsRegister` показывает текущее состояние взаиморасчётов: сколько оплачено и сколько ещё причитается по договору.
