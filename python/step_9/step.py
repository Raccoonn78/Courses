# ============================================================
# ЗАНЯТИЕ 9: Обработка ошибок и работа с файлами 
# ============================================================
# Темы:
#   1. Типы ошибок
#   2. try / except / else / finally
#   3. Создание собственных исключений
#   4. Работа с файлами (чтение и запись)
#   5. Контекстный менеджер with
# ============================================================


# ------------------------------------------------------------
# 1. ТИПЫ ОШИБОК (исключений)
# ------------------------------------------------------------
# SyntaxError    — ошибка синтаксиса (код не запустится)
# NameError      — переменная не определена
# TypeError      — неверный тип данных
# ValueError     — неверное значение
# IndexError     — индекс за пределами списка
# KeyError       — ключ не найден в словаре
# ZeroDivisionError — деление на ноль
# FileNotFoundError — файл не найден


# ------------------------------------------------------------
# 2. TRY / EXCEPT — перехватываем ошибки
# ------------------------------------------------------------
print("=== try/except ===")

# Без обработки — программа упадёт:
# print(10 / 0)   # ZeroDivisionError

# С обработкой — программа продолжит работу:
try:
    result = 10 / 0
except ZeroDivisionError:
    print("Ошибка: деление на ноль!")

# Несколько except — перехватываем разные ошибки
def safe_divide(a, b):
    try:
        result = a / b
        return result
    except ZeroDivisionError:
        print("Деление на ноль!")
        return None
    except TypeError:
        print("Нельзя делить нечисла!")
        return None

print(safe_divide(10, 2))    # 5.0
print(safe_divide(10, 0))    # ошибка → None
print(safe_divide(10, "a"))  # ошибка → None


# ------------------------------------------------------------
# 3. ELSE И FINALLY
# ------------------------------------------------------------
print("\n=== else / finally ===")

# else — выполняется, если ошибки НЕ было
# finally — выполняется ВСЕГДА (ошибка или нет)

def convert_to_int(s):
    try:
        number = int(s)
    except ValueError:
        print(f"'{s}' нельзя преобразовать в число")
    else:
        print(f"Успешно: {number}")    # только при успехе
        return number
    finally:
        print("Функция завершила работу")   # всегда

convert_to_int("42")
print()
convert_to_int("abc")


# ------------------------------------------------------------
# 4. ПЕРЕХВАТ ЛЮБОГО ИСКЛЮЧЕНИЯ + ИНФОРМАЦИЯ ОБ ОШИБКЕ
# ------------------------------------------------------------
print("\n=== Информация об ошибке ===")

data = [1, 2, 3]

try:
    print(data[10])
except IndexError as e:
    print(f"Ошибка: {e}")           # list index out of range

try:
    x = int("не число")
except Exception as e:              # Exception — родитель всех ошибок
    print(f"Тип: {type(e).__name__}, Сообщение: {e}")


# ------------------------------------------------------------
# 5. СОЗДАНИЕ СОБСТВЕННЫХ ИСКЛЮЧЕНИЙ
# ------------------------------------------------------------
print("\n=== Собственные исключения ===")

class AgeError(Exception):
    """Ошибка при неверном возрасте."""
    pass

class NegativeAmountError(Exception):
    pass

def set_age(age):
    if not isinstance(age, int):
        raise TypeError("Возраст должен быть целым числом")
    if age < 0 or age > 150:
        raise AgeError(f"Недопустимый возраст: {age}")
    return age

try:
    set_age(200)
except AgeError as e:
    print(f"AgeError: {e}")

try:
    set_age("двадцать")
except TypeError as e:
    print(f"TypeError: {e}")


# ------------------------------------------------------------
# 6. РАБОТА С ФАЙЛАМИ
# ------------------------------------------------------------
print("\n=== Файлы ===")

import os

# ЗАПИСЬ В ФАЙЛ
# mode:
#   "w" — перезаписать (создаст если нет)
#   "a" — дописать в конец
#   "r" — только чтение (по умолчанию)
#   "x" — создать (ошибка если уже есть)

filename = "test_file.txt"

with open(filename, "w", encoding="utf-8") as f:
    f.write("Первая строка\n")
    f.write("Вторая строка\n")
    f.write("Третья строка\n")

print("Файл создан")

# ЧТЕНИЕ ФАЙЛА
with open(filename, "r", encoding="utf-8") as f:
    content = f.read()          # читаем весь файл как строку
print(content)

# Чтение построчно
with open(filename, "r", encoding="utf-8") as f:
    for line in f:
        print(line.strip())     # strip убирает \n

# Чтение в список строк
with open(filename, "r", encoding="utf-8") as f:
    lines = f.readlines()       # ['Первая строка\n', ...]
print(lines)

# ДОЗАПИСЬ В ФАЙЛ
with open(filename, "a", encoding="utf-8") as f:
    f.write("Добавленная строка\n")

# РАБОТА С JSON-ФАЙЛАМИ
import json


data = {
    "name": "Алексей",
    "age": 25,
    "skills": ["Python", "SQL", "Git"]
}

# Запись JSON
with open("data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# Чтение JSON
with open("data.json", "r", encoding="utf-8") as f:
    loaded = json.load(f)

print(loaded)
print(loaded["skills"])

# Очистка тестовых файлов
os.remove(filename)
os.remove("data.json")
print("Файлы удалены")


# ------------------------------------------------------------
# 7. ОБРАБОТКА ОШИБОК ПРИ РАБОТЕ С ФАЙЛАМИ
# ------------------------------------------------------------
print("\n=== Ошибки файлов ===")

try:
    with open("несуществующий_файл.txt", "r") as f:
        content = f.read()
except FileNotFoundError:
    print("Файл не найден!")
except PermissionError:
    print("Нет доступа к файлу!")


# ============================================================
# ДОМАШНЕЕ ЗАДАНИЕ:
#
# 1. Напиши функцию safe_input(prompt, type_func),
#    которая запрашивает ввод от пользователя,
#    преобразует через type_func, и при ошибке просит ввести снова.
#    Например: safe_input("Введите число: ", int)
#
# 2. Создай файл "students.txt" и запиши в него 5 имён студентов,
#    каждое с новой строки. Затем прочитай файл и выведи
#    только те имена, которые начинаются с буквы "А".
#
# 3. Создай класс исключения NegativeNumberError.
#    Напиши функцию square_root(n), которая:
#    - возбуждает NegativeNumberError если n < 0
#    - иначе возвращает корень из n (используй ** 0.5)
#    Оберни вызов в try/except и выведи понятное сообщение.
# ============================================================
