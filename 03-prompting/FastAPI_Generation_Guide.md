```markdown
# FastAPI CRUD Generation: Prompt Engineering Guide
# Руководство по генерации FastAPI CRUD: Стратегии промптинга

> **RU:** Этот документ описывает три стратегии промптинга для генерации production-ready FastAPI CRUD сервисов с помощью LLM. Каждая стратегия разобрана с примером промпта, обоснованием и разбором антипаттернов.
>
> **EN:** This document covers three prompt engineering strategies for generating production-ready FastAPI CRUD services using LLMs. Each strategy includes a prompt example, rationale, and antipattern analysis.

---

## Table of Contents / Содержание

- [Strategy 1 — Instruction-based Prompting](#strategy-1--instruction-based-prompting)
- [Strategy 2 — Role Prompting](#strategy-2--role-prompting)
- [Strategy 3 — Few-shot Prompting](#strategy-3--few-shot-prompting)
- [Antipatterns](#antipatterns--антипаттерны)
- [Comparison & Conclusion](#comparison--conclusion--сравнение-и-вывод)

---

## Strategy 1 — Instruction-based Prompting

### 🇷🇺 RU — Описание стратегии

**Суть:** Промпт строится как техническое задание — с явными требованиями к стеку, версиям библиотек, структуре эндпоинтов и схемам данных. Модель воспринимает инструкцию как спецификацию и генерирует код строго в её рамках.

**Когда применять:** Когда у вас есть чёткие технические требования и вы хотите минимальной вариативности в ответе.

---

### 🇷🇺 RU — Пример промпта

```
Сгенерируй FastAPI CRUD сервис для сущности `Product` со следующими требованиями:

**Стек и версии:**
- Python 3.11
- FastAPI 0.111.x
- SQLAlchemy 2.0 (async, с использованием AsyncSession)
- Pydantic V2 (BaseModel с model_config)
- Alembic для миграций
- PostgreSQL как база данных
- asyncpg как драйвер

**Структура эндпоинтов (префикс: /api/v1/products):**
- POST   /         — создать продукт
- GET    /         — получить список (с пагинацией: skip, limit)
- GET    /{id}     — получить по ID
- PUT    /{id}     — обновить
- DELETE /{id}     — удалить (soft delete: поле is_deleted=True)

**Pydantic-схемы:**
- ProductBase: name (str), description (Optional[str]), price (Decimal), is_active (bool, default=True)
- ProductCreate(ProductBase)
- ProductUpdate(ProductBase) — все поля Optional
- ProductResponse(ProductBase) — добавить: id (UUID), created_at (datetime), is_deleted (bool)

**SQLAlchemy модель:**
- Таблица: products
- Поля: id (UUID, PK), name, description, price (Numeric 10,2), is_active, is_deleted (default False), created_at (server_default=now()), updated_at

**Требования к коду:**
- Использовать dependency injection для сессии БД (Depends)
- HTTP исключения: 404 если не найден, 422 при ошибке валидации
- Возвращать 201 при создании, 200 при остальных успешных операциях
- Не использовать глобальные переменные
- Покрыть каждый эндпоинт docstring в формате Google Style

Верни полный, рабочий код, разбитый по файлам:
`models.py`, `schemas.py`, `crud.py`, `router.py`, `dependencies.py`
```

---

### 🇬🇧 EN — Strategy Description

**Core idea:** The prompt is structured as a technical specification — with explicit requirements for the stack, library versions, endpoint structure, and data schemas. The model treats the instruction as a spec and generates code strictly within its boundaries.

**When to use:** When you have clear technical requirements and want minimal variability in the response.

---

### 🇬🇧 EN — Prompt Example

```
Generate a FastAPI CRUD service for the `Product` entity with the following requirements:

**Stack & Versions:**
- Python 3.11
- FastAPI 0.111.x
- SQLAlchemy 2.0 (async, using AsyncSession)
- Pydantic V2 (BaseModel with model_config)
- Alembic for migrations
- PostgreSQL as the database
- asyncpg as the driver

**Endpoint Structure (prefix: /api/v1/products):**
- POST   /         — create a product
- GET    /         — list with pagination (skip, limit)
- GET    /{id}     — get by ID
- PUT    /{id}     — update
- DELETE /{id}     — delete (soft delete: is_deleted=True)

**Pydantic Schemas:**
- ProductBase: name (str), description (Optional[str]), price (Decimal), is_active (bool, default=True)
- ProductCreate(ProductBase)
- ProductUpdate(ProductBase) — all fields Optional
- ProductResponse(ProductBase) — add: id (UUID), created_at (datetime), is_deleted (bool)

