# ============================================================
# ЗАНЯТИЕ 13: ООП — Часть 2. Наследование и полиморфизм 
# ============================================================
# Темы:
#   1. Наследование
#   2. super()
#   3. Переопределение методов (override)
#   4. Полиморфизм
#   5. Абстрактные классы
#   6. Множественное наследование + MRO
#   7. Итог: принципы SOLID (кратко)
# ============================================================


# ------------------------------------------------------------
# 1. НАСЛЕДОВАНИЕ — класс "берёт" атрибуты и методы другого
# ------------------------------------------------------------
# Базовый (родительский) класс
print("=== Наследование ===")

class Animal:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def eat(self):
        print(f"{self.name} ест")

    def sleep(self):
        print(f"{self.name} спит")

    def __str__(self):
        return f"{self.__class__.__name__}({self.name}, {self.age} лет)"


# Дочерний класс — наследует от Animal
class Dog(Animal):
    def __init__(self, name, age, breed):
        super().__init__(name, age)    # вызов конструктора родителя
        self.breed = breed

    def bark(self):
        print(f"{self.name}: Гав!")

    def __str__(self):
        return f"Dog({self.name}, {self.breed}, {self.age} лет)"


class Cat(Animal):
    def __init__(self, name, age, indoor=True):
        super().__init__(name, age)
        self.indoor = indoor

    def meow(self):
        print(f"{self.name}: Мяу!")


# Дочерний наследует методы родителя
dog = Dog("Рекс", 3, "Овчарка")
dog.eat()        # унаследовано от Animal
dog.sleep()      # унаследовано от Animal
dog.bark()       # собственный метод

cat = Cat("Мурка", 5)
cat.eat()
cat.meow()

print(dog)
print(cat)       # __str__ из Animal — self.__class__.__name__ = "Cat"


# ------------------------------------------------------------
# 2. ISINSTANCE И ISSUBCLASS
# ------------------------------------------------------------
print("\n=== isinstance / issubclass ===")

print(isinstance(dog, Dog))     # True
print(isinstance(dog, Animal))  # True — Dog наследует Animal!
print(isinstance(cat, Dog))     # False

print(issubclass(Dog, Animal))  # True
print(issubclass(Cat, Animal))  # True
print(issubclass(Dog, Cat))     # False


# ------------------------------------------------------------
# 3. ПЕРЕОПРЕДЕЛЕНИЕ МЕТОДОВ (OVERRIDE)
# ------------------------------------------------------------
print("\n=== Override ===")

class Animal2:
    def speak(self):
        print("Животное издаёт звук")

class Dog2(Animal2):
    def speak(self):                    # переопределяем метод
        print("Гав!")

class Cat2(Animal2):
    def speak(self):
        print("Мяу!")

class Fish(Animal2):
    pass                                # НЕ переопределяем — используем родительский

animals = [Dog2(), Cat2(), Fish(), Dog2()]

for animal in animals:
    animal.speak()   # каждый говорит по-своему — это ПОЛИМОРФИЗМ!


# ------------------------------------------------------------
# 4. ПОЛИМОРФИЗМ — один интерфейс, разное поведение
# ------------------------------------------------------------
print("\n=== Полиморфизм ===")

class Shape:
    def area(self):
        raise NotImplementedError("Подкласс должен реализовать area()")

    def perimeter(self):
        raise NotImplementedError

    def describe(self):
        print(f"{self.__class__.__name__}: площадь={self.area():.2f}, периметр={self.perimeter():.2f}")


import math as m

class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius

    def area(self):
        return m.pi * self.radius ** 2

    def perimeter(self):
        return 2 * m.pi * self.radius


class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height

    def perimeter(self):
        return 2 * (self.width + self.height)


class Triangle(Shape):
    def __init__(self, a, b, c):
        self.a, self.b, self.c = a, b, c

    def area(self):
        s = self.perimeter() / 2        # полупериметр
        return (s * (s-self.a) * (s-self.b) * (s-self.c)) ** 0.5

    def perimeter(self):
        return self.a + self.b + self.c


shapes = [Circle(5), Rectangle(4, 6), Triangle(3, 4, 5)]

for shape in shapes:
    shape.describe()    # один вызов — разная реализация

# Общая площадь всех фигур — полиморфизм в действии
total = sum(shape.area() for shape in shapes)
print(f"Общая площадь: {total:.2f}")


# ------------------------------------------------------------
# 5. АБСТРАКТНЫЕ КЛАССЫ — нельзя создать экземпляр напрямую
# ------------------------------------------------------------
from abc import ABC, abstractmethod

print("\n=== Абстрактные классы ===")

