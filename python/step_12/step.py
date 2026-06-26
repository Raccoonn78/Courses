# ============================================================
# ЗАНЯТИЕ 12: ООП — Часть 1. Классы и объекты 
# ============================================================
# Темы:
#   1. Что такое ООП
#   2. Класс и объект
#   3. Атрибуты и методы
#   4. __init__ и __str__
#   5. Атрибуты класса vs атрибуты экземпляра
#   6. Инкапсуляция (публичные / приватные)
# ============================================================


# ------------------------------------------------------------
# 1. ЧТО ТАКОЕ ООП
# ------------------------------------------------------------
# ООП — способ организации кода через "объекты".
# Объект = данные (атрибуты) + поведение (методы).
# Класс — это шаблон (чертёж) для создания объектов.

# Пример из жизни:
# Класс "Автомобиль" — шаблон
# Объект — конкретный BMW X5 синего цвета, 2020 года


# ------------------------------------------------------------
# 2. СОЗДАНИЕ КЛАССА
# ------------------------------------------------------------
print("=== Базовый класс ===")

class Dog:
    # __init__ — конструктор, вызывается при создании объекта
    # self — ссылка на сам объект (обязательный первый параметр!)
    def __init__(self, name, breed, age):
        self.name = name        # атрибут экземпляра
        self.breed = breed
        self.age = age

    # Метод — функция внутри класса
    def bark(self):
        print(f"{self.name}: Гав!")

    def info(self):
        print(f"{self.name} — {self.breed}, {self.age} лет")

# Создание объектов (экземпляров класса)
dog1 = Dog("Рекс", "Немецкая овчарка", 3)
dog2 = Dog("Бобик", "Лабрадор", 5)

# Доступ к атрибутам
print(dog1.name)      # Рекс
print(dog2.breed)     # Лабрадор

# Вызов методов
dog1.bark()
dog2.info()

# Изменение атрибута
dog1.age = 4
dog1.info()


# ------------------------------------------------------------
# 3. МАГИЧЕСКИЕ МЕТОДЫ (__dunder__ methods)
# ------------------------------------------------------------
print("\n=== Магические методы ===")

class Book:
    def __init__(self, title, author, pages):
        self.title = title
        self.author = author
        self.pages = pages

    def __str__(self):
        # Вызывается при print(объект) или str(объект)
        return f'"{self.title}" — {self.author} ({self.pages} стр.)'

    def __repr__(self):
        # Для разработчиков — точное представление
        return f'Book("{self.title}", "{self.author}", {self.pages})'

    def __len__(self):
        return self.pages

    def __eq__(self, other):
        # Определяем что значит "равный"
        return self.title == other.title and self.author == other.author

    def __lt__(self, other):
        # Определяем оператор < (позволяет сортировать)
        return self.pages < other.pages

b1 = Book("Мастер и Маргарита", "Булгаков", 480)
b2 = Book("1984", "Оруэлл", 328)
b3 = Book("Мастер и Маргарита", "Булгаков", 480)

print(b1)           # вызывает __str__
print(repr(b2))     # вызывает __repr__
print(len(b1))      # 480 — вызывает __len__
print(b1 == b3)     # True
print(b1 == b2)     # False

books = [b1, b2, Book("Преступление и наказание", "Достоевский", 672)]
print(sorted(books))     # сортировка по страницам через __lt__


# ------------------------------------------------------------
# 4. АТРИБУТЫ КЛАССА vs ЭКЗЕМПЛЯРА
# ------------------------------------------------------------
print("\n=== Атрибуты класса ===")

class Employee:
    company = "Tech Corp"   # атрибут класса — общий для всех
    employee_count = 0      # счётчик объектов

    def __init__(self, name, salary):
        self.name = name          # атрибут экземпляра
        self.salary = salary
        Employee.employee_count += 1   # изменяем атрибут КЛАССА

    def describe(self):
        print(f"{self.name} | {Employee.company} | {self.salary}₽")

    @classmethod
    def get_count(cls):
        return f"Сотрудников: {cls.employee_count}"

    @staticmethod
    def is_valid_salary(amount):
        return amount > 0

emp1 = Employee("Анна", 80_000)
emp2 = Employee("Борис", 95_000)

emp1.describe()
emp2.describe()
print(Employee.get_count())     # @classmethod — первый аргумент cls (класс)
print(Employee.is_valid_salary(50_000))  # @staticmethod — нет self/cls


# ------------------------------------------------------------
# 5. ИНКАПСУЛЯЦИЯ — ограничение доступа
# ------------------------------------------------------------
print("\n=== Инкапсуляция ===")

class BankAccount:
    def __init__(self, owner, balance):
        self.owner = owner
        self.__balance = balance    # __двойное подчёркивание = приватный

    def deposit(self, amount):
        if amount > 0:
            self.__balance += amount
            print(f"Пополнение: +{amount}. Баланс: {self.__balance}")

    def withdraw(self, amount):
        if amount > self.__balance:
            print("Недостаточно средств!")
        elif amount > 0:
            self.__balance -= amount
            print(f"Снятие: -{amount}. Баланс: {self.__balance}")

    def get_balance(self):    # геттер — "контролируемый" доступ
        return self.__balance

    def __str__(self):
        return f"Счёт {self.owner}: {self.__balance}₽"

account = BankAccount("Алексей", 10_000)
account.deposit(5_000)
account.withdraw(3_000)
account.withdraw(50_000)    # Недостаточно средств
print(account.get_balance())
print(account)

# account.__balance  # AttributeError — приватный атрибут недоступен снаружи
# (технически можно через account._BankAccount__balance, но это нарушение)


# ------------------------------------------------------------
# 6. PROPERTY — питонский способ геттеров/сеттеров
# ------------------------------------------------------------
print("\n=== Property ===")

class Temperature:
    def __init__(self, celsius):
        self._celsius = celsius    # _одно подчёркивание = "защищённый" (соглашение)

    @property
    def celsius(self):             # геттер
        return self._celsius

    @celsius.setter
    def celsius(self, value):      # сеттер
        if value < -273.15:
            raise ValueError("Температура ниже абсолютного нуля!")
        self._celsius = value

    @property
    def fahrenheit(self):          # вычисляемое свойство (только чтение)
        return self._celsius * 9/5 + 32

t = Temperature(25)
print(t.celsius)       # 25 — через @property выглядит как атрибут
print(t.fahrenheit)    # 77.0
t.celsius = 100        # через @setter
print(t.fahrenheit)    # 212.0
# t.celsius = -300     # ValueError


# ============================================================
# ДОМАШНЕЕ ЗАДАНИЕ:
#
# 1. Создай класс Rectangle (прямоугольник) с атрибутами width и height.
#    Добавь методы:
#    - area() — площадь
#    - perimeter() — периметр
#    - is_square() — True если квадрат
#    - __str__ для красивого вывода
#    Создай несколько объектов и протестируй все методы.
#
# 2. Создай класс Student с атрибутами: name, grades (список оценок).
#    Добавь методы:
#    - add_grade(grade) — добавить оценку
#    - average() — средний балл
#    - best_grade() — лучшая оценка
#    - __str__
#    Используй @property для вычисления среднего балла.
#
# 3. Создай класс Counter с приватным атрибутом __count = 0.
#    Методы: increment(), decrement(), reset(), get_value().
#    Убедись, что __count нельзя изменить напрямую снаружи.
# ============================================================