**SQLAlchemy Model:**
- Table: products
- Fields: id (UUID, PK), name, description, price (Numeric 10,2), is_active, is_deleted (default False), created_at (server_default=now()), updated_at

**Code Requirements:**
- Use dependency injection for DB session (Depends)
- HTTP exceptions: 404 if not found, 422 on validation error
- Return 201 on create, 200 on other successful operations
- No global variables
- Cover each endpoint with a Google Style docstring

Return complete, working code split into files:
`models.py`, `schemas.py`, `crud.py`, `router.py`, `dependencies.py`
```

---

### ✅ Strengths / Сильные стороны

| RU | EN |
|---|---|
| Максимальный контроль над выводом | Maximum control over output |
| Воспроизводимый результат | Reproducible result |
| Легко верифицировать соответствие | Easy to verify compliance |
| Подходит для CI/CD и автоматизации | Suitable for CI/CD and automation |

---

## Strategy 2 — Role Prompting

### 🇷🇺 RU — Описание стратегии

**Суть:** Модели назначается роль эксперта с конкретным опытом и ценностями. Вместо явных инструкций задаётся контекст, в котором модель сама принимает архитектурные решения, опираясь на best practices.

**Когда применять:** Когда требуется не просто рабочий код, а архитектурно обоснованное решение с соблюдением принципов clean architecture, SOLID и DI.

---

### 🇷🇺 RU — Пример промпта

```
Ты — Senior Backend Engineer с 8+ годами опыта разработки на Python.
Ты специализируешься на построении production-ready микросервисов с использованием FastAPI,
придерживаешься принципов Clean Architecture, SOLID и Domain-Driven Design.

Твои профессиональные принципы:
- Никогда не смешиваешь бизнес-логику с роутерами
- Используешь Repository Pattern для изоляции слоя данных
- Применяешь Dependency Injection через интерфейсы (Protocol)
- Пишешь код, который легко тестировать без поднятия реальной БД
- Всегда версионируешь API (/api/v1/)
- Используешь async везде, где это имеет смысл

Задача: спроектируй и сгенерируй CRUD сервис для сущности `Order` (заказ).

Сущность Order включает: id, customer_id, status (enum: pending/processing/completed/cancelled),
total_amount (Decimal), created_at, updated_at.

Реши самостоятельно:
- Как организовать слои (router → service → repository → model)
- Как обработать смену статуса с валидацией переходов (State Machine)
- Как организовать dependency injection
- Какие HTTP-коды использовать и почему

Сгенерируй код так, как ты написал бы его для production-проекта в команде из 5+ разработчиков.
Прокомментируй ключевые архитектурные решения.
```

---

### 🇬🇧 EN — Strategy Description

**Core idea:** The model is assigned an expert role with specific experience and values. Instead of explicit instructions, a context is provided within which the model makes its own architectural decisions based on best practices.

**When to use:** When you need not just working code, but an architecturally sound solution that adheres to clean architecture, SOLID, and DI principles.

---

### 🇬🇧 EN — Prompt Example

```
You are a Senior Backend Engineer with 8+ years of Python development experience.
You specialize in building production-ready microservices with FastAPI,
adhering to Clean Architecture, SOLID, and Domain-Driven Design principles.

Your professional principles:
- Never mix business logic with routers
- Use the Repository Pattern to isolate the data layer
- Apply Dependency Injection through interfaces (Protocol)
- Write code that is easy to test without a real database
- Always version the API (/api/v1/)
- Use async everywhere it makes sense

Task: design and generate a CRUD service for the `Order` entity.

Order includes: id, customer_id, status (enum: pending/processing/completed/cancelled),
total_amount (Decimal), created_at, updated_at.

Decide on your own:
- How to organize layers (router → service → repository → model)
- How to handle status transitions with validation (State Machine)
- How to organize dependency injection
- Which HTTP codes to use and why

Generate code as you would write it for a production project in a team of 5+ developers.
Comment on key architectural decisions.
```

---

### ✅ Strengths / Сильные стороны

| RU | EN |
|---|---|
| Генерирует архитектурно зрелый код | Generates architecturally mature code |
| Модель сама выбирает паттерны | Model selects patterns autonomously |
| Подходит для сложных доменных задач | Suitable for complex domain tasks |
| Результат ближе к senior code review | Output resembles a senior code review |

---

## Strategy 3 — Few-shot Prompting

### 🇷🇺 RU — Описание стратегии

**Суть:** Промпт включает один или несколько конкретных примеров (input → output), которые задают стиль кода, соглашения об именовании и структуру ответа. Модель экстраполирует паттерн на новую задачу.

**Когда применять:** Когда у вас уже есть кодовая база с устоявшимися соглашениями и нужно сгенерировать аналогичный модуль без написания полной спецификации.

---

### 🇷🇺 RU — Пример промпта

```
Ты — Python-разработчик. Генерируй FastAPI-код строго в стиле примеров ниже.
Соблюдай соглашения об именовании, структуру файлов и паттерны из примера.

