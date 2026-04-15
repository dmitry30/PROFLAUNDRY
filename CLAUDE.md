# CLAUDE.md — контекст проекта PROFLAUNDRY

## Docs Portal

Документация проекта хранится в `docs/` и синхронизируется с порталом документации через `docs.yaml`.

**Как устроен портал и правила форматирования:**
→ вызови `mcp__docs-portal__docs_get_rules` в начале любой сессии где работаешь с документацией.

## Как узнать о проекте и его структуре

### Через MCP (предпочтительно)

```
# Общий обзор проекта: стек, дерево страниц, активные изменения
mcp__docs-portal__docs_project_overview(project="PROFLAUNDRY")

# Дерево страниц без содержимого
mcp__docs-portal__docs_get_tree(project="PROFLAUNDRY")

# Содержимое конкретной страницы
mcp__docs-portal__docs_get_page(project="PROFLAUNDRY", page_id="business")
mcp__docs-portal__docs_get_page(project="PROFLAUNDRY", page_id="business.statements")
```

### Локально

```
docs.yaml          # структура страниц и настройки
docs/              # все markdown-страницы
mind.md            # открытые вопросы и пробелы (читать перед новой сессией)
```

## Ключевые страницы документации

| page_id | Что там |
|---------|---------|
| `business` | Общая карта бизнес-процесса |
| `business.statements` | Все зафиксированные утверждения BP-001..N |
| `business.order` | Жизненный цикл заказа |
| `business.reception` | Приёмка (сессия обработки) |
| `business.nomenclature` | Номенклатура, группы, прайс-лист |
| `business.logistics` | Логистика (универсальный модуль) |
| `business.billing` | Расчётный лист |

## Текущий этап работы

Бизнес-процесс → **Модели Django** → Архитектура приложений → UI.

Перед началом новой сессии: прочитай `mind.md` и `business.statements`.
