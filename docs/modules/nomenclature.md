# Модуль: Номенклатура (`nomenclature`)

Модуль управляет товарами/услугами/работами и ценами на них.

---

## Модели

### `Nomenclature` — Номенклатура

**1С-аналог:** справочник «Номенклатура» в 1С:УТ

Наследуется от `CatalogItem` (поддерживает иерархию: папки и элементы, пометку удаления).

Является главной единицей учёта в документах и регистрах. Все строки заказов, счетов ссылаются на `Nomenclature`.

| Поле | Тип | Описание |
|------|-----|----------|
| `nomenclature_type` | CharField | Вид: `goods` / `service` / `work` |
| `article` | CharField(100) | Артикул (необязательно) |
| `unit` | FK → UnitOfMeasure | Базовая единица измерения |
| `weight` | DecimalField(10,3) | Вес в кг (для товаров) |
| `volume` | DecimalField(10,3) | Объём в м³ (для товаров) |
| `vat_rate` | CharField | Ставка НДС: `none` / `0` / `10` / `20` |

**Виды номенклатуры:**
- `goods` — Товар (материальный)
- `service` — Услуга
- `work` — Работа

**Ставки НДС:**
- `none` — Без НДС
- `0` — 0%
- `10` — 10%
- `20` — 20%

---

### `PriceType` — Вид цены

**1С-аналог:** справочник «Виды цен» в 1С:УТ

Определяет ценовую категорию (например: «Розничная», «Оптовая», «VIP»). Каждый вид цены привязан к конкретной валюте.

| Поле | Тип | Описание |
|------|-----|----------|
| `name` | CharField(200) | Наименование (уникально в рамках организации) |
| `currency` | FK → Currency | Валюта |
| `is_deleted` | BooleanField | Пометка удаления |

---

### `PriceRegister` — Цены номенклатуры

**1С-аналог:** регистр сведений «Цены номенклатуры» в 1С:УТ

Наследуется от `InformationRegisterRecord` — **периодический регистр сведений**.

Хранит актуальную цену номенклатуры в разрезе вида цены на каждый момент времени. При запросе цены на дату берётся последняя запись с `period <= запрашиваемая_дата`.

| Поле | Тип | Описание |
|------|-----|----------|
| `nomenclature` | FK → Nomenclature | Номенклатура |
| `price_type` | FK → PriceType | Вид цены |
| `price` | DecimalField(18,2) | Цена |
| `currency` | FK → Currency | Валюта цены |
| `period` | DateTimeField | Период действия цены (из базового класса) |
| `recorder` | GenericForeignKey | Документ, установивший цену (из базового класса) |

**Как получить актуальную цену:**
```python
from modules.nomenclature.models import PriceRegister
record = PriceRegister.objects.filter(
    organization=org,
    nomenclature=nomenclature,
    price_type=price_type,
    period__lte=timezone.now(),
).order_by('-period').first()
price = record.price if record else None
```

---

## Схема связей

```
UnitOfMeasure ←── Nomenclature
                       ↑
Currency ←── PriceType ↑
                 ↑
             PriceRegister (периодический регистр сведений)
```
