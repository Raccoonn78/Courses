# Подготовка к собеседованию: Python TeamLead

Гайд построен на твоём реальном контексте: DDD-проект, задача «новая очередь RabbitMQ для заметок из 1С» (контракт взят из твоих файлов `1c-usk_to_copilot-medkc_notes-changes*.json`).

---

# Часть 1. DDD без магии

## 1.1. Главная идея — правило зависимостей

Весь DDD/Clean Architecture сводится к одному правилу:

**Все зависимости направлены внутрь, к домену. Домен не знает ни о ком.**

```
┌─────────────────────────────────────────────┐
│  presentation / api  (FastAPI, consumers)   │
│  ┌───────────────────────────────────────┐  │
│  │  application  (use cases, handlers)   │  │
│  │  ┌─────────────────────────────────┐  │  │
│  │  │  domain  (сущности, правила)    │  │  │
│  │  └─────────────────────────────────┘  │  │
│  └───────────────────────────────────────┘  │
│  infrastructure (Postgres, Rabbit, HTTP) ───┼──► реализует интерфейсы,
└─────────────────────────────────────────────┘    объявленные внутри
```

Проверка на собеседовании простая: открой любой файл в `domain/` — там не должно быть **ни одного импорта** из `sqlalchemy`, `aio_pika`, `fastapi`, `requests`. Только stdlib, typing и другие модули домена. Если есть — это уже не домен.

Зачем это нужно (ответ для интервьюера): домен — самая дорогая и самая стабильная часть системы. Базу можно сменить с Postgres на Mongo, Rabbit на Kafka — бизнес-правила при этом не трогаются и тесты на них не переписываются. Домен тестируется без единого мока инфраструктуры.

## 1.2. Из чего состоит слой domain — по какому принципу папки

Папки внутри `domain/` режутся **по бизнес-подобластям (bounded context / агрегатам), а не по типам классов**. Плохо: `domain/entities/`, `domain/services/` со свалкой всего подряд. Хорошо — по смыслу:

```
src/
├── domain/
│   ├── notes/                    # агрегат «Заметки по договору»
│   │   ├── entities.py           # Note, NotesCollection
│   │   ├── value_objects.py      # NoteType, ObjectRef
│   │   ├── events.py             # NotesSynchronized
│   │   ├── exceptions.py         # NoteValidationError
│   │   ├── repository.py         # ИНТЕРФЕЙС INotesRepository (Protocol/ABC)
│   │   └── services.py           # доменные сервисы (если нужны)
│   ├── contracts/                # агрегат «Договор ДМС»
│   │   └── ...
│   └── shared/                   # общие VO: Money, Period, EntityId
├── application/
│   ├── notes/
│   │   ├── commands.py           # DTO: SyncNotesCommand
│   │   ├── handlers.py           # SyncNotesHandler (use case)
│   │   └── interfaces.py         # IUnitOfWork, IMessageDeduplicator
│   └── ...
├── infrastructure/
│   ├── db/
│   │   ├── models.py             # SQLAlchemy-модели (≠ доменные сущности!)
│   │   ├── repositories.py       # PostgresNotesRepository(INotesRepository)
│   │   └── uow.py
│   ├── rabbit/
│   │   ├── consumer.py
│   │   ├── schemas.py            # Pydantic-схемы сообщений (анти-коррупционный слой)
│   │   └── mappers.py            # JSON 1С → доменные объекты
│   └── config.py
└── presentation/                 # FastAPI-роуты, CLI, точки входа
```

## 1.3. Как разбивать классы: Entity vs Value Object vs Aggregate

Три вопроса, которые нужно задавать про любой класс:

**1. Есть ли у объекта идентичность, живущая во времени?**
Да → **Entity**. Заметка с `objectId` из 1С — сущность: её содержимое меняется, но это «та же самая» заметка. Сравниваются entity по id.

**2. Объект определяется только своими значениями?**
Да → **Value Object**. Тип заметки, денежная сумма, период. Иммутабельны, сравниваются по значению, валидируют себя при создании (`frozen dataclass`):

```python
# domain/notes/value_objects.py
from dataclasses import dataclass
from enum import Enum

class NoteType(str, Enum):
    DMS_CONTRACT_INFO = "ИнформацияПоДоговоруДМС"

@dataclass(frozen=True, slots=True)
class NoteContent:
    text: str

    def __post_init__(self) -> None:
        if not self.text.strip():
            raise NoteValidationError("Текст заметки пуст")
        if len(self.text) > 10_000:
            raise NoteValidationError("Текст заметки слишком длинный")
```

