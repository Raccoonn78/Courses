# ============================================================
# ЗАНЯТИЕ 10: Модули и пакеты 
# ============================================================
# Темы:
#   1. Импорт модулей
#   2. Стандартная библиотека Python
#   3. Создание собственного модуля
#   4. Пакеты
#   5. pip — установка сторонних библиотек
# ============================================================


# ------------------------------------------------------------
# 1. СПОСОБЫ ИМПОРТА
# ------------------------------------------------------------
import math                     # импорт всего модуля
from math import sqrt, pi       # импорт конкретных имён
from math import factorial as fact  # с псевдонимом
import random as rnd            # модуль с псевдонимом

print("=== Способы импорта ===")
print(math.sqrt(16))      # 4.0 — через имя модуля
print(sqrt(25))           # 5.0 — напрямую
print(pi)                 # 3.14159...
print(fact(5))            # 120 — факториал


# ------------------------------------------------------------
# 2. МОДУЛЬ MATH
# ------------------------------------------------------------
print("\n=== math ===")

print(math.floor(3.7))     # 3  — округление вниз
print(math.ceil(3.2))      # 4  — округление вверх
print(round(3.567, 2))     # 3.57 — встроенная функция
print(math.pow(2, 10))     # 1024.0
print(math.log(100, 10))   # 2.0  — логарифм
print(math.sin(math.pi / 2))  # 1.0
print(math.inf)            # бесконечность


# ------------------------------------------------------------
# 3. МОДУЛЬ RANDOM
# ------------------------------------------------------------
print("\n=== random ===")

print(rnd.random())                 # случайный float [0, 1)
print(rnd.randint(1, 10))           # случайный int от 1 до 10 включительно
print(rnd.randrange(0, 100, 5))     # случайный из 0,5,10,...,95

items = ["яблоко", "банан", "вишня", "дыня"]
print(rnd.choice(items))            # случайный элемент
rnd.shuffle(items)                  # перемешать на месте
print(items)

sample = rnd.sample(range(1, 50), 6)  # 6 уникальных из диапазона
print(sorted(sample))               # случайные числа лотереи

rnd.seed(42)                        # фиксируем результат (воспроизводимость)
print(rnd.random())                 # всегда одно и то же число


# ------------------------------------------------------------
# 4. МОДУЛЬ DATETIME
# ------------------------------------------------------------
from datetime import datetime, date, timedelta

print("\n=== datetime ===")

now = datetime.now()
print(now)
print(now.year, now.month, now.day)
print(now.strftime("%d.%m.%Y %H:%M"))   # форматирование

birthday = date(1995, 8, 15)
today = date.today()
age_days = (today - birthday).days
print(f"Дней с рождения: {age_days}")

# Арифметика дат
tomorrow = today + timedelta(days=1)
week_ago = today - timedelta(weeks=1)
print(f"Завтра: {tomorrow}")
print(f"Неделю назад: {week_ago}")

# Парсинг даты из строки
date_str = "25.12.2024"
parsed = datetime.strptime(date_str, "%d.%m.%Y")
print(parsed.date())


# ------------------------------------------------------------
# 5. МОДУЛЬ OS И PATHLIB
# ------------------------------------------------------------
import os
from pathlib import Path

print("\n=== os / pathlib ===")

print(os.getcwd())                  # текущая директория
print(os.path.exists("step.py"))    # существует ли файл

# Pathlib — современный способ (Python 3.4+)
current = Path(".")
script = Path(__file__)             # путь к текущему файлу
print(script.name)                  # step.py
print(script.stem)                  # step
print(script.suffix)                # .py
print(script.parent)                # родительская директория


# ------------------------------------------------------------
# 6. МОДУЛЬ COLLECTIONS
# ------------------------------------------------------------
from collections import Counter, defaultdict, namedtuple

print("\n=== collections ===")

# Counter — подсчёт элементов
text = "hello world"
counter = Counter(text)
print(counter.most_common(3))    # [('l', 3), ('o', 2), (' ', 1)]

words = ["яблоко", "банан", "яблоко", "вишня", "банан", "яблоко"]
word_count = Counter(words)
print(word_count)

# defaultdict — словарь с дефолтным значением
groups = defaultdict(list)
students = [("A", "Анна"), ("B", "Борис"), ("A", "Вера"), ("B", "Гриша")]
for group, name in students:
    groups[group].append(name)
print(dict(groups))    # {'A': ['Анна', 'Вера'], 'B': ['Борис', 'Гриша']}

# namedtuple — кортеж с именованными полями
Point = namedtuple("Point", ["x", "y"])
p = Point(10, 20)
print(p.x, p.y)        # 10 20 — доступ по имени
print(p[0], p[1])      # 10 20 — доступ по индексу


# ------------------------------------------------------------
# 7. МОДУЛЬ ITERTOOLS
# ------------------------------------------------------------
import itertools

print("\n=== itertools ===")

# chain — объединить итерируемые объекты
chained = list(itertools.chain([1, 2], [3, 4], [5]))
print(chained)    # [1, 2, 3, 4, 5]

# product — декартово произведение (все комбинации)
pairs = list(itertools.product("AB", [1, 2]))
print(pairs)      # [('A',1), ('A',2), ('B',1), ('B',2)]

# combinations — комбинации без повторений
combos = list(itertools.combinations([1, 2, 3, 4], 2))
print(combos)

# takewhile — брать пока условие True
result = list(itertools.takewhile(lambda x: x < 5, [1, 2, 3, 4, 5, 6]))
print(result)    # [1, 2, 3, 4]


# ============================================================
# ДОМАШНЕЕ ЗАДАНИЕ:
#
# 1. Используя модуль random:
#    Напиши симулятор броска кубика (6 граней).
#    Бросай кубик 1000 раз, подсчитай частоту каждого числа
#    и выведи результаты в виде:
#    "1: 167 раз (16.7%)"
#
# 2. Используя модуль datetime:
#    Напиши функцию days_until_new_year(), которая возвращает
#    количество дней до 1 января следующего года.
#
# 3. Используя Counter из collections:
#    Возьми любое длинное предложение на русском языке.
#    Найди 5 самых часто встречающихся букв (не считая пробелы).
# ============================================================
