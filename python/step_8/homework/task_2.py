# ============================================================
# ЗАНЯТИЕ 8 | ЗАДАЧА 2
# Тема: Параметры по умолчанию и именованные аргументы
# ============================================================
#
# Задание 1.
#   Напиши функцию greet(name, greeting="Привет", punctuation="!"),
#   которая выводит: "Привет, Алексей!"
#   Протестируй все комбинации:
#   - greet("Алексей")
#   - greet("Мария", greeting="Здравствуйте")
#   - greet("Иван", punctuation=".")
#   - greet("Ольга", greeting="Добрый день", punctuation="!")
#
# Задание 2.
#   Напиши функцию create_email(username, domain="gmail.com", tld=None),
#   которая собирает email-адрес.
#   Если tld передан — добавляй его: user@domain.tld
#   Иначе: user@domain
#   Примеры:
#   create_email("alex")              → "alex@gmail.com"
#   create_email("ivan", "mail.ru")   → "ivan@mail.ru"
#   create_email("bot", "company", "org") → "bot@company.org"
# ============================================================