**3. Какие объекты меняются только вместе, одной транзакцией?**
Это граница **Aggregate**. Aggregate root — единственная точка входа: снаружи нельзя менять внутренние объекты агрегата напрямую, только через методы корня. У тебя агрегат — «набор заметок документа»: сообщение из 1С приносит полный `recordSet` для одного `objectId`, и заменять его надо атомарно:

```python
# domain/notes/entities.py
from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

@dataclass
class Note:
    row_number: int
    content: NoteContent
    note_type: NoteType
    author_id: UUID
    created_at: datetime
    active: bool

@dataclass
class DocumentNotes:
    """Aggregate root: все заметки одного документа 1С."""
    object_id: UUID              # identity агрегата
    notes: list[Note] = field(default_factory=list)

    def replace_all(self, notes: list[Note]) -> None:
        """1С присылает полный снапшот — заменяем целиком, не мержим."""
        seen = set()
        for note in notes:
            if note.row_number in seen:
                raise NoteValidationError(
                    f"Дубликат rowNumber={note.row_number}"
                )
            seen.add(note.row_number)
        self.notes = sorted(notes, key=lambda n: n.row_number)

    @property
    def active_notes(self) -> list[Note]:
        return [n for n in self.notes if n.active]
```

**Репозиторий**: интерфейс живёт в домене (домен диктует, что ему нужно), реализация — в инфраструктуре:

```python
# domain/notes/repository.py
from typing import Protocol
from uuid import UUID

class INotesRepository(Protocol):
    async def get(self, object_id: UUID) -> DocumentNotes | None: ...
    async def save(self, aggregate: DocumentNotes) -> None: ...
```

```python
# infrastructure/db/repositories.py — а вот тут уже можно SQLAlchemy
class PostgresNotesRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get(self, object_id: UUID) -> DocumentNotes | None:
        ...  # ORM-модель → доменная сущность (маппинг!)

    async def save(self, aggregate: DocumentNotes) -> None:
        ...  # доменная сущность → ORM-модель
```

Важный нюанс, о котором любят спрашивать: **ORM-модель ≠ доменная сущность**. SQLAlchemy-модель — деталь хранения, доменная сущность — бизнес-объект. На маленьких проектах их сливают в один класс (и это осознанный трейд-офф, так и говори), в «честном» DDD — маппят туда-обратно в репозитории.

## 1.4. Откуда какая зависимость — шпаргалка

| Слой | Может импортировать | Не может |
|---|---|---|
| `domain` | stdlib, свои модули домена | всё остальное |
| `application` | `domain`, свои интерфейсы | инфраструктуру, фреймворки |
| `infrastructure` | `domain`, `application` (реализует их интерфейсы) | `presentation` |
| `presentation` | `application` (вызывает handlers), DI-контейнер | напрямую БД/домен в обход application |

Механизм, который это склеивает — **Dependency Inversion (буква D в SOLID)**: application объявляет `Protocol`/ABC, инфраструктура реализует, а конкретный экземпляр подставляется снаружи через DI (конструктор, `dishka`, `punq`, ручная сборка в `main.py`). Handler никогда сам не делает `PostgresNotesRepository()` — он получает `INotesRepository` в конструктор.

---

# Часть 2. Задача «новая очередь RabbitMQ» — с чего начать и как вести код

Разбор на твоём реальном контракте. Из файлов видно:

- очередь/топик: `1c-usk_to_copilot-medkc_notes-changes` — 1С шлёт изменения заметок;
- **data-сообщение** (`notes-changes`): `recordSet` — полный набор заметок для документа `objectId`;
- **контрольное сообщение** (`notes-changes-final`): приходит после батча, несёт `countMessages`/`countRows` — сверка, что всё дошло;
- сквозные поля: `cid` (correlation id батча), `message-id` (идемпотентность), `keyValue == objectId`.

## Шаг 0. Вопросы, которые тимлид задаёт ДО кода

Это то, что отличает сеньора/лида на собеседовании — сначала уточнить контракт и гарантии:

1. **Семантика доставки**: at-least-once (значит, будут дубли → нужна идемпотентность) или exactly-once (в Rabbit её нет, значит at-least-once)?
2. **Порядок**: важен ли порядок сообщений? Здесь — снапшоты по `objectId`, значит важен порядок в рамках одного объекта; решается либо одной очередью с prefetch, либо ключом партиционирования.
3. **Что делать с «ядовитым» сообщением** (невалидный JSON, бесконечно падающая обработка)? → DLQ + лимит retry.
4. **Что означает `final`-сообщение** и что делать при расхождении счётчиков? Алерт? Перезапрос?
5. **Идемпотентность**: по `message-id` (дедупликация) или по природе операции (replace-снапшот по `objectId` идемпотентен сам по себе — это твой случай, и это сильный ответ).
6. Нагрузка, размер сообщений, SLA на лаг обработки.

## Шаг 1. Contract first: зафиксировать схемы сообщений

Первый код, который ты пишешь — не consumer, а **схемы**. Это анти-коррупционный слой: уродливый формат 1С (русские enum-значения, timestamp вида `63918500167254` — это секунды от года 0001, кстати) не должен протечь в домен.

```python
# infrastructure/rabbit/schemas.py
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field

class NoteTypePayload(BaseModel):
    type: str
    representation: str
    value: str                       # "ИнформацияПоДоговоруДМС"

class NoteRecordPayload(BaseModel):
    content: str
    active: bool
    type: NoteTypePayload
    author_id: UUID = Field(alias="authorId")
    object_id: UUID = Field(alias="objectId")
    date: datetime
    row_number: int = Field(alias="rowNumber")

class NotesChangesPayload(BaseModel):
    key_type: str = Field(alias="keyType")        # "DocumentRef.ДСП"
    key_value: UUID = Field(alias="keyValue")
    record_set: list[NoteRecordPayload] = Field(alias="recordSet")
    cid: UUID

class NotesChangesFinalPayload(BaseModel):
    count_messages: int = Field(alias="countMessages")
    count_rows: int = Field(alias="countRows")
    key_value: UUID = Field(alias="keyValue")
    cid: UUID
```

Почему сначала это: схема — исполняемая документация контракта, на неё сразу пишутся тесты с реальными JSON из твоих файлов, и она отсекает мусор на входе.

## Шаг 2. Домен

Сущности `Note`, `DocumentNotes` из части 1 — они уже написаны. Заметь порядок: мы движемся **изнутри наружу** (domain → application → infrastructure), потому что внутренние слои ни от чего не зависят и их можно писать и тестировать сразу.

## Шаг 3. Application: use case

```python
# application/notes/commands.py
from dataclasses import dataclass
from uuid import UUID

@dataclass(frozen=True)
class SyncNotesCommand:
    object_id: UUID
    notes: list[NoteDTO]          # плоские DTO, не Pydantic и не домен
    cid: UUID
    message_id: UUID
```

```python
# application/notes/handlers.py
class SyncNotesHandler:
    def __init__(self, uow: IUnitOfWork) -> None:
        self._uow = uow

    async def handle(self, cmd: SyncNotesCommand) -> None:
        async with self._uow:
            aggregate = (
                await self._uow.notes.get(cmd.object_id)
                or DocumentNotes(object_id=cmd.object_id)
            )
            aggregate.replace_all([self._to_entity(n) for n in cmd.notes])
            await self._uow.notes.save(aggregate)
            await self._uow.commit()
```

Handler тонкий: достал агрегат → вызвал доменный метод → сохранил. Вся бизнес-логика — в `replace_all`, в домене. Если handler начинает толстеть if-ами про бизнес — логика утекла не туда, это классическое замечание на код-ревью.

## Шаг 4. Инфраструктура: consumer