class Vehicle(ABC):
    def __init__(self, brand, speed):
        self.brand = brand
        self.speed = speed

    @abstractmethod
    def move(self):
        """Каждый транспорт движется по-своему."""
        pass

    @abstractmethod
    def fuel_type(self):
        pass

    def info(self):                    # обычный метод — наследуется как есть
        print(f"{self.brand}: {self.speed} км/ч, топливо: {self.fuel_type()}")


class Car(Vehicle):
    def move(self):
        print(f"{self.brand} едет по дороге")

    def fuel_type(self):
        return "бензин"


class Boat(Vehicle):
    def move(self):
        print(f"{self.brand} плывёт по воде")

    def fuel_type(self):
        return "дизель"


class Bicycle(Vehicle):
    def move(self):
        print(f"{self.brand} едет (педали)")

    def fuel_type(self):
        return "мышечная сила"


# vehicle = Vehicle("X", 100)  # TypeError — нельзя создать абстрактный!

vehicles = [Car("Toyota", 200), Boat("Yamaha", 60), Bicycle("Trek", 30)]
for v in vehicles:
    v.move()
    v.info()


# ------------------------------------------------------------
# 6. МНОЖЕСТВЕННОЕ НАСЛЕДОВАНИЕ + MRO
# ------------------------------------------------------------
print("\n=== Множественное наследование ===")

class Flyable:
    def move(self):
        return "летит"

class Swimmable:
    def move(self):
        return "плывёт"

class Duck(Flyable, Swimmable):    # наследует оба
    def move(self):
        return f"утка: {Flyable.move(self)} и {Swimmable.move(self)}"

duck = Duck()
print(duck.move())

# MRO (Method Resolution Order) — порядок поиска методов
print(Duck.__mro__)    # [Duck, Flyable, Swimmable, object]


# ------------------------------------------------------------
# 7. ИТОГОВЫЙ ПРИМЕР — Система сотрудников
# ------------------------------------------------------------
print("\n=== Итоговый пример ===")

class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def __str__(self):
        return f"{self.name} ({self.age} лет)"


class Employee(Person):
    def __init__(self, name, age, department, base_salary):
        super().__init__(name, age)
        self.department = department
        self._base_salary = base_salary

    @property
    def salary(self):
        return self._base_salary

    def work(self):
        print(f"{self.name} работает в отделе {self.department}")

    def __str__(self):
        return f"{super().__str__()} | {self.department} | {self.salary}₽"


class Manager(Employee):
    def __init__(self, name, age, department, base_salary, team_size):
        super().__init__(name, age, department, base_salary)
        self.team_size = team_size

    @property
    def salary(self):                            # переопределяем зарплату
        return self._base_salary + self.team_size * 5_000

    def hold_meeting(self):
        print(f"{self.name} проводит митинг с {self.team_size} сотрудниками")


class Developer(Employee):
    def __init__(self, name, age, base_salary, languages):
        super().__init__(name, age, "Разработка", base_salary)
        self.languages = languages

    def code(self):
        print(f"{self.name} пишет код на {', '.join(self.languages)}")


staff = [
    Manager("Алексей", 35, "Менеджмент", 100_000, 5),
    Developer("Борис", 28, 120_000, ["Python", "SQL"]),
    Developer("Вера", 25, 110_000, ["Python", "JavaScript"]),
]

for person in staff:
    print(person)
    person.work()

print("\nФОНД ЗАРПЛАТЫ:")
total = sum(e.salary for e in staff)
print(f"Итого: {total:,}₽")


# ============================================================
# ДОМАШНЕЕ ЗАДАНИЕ (итоговое):
#
# Создай систему "Зоопарк".
#
# 1. Абстрактный класс Animal (ABC):
#    - __init__(name, age, weight)
#    - @abstractmethod sound() — звук животного
#    - @abstractmethod diet() — "травоядное" / "хищник" / "всеядное"
#    - feed() — выводит "Кормим [name]: [diet()]"
#    - __str__
#
# 2. Классы: Lion, Elephant, Parrot — наследуют Animal
#    - Реализуй sound() и diet() для каждого
#    - Добавь уникальный метод для каждого:
#      Lion.hunt(), Elephant.trumpet(), Parrot.repeat(phrase)
#
# 3. Класс Zoo:
#    - animals = [] (список животных)
#    - add_animal(animal)
#    - feed_all() — кормит всех
#    - show_all() — выводит всех животных
#    - find_by_diet(diet_type) — возвращает список животных с таким питанием
#
# 4. Создай зоопарк, добавь минимум 5 животных,
#    покорми всех, найди всех хищников.
# ============================================================
