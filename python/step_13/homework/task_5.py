# ============================================================
# ЗАНЯТИЕ 13 | ЗАДАЧА 5 (итоговая)
# Тема: Полный проект — Система управления сотрудниками
# ============================================================
#
# Реализуй мини-систему HR с использованием всех концепций ООП.
#
# Абстрактный класс Employee(ABC):
#   - __init__(name, age, department)
#   - @abstractmethod calculate_salary() → float
#   - @abstractmethod get_role()          → str
#   - Обычный: display()  — выводит полную информацию
#   - @property name, age (с валидацией через сеттеры)
#
# Классы сотрудников:
#
#   FullTimeEmployee(Employee):
#     - monthly_salary (фиксированная)
#     - calculate_salary() → monthly_salary
#     - get_role() → "Штатный сотрудник"
#
#   PartTimeEmployee(Employee):
#     - hourly_rate, hours_per_month
#     - calculate_salary() → hourly_rate * hours_per_month
#     - get_role() → "Сотрудник на полставки"
#
#   Contractor(Employee):
#     - project_fee, num_projects
#     - calculate_salary() → project_fee * num_projects
#     - get_role() → "Подрядчик"
#
#   Manager(FullTimeEmployee):
#     - bonus_percent (% надбавки к окладу)
#     - team = [] (список подчинённых Employee)
#     - calculate_salary() → monthly_salary * (1 + bonus_percent/100)
#     - get_role() → "Менеджер"
#     - add_to_team(employee)
#     - team_salary_total() → сумма зарплат всей команды включая себя
#
# Класс Company:
#   - __init__(name)
#   - Приватный __employees = []
#   - hire(employee)
#   - fire(name)  — удалить по имени, Exception если нет
#   - payroll()   — выводит всех сотрудников и их зарплаты + итог
#   - get_by_department(dept) → список
#   - highest_paid() → сотрудник с максимальной зарплатой
#   - __len__, __str__
#
# Создай компанию с 6+ сотрудниками разных типов.
# Назначь менеджера с командой из 3 человек.
# Выведи полный расчётный лист (payroll).
# Найди самого высокооплачиваемого.
# Уволь одного сотрудника и снова выведи payroll.
# ============================================================