```python
# infrastructure/rabbit/consumer.py
import aio_pika
from pydantic import ValidationError

MAX_RETRIES = 3

class NotesChangesConsumer:
    def __init__(self, handler: SyncNotesHandler, settings: RabbitSettings):
        self._handler = handler
        self._settings = settings

    async def start(self) -> None:
        connection = await aio_pika.connect_robust(self._settings.url)
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=10)

        # Топология: очередь + DLQ
        dlx = await channel.declare_exchange("dlx", type="direct", durable=True)
        dlq = await channel.declare_queue(
            "1c-usk_to_copilot-medkc_notes-changes.dlq", durable=True
        )
        await dlq.bind(dlx, routing_key="notes-changes")

        queue = await channel.declare_queue(
            "1c-usk_to_copilot-medkc_notes-changes",
            durable=True,
            arguments={
                "x-dead-letter-exchange": "dlx",
                "x-dead-letter-routing-key": "notes-changes",
            },
        )
        await queue.consume(self._on_message)

    async def _on_message(self, message: aio_pika.IncomingMessage) -> None:
        try:
            payload = NotesChangesPayload.model_validate_json(message.body)
        except ValidationError:
            logger.exception("Invalid message, sending to DLQ",
                             extra={"message_id": message.message_id})
            await message.reject(requeue=False)   # сразу в DLQ, retry бессмысленен
            return

        try:
            await self._handler.handle(to_command(payload, message))
        except Exception:
            logger.exception("Processing failed",
                             extra={"cid": str(payload.cid)})
            if _retry_count(message) >= MAX_RETRIES:
                await message.reject(requeue=False)   # в DLQ
            else:
                await message.nack(requeue=True)
            return

        await message.ack()   # ack ТОЛЬКО после успешной обработки
```

Ключевые решения, которые нужно уметь проговорить:

1. **ack после обработки, не до** — иначе при падении сервиса сообщение теряется.
2. **Два типа ошибок — две стратегии**: невалидное сообщение → сразу DLQ (retry не поможет); транзиентная ошибка (БД отвалилась) → nack с requeue и лимитом попыток.
3. **prefetch_count** — backpressure: не набирать 10 000 сообщений в память.
4. **connect_robust** — авто-реконнект.
5. **Идемпотентность бесплатно**: обработчик делает replace-снапшот по `objectId`, повторная доставка того же сообщения даёт тот же результат. Это и есть правильный ответ на «а что с дублями при at-least-once».
6. `final`-сообщение — отдельный маленький handler: сверить счётчики за `cid`, при расхождении — метрика + алерт.

## Шаг 5. Тесты (см. часть 3.4 — там разобрано как их писать)

Пирамида для этой задачи:
- **unit на домен**: `replace_all` — дубликаты rowNumber, сортировка, пустой набор. Без моков вообще.
- **unit на handler**: с in-memory fake-репозиторием (не MagicMock! fake честнее и читабельнее).
- **unit на схемы**: скормить реальные JSON из твоих файлов — они становятся фикстурами.
- **интеграционный на consumer**: testcontainers с реальным Rabbit — publish → assert записи в БД, отдельный тест на попадание мусора в DLQ.

## Шаг 6. Порядок работы над задачей целиком (как «вести код»)

1. Уточнил контракт и гарантии (шаг 0) — 30 минут разговора экономят дни.
2. Схемы + тесты на схемы с реальными примерами сообщений.
3. Домен + unit-тесты.
4. Handler + тесты на fake.
5. Consumer + топология очередей (durable, DLQ).
6. Wiring: DI, конфиг, healthcheck, graceful shutdown (дообработать текущее сообщение при SIGTERM).
7. Наблюдаемость: лог с `cid`/`message_id` в каждой записи, метрики (lag очереди, rate ошибок, размер DLQ).
8. Интеграционный тест, PR небольшими коммитами по слоям.

Каждый пункт — отдельный логичный коммит; ревьюеру видна структура мысли.

---

# Часть 3. Live coding: практические примеры «найди ошибки → исправь → напиши тесты»

Прорешай каждый пример руками: сначала сам ищи ошибки, потом сверяйся с разбором.

## 3.1. Пример «код-ревью consumer'а» (почти наверняка дадут что-то такое)

**Задание: этот код работает на проде. Найдите проблемы.**

```python
import json
import pika

connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
channel = connection.channel()

processed = []

def process(ch, method, properties, body, cache={}):
    ch.basic_ack(delivery_tag=method.delivery_tag)
    try:
        data = json.loads(body)
        if data["keyValue"] in cache:
            return
        cache[data["keyValue"]] = True
        for rec in data["recordSet"]:
            save_note(rec["objectId"], rec["content"], rec.get("active"))
        processed.append(data["keyValue"])
    except Exception:
        pass

channel.basic_consume(queue="notes-changes", on_message_callback=process)
channel.start_consuming()
```

<details><summary><b>Разбор (сначала найди сам — тут минимум 8 проблем)</b></summary>