---

### ПРИМЕР (Input → Output)

**Сущность:** Category (id: UUID, name: str, slug: str, is_active: bool)

**schemas.py:**
```python
from uuid import UUID
from pydantic import BaseModel, ConfigDict

class CategoryBase(BaseModel):
    name: str
    slug: str
    is_active: bool = True

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(CategoryBase):
    name: str | None = None
    slug: str | None = None
    is_active: bool | None = None

class CategoryResponse(CategoryBase):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
```

**crud.py:**
```python
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Category
from app.schemas import CategoryCreate, CategoryUpdate

async def get_category(db: AsyncSession, category_id: UUID) -> Category | None:
    result = await db.execute(select(Category).where(Category.id == category_id))
    return result.scalar_one_or_none()

async def create_category(db: AsyncSession, data: CategoryCreate) -> Category:
    obj = Category(**data.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj
```

**router.py:**
```python
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db
from app import crud, schemas

router = APIRouter(prefix="/api/v1/categories", tags=["Categories"])

@router.get("/{category_id}", response_model=schemas.CategoryResponse)
async def read_category(category_id: UUID, db: AsyncSession = Depends(get_db)):
    """Retrieve a category by ID."""
    obj = await crud.get_category(db, category_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return obj
```

---

### ЗАДАЧА (Task)

Используя точно такой же стиль, соглашения и паттерны из примера выше,
сгенерируй аналогичный CRUD модуль для сущности:

