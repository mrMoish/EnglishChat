# GDP Report Generator

Небольшая консольная утилита на Python для анализа экономических данных из CSV-файлов и формирования отчётов.

## Возможности

- 📊 Анализирует один или несколько CSV-файлов.
- 📈 Вычисляет средний показатель GDP.
- 🖥️ Выводит результаты в виде аккуратной таблицы.
- ➕ Легко расширяется новыми типами отчётов.

---

## Структура проекта

```
.
├── main.py
├── economic1.csv
├── economic2.csv
├── screenshot.png
└── README.md
```

---

## Требования

- Python 3.10+
- Библиотека `tabulate`

---

## Установка

### 1. Клонировать репозиторий

```bash
git clone https://github.com/mrMoish/gdp.git
cd gdp
```

### 2. Создать виртуальное окружение

macOS / Linux

```bash
python -m venv venv
source venv/bin/activate
```

Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Установить зависимости

```bash
pip install tabulate
```

---

## Запуск

Пример запуска:

```bash
python main.py \
    --files economic1.csv economic2.csv \
    --report average-gdp
```

или одной строкой

```bash
python main.py --files economic1.csv economic2.csv --report average-gdp
```

---

## Пример результата

![Результат работы](screenshot.png)

---

## Добавление нового отчёта

Добавить собственный отчёт очень просто.

### Шаг 1

Создайте функцию формирования отчёта.

```python
def build_new_report(rows):
    ...
```

### Шаг 2

Добавьте обработку нового типа отчёта в `main()`.

```python
if args.report == "average-gdp":
    report = build_average_gdp_report(rows)

elif args.report == "new-report":
    report = build_new_report(rows)

else:
    print(f"Report '{args.report}' is not supported.")
```

После этого новый отчёт можно запускать командой

```bash
python main.py --files economic1.csv --report new-report
```

---

## Используемые технологии

- Python
- argparse
- csv
- tabulate

---