1. **ack до обработки** — упали на `save_note` → сообщение потеряно навсегда. Ack переносится в конец, в except — nack/reject.
2. **`except Exception: pass`** — глотание всех ошибок без лога. Молчаливая потеря данных, невозможно дебажить.
3. **Мутабельный аргумент по умолчанию `cache={}`** — классика Python: словарь создаётся один раз и живёт вечно → безлимитный рост памяти. И заодно это неверная дедупликация: `keyValue` легитимно повторяется (новый снапшот того же документа!) — кэшировать надо `message_id`, и не в памяти процесса (рестарт/несколько инстансов), а в Redis/БД с TTL. А лучше — сделать обработку идемпотентной и не дедуплицировать вовсе.
4. **Глобальное мутабельное состояние** `processed` — растёт бесконечно, непригодно при нескольких инстансах.
5. **Нет валидации** — `data["keyValue"]` упадёт KeyError на мусорном сообщении; нужна схема (Pydantic) и маршрут невалидного в DLQ.
6. **Нет prefetch (`basic_qos`)** — Rabbit вывалит в consumer всё содержимое очереди.
7. **Частичная запись без транзакции** — упали на 3-й заметке из 5: две записаны, состояние неконсистентно, а после ack-до-обработки ещё и без шанса на повтор. Нужен UoW/транзакция на весь recordSet.
8. **Нет durable/DLQ/reconnect**, соединение не закрывается, нет graceful shutdown.
9. **`rec.get("active")`** вернёт `None` вместо ошибки — тихая порча данных; поле обязательное.
10. Синхронный `BlockingConnection` — ок сам по себе, но в проекте на asyncio это заблокирует event loop; либо aio_pika, либо отдельный процесс.

Исправленная версия — по сути consumer из части 2, шаг 4.
</details>

## 3.2. Классические Python-ловушки (быстрые вопросы разминки)

**А. Что напечатает и почему?**

```python
def add_item(item, items=[]):
    items.append(item)
    return items

print(add_item(1))
print(add_item(2))
```

Ответ: `[1]`, затем `[1, 2]`. Default вычисляется один раз при определении функции. Фикс: `items: list | None = None` + `items = items or []` внутри (аккуратно: `or` подменит и переданный пустой список — строже `if items is None`).

**Б. Замыкания в цикле:**

```python
funcs = [lambda: i for i in range(3)]
print([f() for f in funcs])   # ?
```

Ответ: `[2, 2, 2]` — замыкание захватывает переменную, не значение. Фикс: `lambda i=i: i`.

**В. Race condition, которого «не может быть из-за GIL»:**

```python
counter = 0
def worker():
    global counter
    for _ in range(100_000):
        counter += 1   # НЕ атомарно: LOAD, ADD, STORE
```

`counter += 1` — три байткод-операции, GIL может переключить поток между ними. Итог < 200 000 при двух потоках (на 3.10+ воспроизводится реже из-за изменений в переключении, но гарантий нет). Фикс: `threading.Lock`. Заодно расскажи: GIL защищает интерпретатор, а не твои инварианты; в 3.13+ есть free-threaded сборка — тем более нужны локи.

**Г. `is` vs `==`, кэш маленьких int:**

```python
a = 256; b = 256; a is b   # True
a = 257; b = 257; a is b   # False (в скрипте; в REPL может быть True)
```

`is` — сравнение идентичности, для чисел/строк использовать нельзя, только для `None`/синглтонов.

**Д. Изменение списка во время итерации:**

```python
nums = [1, 2, 3, 4]
for n in nums:
    if n % 2 == 0:
        nums.remove(n)   # пропустит элементы
```

Фикс: итерироваться по копии или собрать новый список comprehension'ом.

## 3.3. Async-ловушки (для проекта на aio_pika/FastAPI — спросят точно)

**А. Блокирующий вызов в корутине:**

```python
async def handler(cmd):
    data = requests.get(url)          # БЛОКИРУЕТ весь event loop
    time.sleep(1)                     # тоже
```

Весь сервис (включая consumer!) встаёт. Фикс: `httpx.AsyncClient`, `asyncio.sleep`; для неизбежного sync-кода — `await asyncio.to_thread(func)`.

**Б. Забытый await / фоновая задача без ссылки:**