**Tag** (id: UUID, name: str, color: str [hex-код, например #FF5733], created_at: datetime)

Сгенерируй: `schemas.py`, `crud.py`, `router.py` (все 5 CRUD операций).
```

---

### 🇬🇧 EN — Strategy Description

**Core idea:** The prompt includes one or more concrete examples (input → output) that establish the code style, naming conventions, and response structure. The model extrapolates the pattern to a new task.

**When to use:** When you already have a codebase with established conventions and need to generate a similar module without writing a full specification.

---

### 🇬🇧 EN — Prompt Example

```
You are a Python developer. Generate FastAPI code strictly following the style of the examples below.
Adhere to the naming conventions, file structure, and patterns from the example.

---

### EXAMPLE (Input → Output)

**Entity:** Category (id: UUID, name: str, slug: str, is_active: bool)

**schemas.py:**
```python
from uuid import UUID
from pydantic import BaseModel, ConfigDict

class CategoryBase(BaseModel):
    name: str
    slug: str
    is_active: bool = True

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(CategoryBase):
    name: str | None = None
    slug: str | None = None
    is_active: bool | None = None

class CategoryResponse(CategoryBase):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
```

**crud.py:**
```python
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Category
from app.schemas import CategoryCreate, CategoryUpdate

async def get_category(db: AsyncSession, category_id: UUID) -> Category | None:
    result = await db.execute(select(Category).where(Category.id == category_id))
    return result.scalar_one_or_none()

async def create_category(db: AsyncSession, data: CategoryCreate) -> Category:
    obj = Category(**data.model_dump())
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj
```

**router.py:**
```python
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db
from app import crud, schemas

router = APIRouter(prefix="/api/v1/categories", tags=["Categories"])

@router.get("/{category_id}", response_model=schemas.CategoryResponse)
async def read_category(category_id: UUID, db: AsyncSession = Depends(get_db)):
    """Retrieve a category by ID."""
    obj = await crud.get_category(db, category_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return obj
```

---

### TASK

Using exactly the same style, conventions, and patterns from the example above,
generate an equivalent CRUD module for the entity:

**Tag** (id: UUID, name: str, color: str [hex code, e.g. #FF5733], created_at: datetime)

Generate: `schemas.py`, `crud.py`, `router.py` (all 5 CRUD operations).
```

---

### ✅ Strengths / Сильные стороны

| RU | EN |
|---|---|
| Обеспечивает стилистическое единство кода | Ensures stylistic consistency of code |
| Не требует описания всех деталей | No need to describe every detail |
| Идеален для масштабирования кодовой базы | Ideal for scaling an existing codebase |
| Минимизирует «творческую свободу» модели | Minimizes the model's "creative freedom" |

---

## Antipatterns / Антипаттерны

> **RU:** Следующие антипаттерны — наиболее распространённые ошибки при составлении промптов для генерации backend-кода. Их игнорирование приводит к нерабочему, небезопасному или нечитаемому коду.
>
> **EN:** The following antipatterns are the most common mistakes when writing prompts for backend code generation. Ignoring them leads to broken, insecure, or unreadable code.

---

### ❌ Antipattern 1 — «Ленивый» промптинг / "Lazy" Prompting

| | RU | EN |
|---|---|---|
| **Пример** | `Напиши FastAPI CRUD.` | `Write a FastAPI CRUD.` |
| **Проблема** | Нет сущности, стека, версий, структуры. Модель генерирует устаревший boilerplate с `db.query()` вместо async SQLAlchemy 2.0. | No entity, stack, versions, or structure. The model generates outdated boilerplate with `db.query()` instead of async SQLAlchemy 2.0. |
| **Решение** | Всегда указывай минимум: сущность, версии библиотек, тип БД, структуру эндпоинтов. | Always specify at minimum: entity, library versions, DB type, and endpoint structure. |

---

### ❌ Antipattern 2 — Отсутствие версий библиотек / Missing Library Versions

| | RU | EN |
|---|---|---|
| **Пример** | `Используй SQLAlchemy и Pydantic.` | `Use SQLAlchemy and Pydantic.` |
| **Проблема** | Модель может сгенерировать код для SQLAlchemy 1.4 (синхронный) и Pydantic V1 (`.dict()` вместо `.model_dump()`), что несовместимо с современным стеком. | The model may generate code for SQLAlchemy 1.4 (sync) and Pydantic V1 (`.dict()` instead of `.model_dump()`), incompatible with the modern stack. |
| **Решение** | Явно указывай: `SQLAlchemy 2.0 (async)`, `Pydantic V2`, `FastAPI 0.111.x`. | Explicitly specify: `SQLAlchemy 2.0 (async)`, `Pydantic V2`, `FastAPI 0.111.x`. |

---

### ❌ Antipattern 3 — Смешивание слоёв в промпте / Mixing Layers in the Prompt

| | RU | EN |
|---|---|---|
| **Пример** | `Напиши роутер, который напрямую обращается к БД через SQLAlchemy.` | `Write a router that directly queries the DB via SQLAlchemy.` |
| **Проблема** | Ты сам инструктируешь модель нарушить архитектуру. Результат — монолитный, нетестируемый роутер с бизнес-логикой и SQL внутри. | You are explicitly instructing the model to violate architecture. The result is a monolithic, untestable router with business logic and SQL inside. |
| **Решение** | Явно опиши слои: `router → service → repository → model`. Запрети прямые DB-вызовы в роутерах. | Explicitly describe layers: `router → service → repository → model`. Prohibit direct DB calls in routers. |

---

### ❌ Antipattern 4 — Отсутствие требований к обработке ошибок / No Error Handling Requirements

| | RU | EN |
|---|---|---|
| **Пример** | `Сгенерируй GET /products/{id} эндпоинт.` | `Generate a GET /products/{id} endpoint.` |
| **Проблема** | Модель может вернуть `None` или вызвать `AttributeError` вместо `HTTPException(404)`. Без явного указания — обработка ошибок непредсказуема. | The model may return `None` or raise `AttributeError` instead of `HTTPException(404)`. Without explicit instruction, error handling is unpredictable. |
| **Решение** | Всегда перечисляй HTTP-статусы: `404 — не найден`, `422 — ошибка валидации`, `409 — конфликт`. | Always enumerate HTTP statuses: `404 — not found`, `422 — validation error`, `409 — conflict`. |

---

### ❌ Antipattern 5 — Перегруженный одиночный промпт / Overloaded Single Prompt

| | RU | EN |
|---|---|---|
| **Пример** | `Напиши весь микросервис: аутентификацию, CRUD для 5 сущностей, кэширование Redis, Celery задачи, Docker-конфиг и тесты.` | `Write the entire microservice: authentication, CRUD for 5 entities, Redis caching, Celery tasks, Docker config, and tests.` |
| **Проблема** | Контекстное окно модели не резиновое. При перегрузке страдает качество каждого компонента: код становится поверхностным, появляются заглушки и `# TODO`. | The model's context window is not infinite. Overloading degrades the quality of every component: code becomes shallow, stubs and `# TODO` comments appear. |
| **Решение** | Декомпозируй задачу. Один промпт — одна ответственность. Используй цепочку промптов (prompt chaining). | Decompose the task. One prompt — one responsibility. Use prompt chaining. |

---

## Comparison & Conclusion / Сравнение и вывод

### Сравнительная таблица / Comparison Table

| Критерий / Criterion | Instruction-based | Role Prompting | Few-shot Prompting |
|---|:---:|:---:|:---:|
| **RU:** Контроль над структурой кода | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **EN:** Control over code structure | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **RU:** Архитектурная зрелость | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **EN:** Architectural maturity | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **RU:** Стилистическое единство | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **EN:** Stylistic consistency | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| **RU:** Воспроизводимость результата | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **EN:** Result reproducibility | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| **RU:** Сложность написания промпта | Средняя | Низкая | Высокая |
| **EN:** Prompt writing complexity | Medium | Low | High |
| **RU:** Лучший сценарий применения | Новый сервис с нуля | Рефакторинг, архитектура | Расширение кодовой базы |
| **EN:** Best use case | New service from scratch | Refactoring, architecture | Extending a codebase |

---

### 🇷🇺 RU — Аналитический вывод

Для **архитектурных задач** — проектирования слоёв, выбора паттернов, принятия решений по DI и тестируемости — наиболее эффективен **Role Prompting (Стратегия 2)**. Причина: языковая модель, работающая в роли Senior Engineer, активирует соответствующие паттерны из своих обучающих данных и применяет их самостоятельно, без необходимости перечислять каждый из них явно. Это снижает когнитивную нагрузку на автора промпта и повышает качество архитектурных решений.

Для **воспроизводимой генерации по спецификации** — например, в CI/CD пайплайне или при автоматизации кодогенерации — оптимален **Instruction-based Prompting (Стратегия 1)**. Он даёт детерминированный результат, легко верифицируемый по чеклисту.

**Few-shot Prompting (Стратегия 3)** побеждает в контексте **масштабирования существующего проекта**: когда нужно добавить пятый, десятый, двадцатый модуль в одном стиле — пример из кодовой базы работает как «живая спецификация» и исключает стилистический дрейф.

**Рекомендуемая комбинация для production-проектов:**
```
Role Prompting → для проектирования архитектуры
Instruction-based → для генерации конкретных модулей
Few-shot → для поддержания стилистической согласованности
```

---

### 🇬🇧 EN — Analytical Conclusion

For **architectural tasks** — designing layers, selecting patterns, making decisions about DI and testability — **Role Prompting (Strategy 2)** is the most effective. The reason: a language model operating in the role of a Senior Engineer activates the corresponding patterns from its training data and applies them autonomously, without needing each one enumerated explicitly. This reduces cognitive load on the prompt author and improves the quality of architectural decisions.

For **reproducible spec-driven generation** — e.g., in a CI/CD pipeline or code generation automation — **Instruction-based Prompting (Strategy 1)** is optimal. It produces a deterministic result that is easy to verify against a checklist.

**Few-shot Prompting (Strategy 3)** wins in the context of **scaling an existing project**: when you need to add the fifth, tenth, or twentieth module in the same style — an example from the codebase acts as a "living specification" and eliminates stylistic drift.

**Recommended combination for production projects:**
```
Role Prompting    → for architectural design
Instruction-based → for generating specific modules
Few-shot          → for maintaining stylistic consistency
```

---

## Quick Reference / Шпаргалка

```
✅ DO (RU)                              ✅ DO (EN)
──────────────────────────────────────  ──────────────────────────────────────
Указывай версии библиотек               Specify library versions
Описывай слои архитектуры               Describe architectural layers
Задавай HTTP-статусы явно               Define HTTP status codes explicitly
Используй роль для архитектуры          Use role for architectural tasks
Давай пример для стиля кода             Provide an example for code style
Декомпозируй большие задачи             Decompose large tasks

❌ DON'T (RU)                           ❌ DON'T (EN)
──────────────────────────────────────  ──────────────────────────────────────
Писать «напиши FastAPI CRUD»            Write "write FastAPI CRUD"
Смешивать слои в инструкции             Mix layers in the instruction
Пихать всё в один промпт               Cram everything into one prompt
Забывать про обработку ошибок           Forget about error handling
Игнорировать async/sync различия        Ignore async/sync distinctions
```

---

*Generated by: Senior Python Developer + Lead AI Engineer*
*Stack: FastAPI · SQLAlchemy 2.0 · Pydantic V2 · PostgreSQL · Python 3.11*
```
