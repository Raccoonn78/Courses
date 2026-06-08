# ============================================================
# ЗАНЯТИЕ 11: Генераторы и декораторы (~50 мин)
# ============================================================
# Темы:
#   1. Генераторы (yield)
#   2. Generator expression
#   3. Декораторы
#   4. functools.wraps
#   5. Декораторы с аргументами
# ============================================================


# ------------------------------------------------------------
# 1. ГЕНЕРАТОРЫ — функции которые "ленивo" генерируют значения
# ------------------------------------------------------------
# Обычная функция возвращает всё сразу.
# Генератор возвращает по одному значению через yield,
# не храня всё в памяти — идеально для больших данных.

print("=== Генераторы ===")

# Обычная функция — создаёт список целиком в памяти
def squares_list(n):
    result = []
    for i in range(n):
        result.append(i ** 2)
    return result

# Генератор — вычисляет каждое значение только когда нужно
def squares_gen(n):
    for i in range(n):
        yield i ** 2    # yield "замораживает" функцию и отдаёт значение

# Использование
gen = squares_gen(5)
print(type(gen))            # <class 'generator'>
print(next(gen))            # 0
print(next(gen))            # 1
print(next(gen))            # 4

# Итерация в цикле
for sq in squares_gen(5):
    print(sq, end=" ")
print()

# Конвертация в список
print(list(squares_gen(6)))    # [0, 1, 4, 9, 16, 25]


# Генератор бесконечной последовательности (fibonacci)
def fibonacci():
    a, b = 0, 1
    while True:          # бесконечный цикл — но память не кончится!
        yield a
        a, b = b, a + b

fib = fibonacci()
print([next(fib) for _ in range(10)])    # первые 10 чисел Фибоначчи


# ------------------------------------------------------------
# 2. GENERATOR EXPRESSION — как list comprehension, но ленивый
# ------------------------------------------------------------
print("\n=== Generator expression ===")

# List comprehension — всё в памяти сразу
list_comp = [x**2 for x in range(1_000_000)]    # занимает память

# Generator expression — скобки вместо квадратных
gen_expr = (x**2 for x in range(1_000_000))     # почти не занимает память

print(type(gen_expr))    # <class 'generator'>
print(sum(gen_expr))     # можно передать в sum, min, max

# Практический пример: чтение большого файла
# with open("huge_file.txt") as f:
#     long_lines = (line for line in f if len(line) > 100)
#     for line in long_lines:
#         process(line)


# ------------------------------------------------------------
# 3. ДЕКОРАТОРЫ — функции которые "оборачивают" другие функции
# ------------------------------------------------------------
# Декоратор позволяет добавить поведение к функции без изменения её кода.
# Синтаксис: @decorator_name над функцией

print("\n=== Декораторы ===")

# Простой декоратор: логирование вызовов
def logger(func):
    def wrapper(*args, **kwargs):
        print(f"Вызов: {func.__name__}{args}")
        result = func(*args, **kwargs)
        print(f"Результат: {result}")
        return result
    return wrapper

@logger                          # эквивалентно: add = logger(add)
def add(a, b):
    return a + b

add(3, 5)
add(10, 20)


# Декоратор: измерение времени выполнения
import time

def timer(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        print(f"{func.__name__} выполнилась за {elapsed:.4f} сек")
        return result
    return wrapper

@timer
def slow_sum(n):
    return sum(range(n))

slow_sum(10_000_000)


# ------------------------------------------------------------
# 4. FUNCTOOLS.WRAPS — сохраняем метаданные функции
# ------------------------------------------------------------
from functools import wraps

print("\n=== functools.wraps ===")

def my_decorator(func):
    @wraps(func)                 # сохраняет __name__, __doc__ и т.д.
    def wrapper(*args, **kwargs):
        print("До функции")
        result = func(*args, **kwargs)
        print("После функции")
        return result
    return wrapper

@my_decorator
def greet(name):
    """Функция приветствия."""
    print(f"Привет, {name}!")

greet("Алексей")
print(greet.__name__)    # greet — благодаря @wraps


# ------------------------------------------------------------
# 5. НЕСКОЛЬКО ДЕКОРАТОРОВ
# ------------------------------------------------------------
# Декораторы применяются снизу вверх

def bold(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return f"<b>{func(*args, **kwargs)}</b>"
    return wrapper

def italic(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        return f"<i>{func(*args, **kwargs)}</i>"
    return wrapper

@bold                # применяется вторым
@italic              # применяется первым
def format_text(text):
    return text

print(format_text("Hello"))    # <b><i>Hello</i></b>


# ------------------------------------------------------------
# 6. ДЕКОРАТОР С АРГУМЕНТАМИ
# ------------------------------------------------------------
print("\n=== Декоратор с аргументами ===")

def repeat(times):
    """Повторяет функцию указанное количество раз."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for _ in range(times):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

@repeat(3)
def say_hello():
    print("Привет!")

say_hello()    # напечатает 3 раза


# Декоратор кэширования (memoize)
def memoize(func):
    cache = {}
    @wraps(func)
    def wrapper(*args):
        if args not in cache:
            cache[args] = func(*args)
        return cache[args]
    return wrapper

@memoize
def fib(n):
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)

print([fib(i) for i in range(10)])    # быстро, благодаря кэшу

# Python предоставляет встроенный кэш:
from functools import lru_cache

@lru_cache(maxsize=None)
def fib_lru(n):
    if n <= 1:
        return n
    return fib_lru(n - 1) + fib_lru(n - 2)

print(fib_lru(50))


# ============================================================
# ДОМАШНЕЕ ЗАДАНИЕ:
#
# 1. Напиши генератор even_numbers(start, end), который
#    генерирует все чётные числа в диапазоне [start, end].
#    Используй его для вычисления суммы чётных чисел от 1 до 1000.
#
# 2. Напиши декоратор validate_positive, который проверяет,
#    что все числовые аргументы функции положительны.
#    Если нет — выбрасывай ValueError с понятным сообщением.
#    Применить к функции area(width, height) = width * height.
#
# 3. Используя lru_cache, напиши функцию factorial(n)
#    и сравни скорость с обычной рекурсивной версией
#    (используй модуль time).
# ============================================================