```python
async def on_message(msg):
    asyncio.create_task(process(msg))   # 1) исключения потеряются
    await msg.ack()                     # 2) ack ДО обработки — потеря данных
```

Плюс тонкость: на task без сохранённой ссылки может сработать GC. Держать реестр задач, `add_done_callback` для логирования исключений, ну и ack после.

**В. Последовательные await там, где нужен параллелизм:**

```python
a = await fetch_a()      # 1 сек
b = await fetch_b()      # 1 сек   → всего 2 сек
# vs
a, b = await asyncio.gather(fetch_a(), fetch_b())   # 1 сек
```

И следом уточнение интервьюера: чем `gather` опасен? По умолчанию при исключении в одной задаче остальные продолжают висеть; обсуди `return_exceptions=True` и `asyncio.TaskGroup` (3.11+) со structured concurrency.

**Г. Одна `AsyncSession` SQLAlchemy на несколько конкурентных задач** — session не потокобезопасна и не task-безопасна: session-per-request/per-message через DI.

## 3.4. «Напишите тесты» — эталонная структура ответа

Дают функцию/класс — например, наш `DocumentNotes.replace_all` и `SyncNotesHandler`. Как отвечать.

**1. Сначала проговори стратегию** (это оценивается выше самих тестов): что тестируем как unit, где границы, что мокаем (ничего лишнего), какие классы эквивалентности и граничные случаи.

**2. Unit на домен — без моков:**

```python
import pytest
from datetime import datetime, timezone
from uuid import uuid4

def make_note(row: int, active: bool = True) -> Note:
    return Note(
        row_number=row,
        content=NoteContent("текст"),
        note_type=NoteType.DMS_CONTRACT_INFO,
        author_id=uuid4(),
        created_at=datetime.now(timezone.utc),
        active=active,
    )

class TestDocumentNotesReplaceAll:
    def test_replaces_previous_snapshot_entirely(self):
        agg = DocumentNotes(object_id=uuid4())
        agg.replace_all([make_note(1), make_note(2)])
        agg.replace_all([make_note(1)])          # новый снапшот
        assert len(agg.notes) == 1               # старьё не мержится

    def test_sorts_by_row_number(self):
        agg = DocumentNotes(object_id=uuid4())
        agg.replace_all([make_note(3), make_note(1), make_note(2)])
        assert [n.row_number for n in agg.notes] == [1, 2, 3]

    def test_rejects_duplicate_row_numbers(self):
        agg = DocumentNotes(object_id=uuid4())
        with pytest.raises(NoteValidationError, match="Дубликат"):
            agg.replace_all([make_note(1), make_note(1)])

    def test_empty_snapshot_clears_notes(self):        # граничный случай!
        agg = DocumentNotes(object_id=uuid4())
        agg.replace_all([make_note(1)])
        agg.replace_all([])
        assert agg.notes == []

    def test_active_notes_filters_inactive(self):
        agg = DocumentNotes(object_id=uuid4())
        agg.replace_all([make_note(1, active=True), make_note(2, active=False)])
        assert [n.row_number for n in agg.active_notes] == [1]
```

Что здесь демонстрируешь: фабрика тест-данных вместо копипасты, имена тестов = спецификация поведения, `pytest.raises(..., match=...)`, отдельный тест на пустой ввод, паттерн AAA (arrange-act-assert).

**3. Unit на handler — с fake, а не MagicMock:**

```python
class FakeNotesRepository:
    def __init__(self) -> None:
        self.storage: dict[UUID, DocumentNotes] = {}

    async def get(self, object_id):
        return self.storage.get(object_id)

    async def save(self, aggregate):
        self.storage[aggregate.object_id] = aggregate


@pytest.mark.asyncio
async def test_sync_creates_aggregate_when_absent():
    uow = FakeUnitOfWork()                     # fake поверх FakeNotesRepository
    handler = SyncNotesHandler(uow)
    oid = uuid4()

    await handler.handle(SyncNotesCommand(
        object_id=oid, notes=[make_note_dto(1)], cid=uuid4(), message_id=uuid4(),
    ))

    assert oid in uow.notes.storage
    assert uow.committed is True


@pytest.mark.asyncio
async def test_idempotent_on_redelivery():
    """Ключевой тест для at-least-once: дубль сообщения не ломает состояние."""
    uow = FakeUnitOfWork()
    handler = SyncNotesHandler(uow)
    cmd = SyncNotesCommand(object_id=uuid4(), notes=[make_note_dto(1)],
                           cid=uuid4(), message_id=uuid4())
    await handler.handle(cmd)
    await handler.handle(cmd)                  # повторная доставка

    assert len(uow.notes.storage[cmd.object_id].notes) == 1
```

Проговори, почему fake, а не `MagicMock`: mock проверяет «вызвали ли метод» (тест реализации, хрупкий), fake проверяет итоговое состояние (тест поведения). Mock оставляем для внешних side-effect'ов, которые нечем заменить.

**4. Тест схем на реальных сообщениях** — твои JSON-файлы кладутся в `tests/fixtures/` и парсятся в тесте: контракт зафиксирован исполняемо.

**5. Интеграционный (опиши словами, если нет времени писать):** testcontainers поднимает Rabbit+Postgres, publish реального сообщения → poll БД → assert; второй тест — мусорный JSON → assert, что он оказался в DLQ и очередь не заблокирована.

## 3.5. Задача на рефакторинг (типовой формат «что не так и как улучшить»)

```python
class NoteService:
    def process_note(self, note_data):
        conn = psycopg2.connect("dbname=notes user=admin password=admin123")
        cur = conn.cursor()
        if note_data["type"] == "dms":
            if note_data.get("active") == True:
                if len(note_data["content"]) > 0:
                    cur.execute("INSERT INTO notes VALUES ('%s', '%s')" %
                                (note_data["objectId"], note_data["content"]))
                    conn.commit()
                    requests.post("http://notifier/send",
                                  json={"text": "new note"})
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False
```

<details><summary><b>Разбор</b></summary>

Безопасность и корректность:
1. **SQL-инъекция** — форматирование строки вместо параметризованного запроса. Самое важное, называть первым.
2. **Пароль в коде** — секреты только из env/vault.
3. Соединение не закрывается (нет context manager), создаётся на каждый вызов — нужен пул.
4. Нет обработки ошибок: упавший `requests.post` после commit — и что? А если до? Side-effect'ы вне транзакции нужно осмыслить (outbox-паттерн — бонусный балл за упоминание).

Дизайн:
5. Нарушение SRP: валидация + БД + HTTP-уведомления в одном методе.
6. Стрела вложенности → guard clauses / ранние возвраты.
7. `== True` → просто `if note_data.get("active"):`... но лучше валидация схемой на входе.
8. Возврат `True/False` без причины — исключения или Result-тип.
9. Нет типизации, `note_data` — dict-помойка → DTO.
10. Синхронный `requests` + прямое создание зависимостей внутри метода (нетестируемо) → инъекция зависимостей.

Рефакторинг сводится ровно к структуре из части 2: схема на входе → доменная валидация → тонкий handler → репозиторий с параметризованными запросами → уведомления через интерфейс (и в идеале через outbox).
</details>

---

# Часть 4. Теория, которую спрашивают у Python-лидов (чек-лист для зубрёжки)

По каждому пункту ты должен уметь говорить 2–3 минуты без подготовки.

## Python-ядро
- **GIL**: что защищает (структуры интерпретатора, refcount), что НЕ защищает (твои инварианты), когда отпускается (I/O, C-extensions вроде numpy). Следствие: threads — для I/O-bound, processes — для CPU-bound, asyncio — для массового I/O. Новое: PEP 703, free-threaded CPython 3.13+.
- **Память**: reference counting + циклический GC (поколения), `__slots__`, почему `sys.getrefcount` возвращает +1.
- **Генераторы/итераторы**: протокол `__iter__`/`__next__`, ленивость, `yield from`, генератор как сопрограмма (send/throw) — и как из этого исторически вырос asyncio.
- **Декораторы**: с параметрами и без, `functools.wraps` (и что ломается без него), декоратор класса.
- **Дескрипторы**: `__get__/__set__`, как через них работают `property`, методы (bound method), `classmethod`.
- **Контекстные менеджеры**: `__enter__/__exit__`, `contextlib.contextmanager`, подавление исключений через возврат True из `__exit__`, `AsyncExitStack`.
- **Метаклассы** — хотя бы: «класс создаётся метаклассом, ABCMeta и ORM так работают; в прикладном коде почти всегда есть решение проще: `__init_subclass__`».
- **Типизация**: `Protocol` vs ABC (структурная vs номинальная), Generic, `TypeVar`, ковариантность на пальцах, `mypy --strict` в CI.
- Копирование: shallow vs deep; hashability и почему mutable нельзя в ключи dict.

## Asyncio
- Event loop, task vs coroutine vs future; когда происходит переключение (только на await).
- Отмена задач (`CancelledError` — почему её нельзя глотать), таймауты (`asyncio.timeout`), `TaskGroup`.
- Backpressure: `asyncio.Semaphore`, ограничение конкурентности при fan-out.

## Базы данных
- Транзакции и уровни изоляции: read committed vs repeatable read, что такое фантомы; какой уровень в Postgres по умолчанию.
- N+1 и как ловить (логирование запросов, `selectinload`/`joinedload`).
- Индексы: b-tree, составные (порядок колонок!), частичные, когда индекс не используется.
- Оптимистичные vs пессимистичные блокировки; `SELECT ... FOR UPDATE`; version-колонка в агрегате.
- Миграции: почему `ALTER TABLE` на большой таблице опасен, backward-compatible деплой (expand → migrate → contract).

## Брокеры и распределёнка (твоя задача — отсюда)
- At-most-once / at-least-once / exactly-once; почему exactly-once delivery — миф, а exactly-once *processing* = at-least-once + идемпотентность.
- Rabbit vs Kafka: очередь с ack и умным брокером vs лог с оффсетами и тупым брокером; когда что.
- Outbox-паттерн: как атомарно «записать в БД и отправить событие». Saga для распределённых транзакций (хотя бы идея).
- Retry: exponential backoff + jitter, retry budget, circuit breaker.
- Идемпотентность: ключи идемпотентности, natural idempotency (upsert/replace — твой случай).

## Архитектура и процессы (лидская часть)
- SOLID с примерами из своего кода (DIP ты теперь показываешь на INotesRepository).
- Как проводишь код-ревью: что смотришь в первую очередь (корректность/безопасность → дизайн → стиль), тон комментариев, «nit:» пометки, когда одобрить с замечаниями vs заблокировать.
- Как декомпозируешь и оцениваешь задачи; что делаешь, когда команда не успевает к дедлайну (резать скоуп, а не качество — и уметь это аргументировать).
- Как онбордишь джуна; как даёшь негативный фидбек (приватно, про работу, а не личность, с конкретикой).
- Инциденты: кто тушит, как пишется постмортем (blameless), action items.
- Технический долг: как продаёшь бизнесу (в терминах рисков и денег, не «код некрасивый»).

---

# Часть 5. План занятий до собеседования

**День 1–2.** Часть 1 (DDD): перерисуй схему слоёв по памяти. Открой свой проект и для 5 случайных файлов ответь: какой это слой, легальны ли его импорты. Найди в проекте нарушение правила зависимостей — оно почти наверняка есть, и это готовая история для собеседования («что бы я улучшил в текущем проекте»).

**День 3–4.** Часть 2: реализуй пайплайн заметок целиком у себя в проекте (это же твоя рабочая задача — двух зайцев). Схемы → домен → handler → consumer → тесты. Твои JSON — фикстуры.

**День 5.** Часть 3: прорешай все примеры. Правило: сначала ищешь ошибки сам, письменно, потом открываешь разбор. На собеседовании озвучивай мысли вслух — это оценивается.

**День 6.** Часть 4: пройди чек-лист, отметь дыры, закрой худшие три. Потренируй рассказ о себе и о текущем проекте (архитектура за 3 минуты: «сервис интеграции с 1С, DDD-слои, асинхронный consumer Rabbit, вот такие гарантии доставки...»).

**День 7.** Мок-интервью: попроси кого-то (или меня в новом чате) погонять тебя по частям 3–4 вслух, с таймером.

**На самом собеседовании:**
1. Live coding: сначала уточни требования и краевые случаи вслух, потом набросай план, потом код. Молчаливое кодирование — главная ошибка кандидатов.
2. Нашёл не все ошибки в код-ревью — не страшно; важнее приоритизация: безопасность и потеря данных раньше стиля.
3. Не знаешь ответ — говори, как бы выяснял: «не помню сигнатуру, но смотрел бы в сторону X, проверил бы Y». Для лида это нормальный и сильный ответ.
4. К каждой теме готовь пример из своей практики — истории запоминаются лучше определений.
