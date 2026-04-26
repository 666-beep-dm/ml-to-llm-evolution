```markdown
# Промпты: «Объясни, что такое REST API» / Prompts: "Explain What REST API Is"

---

## Введение / Introduction

**RU:** Этот документ создан в учебных целях и демонстрирует разницу между эффективными и неэффективными промптами на примере одной темы — «Объясни, что такое REST API». Каждый промпт приведён на русском и английском языках с пояснением, почему он считается хорошим или плохим. Цель — помочь разработчикам, техническим писателям и всем, кто работает с LLM, научиться формулировать точные, контекстные и результативные запросы.

**EN:** This document is created for educational purposes and demonstrates the difference between effective and ineffective prompts, using the topic "Explain What REST API Is" as a case study. Each prompt is provided in both Russian and English, with an explanation of why it is considered good or bad. The goal is to help developers, technical writers, and anyone working with LLMs learn how to craft precise, context-rich, and result-oriented prompts.

---

## ❌ Плохие промпты / Bad Prompts

---

### ❌ Плохой промпт #1

**RU:** `Расскажи про REST API.`

**EN:** `Tell me about REST API.`

> **Почему плохой (RU):** Промпт слишком расплывчатый. Нет контекста, целевой аудитории, формата ответа или ограничений по объёму. Модель не знает, нужен ли краткий обзор, глубокая техническая статья или простое объяснение для новичка. Результат будет непредсказуемым.
>
> **Why it's bad (EN):** The prompt is too vague. There is no context, target audience, response format, or length constraint. The model doesn't know whether a brief overview, a deep technical article, or a simple beginner explanation is needed. The output will be unpredictable.

---

### ❌ Плохой промпт #2

**RU:** `REST API — это хорошо или плохо? Объясни.`

**EN:** `Is REST API good or bad? Explain.`

> **Почему плохой (RU):** Вопрос сформулирован в оценочной манере и предполагает субъективный ответ. REST API — это архитектурный стиль, а не объект для моральной оценки. Такая формулировка уводит модель от фактической информации в сторону мнений.
>
> **Why it's bad (EN):** The question is framed in an evaluative manner and implies a subjective answer. REST API is an architectural style, not something to be judged as good or bad. This framing steers the model away from factual information toward opinions.

---

### ❌ Плохой промпт #3

**RU:** `Напиши всё, что знаешь о REST API, HTTP, веб-разработке, микросервисах, JSON, XML, GraphQL и gRPC.`

**EN:** `Write everything you know about REST API, HTTP, web development, microservices, JSON, XML, GraphQL, and gRPC.`

> **Почему плохой (RU):** Промпт содержит слишком много несвязанных тем одновременно. Это приводит к поверхностному, перегруженному ответу, в котором ни одна из тем не раскрыта качественно. Фокус полностью отсутствует.
>
> **Why it's bad (EN):** The prompt contains too many unrelated topics at once. This leads to a shallow, overloaded response where none of the topics are covered well. There is a complete lack of focus.

---

### ❌ Плохой промпт #4

**RU:** `Объясни REST API так, как будто ты уже объяснял это раньше.`

**EN:** `Explain REST API as if you've already explained it before.`

> **Почему плохой (RU):** Инструкция бессмысленна и создаёт ложный контекст. У языковой модели нет памяти о предыдущих сессиях, поэтому такая формулировка не даёт модели никакой полезной информации о том, как строить ответ.
>
> **Why it's bad (EN):** The instruction is meaningless and creates a false context. A language model has no memory of previous sessions, so this phrasing gives the model no useful information about how to structure the response.

---

### ❌ Плохой промпт #5

**RU:** `REST API объяснение пожалуйста быстро коротко`

**EN:** `REST API explanation please fast short`

> **Почему плохой (RU):** Промпт написан небрежно, без знаков препинания и чёткой структуры. Слова «быстро» и «коротко» — субъективные и не задают конкретных ограничений (например, «не более 3 предложений» или «до 100 слов»). Отсутствие структуры снижает качество ответа.
>
> **Why it's bad (EN):** The prompt is written carelessly, without punctuation or clear structure. The words "fast" and "short" are subjective and don't set concrete constraints (e.g., "no more than 3 sentences" or "under 100 words"). The lack of structure reduces the quality of the response.

---

## ✅ Хорошие промпты / Good Prompts

---

### ✅ Хороший промпт #1 — для Junior-разработчика / For a Junior Developer

**RU:**
```
Ты — опытный backend-разработчик и наставник.
Я — junior-разработчик с базовыми знаниями HTTP и веб-технологий.
Объясни, что такое REST API: что это такое, на каких принципах основано и зачем используется в разработке.
Используй технически точный, но доступный язык. Структурируй ответ с заголовками:
1. Определение
2. Основные принципы REST
3. Пример использования
Объём: не более 300 слов.
```

**EN:**
```
You are an experienced backend developer and mentor.
I am a junior developer with basic knowledge of HTTP and web technologies.
Explain what REST API is: what it is, what principles it is based on, and why it is used in development.
Use technically accurate but accessible language. Structure the response with headings:
1. Definition
2. Core REST Principles
3. Usage Example
Length: no more than 300 words.
```

> **Почему хороший (RU):** Промпт задаёт роль модели (наставник), роль пользователя (junior), конкретную тему, целевую аудиторию, формат (заголовки, структура) и ограничение по объёму. Модель получает всё необходимое для точного и релевантного ответа.
>
> **Why it's good (EN):** The prompt defines the model's role (mentor), the user's role (junior), a specific topic, target audience, format (headings, structure), and a length constraint. The model has everything it needs to produce an accurate and relevant response.

---

### ✅ Хороший промпт #2 — для ребёнка / For a Child

**RU:**
```
Ты — учитель, который умеет объяснять сложные технические вещи простыми словами для детей 10–12 лет.
Объясни, что такое REST API, используя аналогию из повседневной жизни (например, заказ еды в ресторане или поход в библиотеку).
Избегай технических терминов. Если термин неизбежен — сразу объясни его.
Формат: 3–4 коротких абзаца с примером-историей.
```

**EN:**
```
You are a teacher who can explain complex technical concepts in simple words for children aged 10–12.
Explain what REST API is using an analogy from everyday life (e.g., ordering food at a restaurant or visiting a library).
Avoid technical jargon. If a term is unavoidable, explain it immediately.
Format: 3–4 short paragraphs with a story-based example.
```

> **Почему хороший (RU):** Чётко определена роль модели и целевая аудитория (дети 10–12 лет). Задан формат (аналогия, история) и явные ограничения на использование терминологии. Это позволяет получить объяснение, которое будет действительно понятно ребёнку.
>
> **Why it's good (EN):** The model's role and target audience (children aged 10–12) are clearly defined. The format (analogy, story) is specified along with explicit constraints on terminology use. This ensures an explanation that a child can genuinely understand.

---

### ✅ Хороший промпт #3 — для нетехнического менеджера / For a Non-Technical Manager

**RU:**
```
Ты — технический консультант, объясняющий IT-концепции бизнес-аудитории.
Твой слушатель — продакт-менеджер без технического образования, который хочет понять, что такое REST API и зачем его используют в продуктах компании.
Объясни без кода и технических деталей. Сделай акцент на бизнес-ценности и практических примерах (мобильные приложения, интеграции с партнёрами).
Формат: короткое введение + маркированный список из 4–5 ключевых тезисов + 1 практический пример.
```

**EN:**
```
You are a technical consultant explaining IT concepts to a business audience.
Your listener is a product manager without a technical background who wants to understand what REST API is and why it is used in the company's products.
Explain without code or technical details. Focus on business value and practical examples (mobile apps, partner integrations).
Format: short introduction + bulleted list of 4–5 key points + 1 practical example.
```

> **Почему хороший (RU):** Промпт адаптирован под конкретного читателя (нетехнический менеджер), задаёт запрет на код, делает акцент на бизнес-ценности и определяет точный формат вывода. Ответ будет максимально полезен именно для этой аудитории.
>
> **Why it's good (EN):** The prompt is tailored to a specific reader (non-technical manager), prohibits code, emphasizes business value, and defines an exact output format. The response will be maximally useful for this particular audience.

---

### ✅ Хороший промпт #4 — сравнительный анализ / Comparative Analysis

**RU:**
```
Ты — старший разработчик, готовящий обучающий материал для команды.
Объясни, что такое REST API, и сравни его с SOAP и GraphQL по следующим критериям:
- Простота использования
- Производительность
- Гибкость
- Типичные сценарии применения
Аудитория: middle-разработчики, знакомые с HTTP.
Формат: таблица сравнения + краткий вывод (2–3 предложения) о том, когда лучше выбрать REST.
```

**EN:**
```
You are a senior developer preparing educational material for your team.
Explain what REST API is and compare it to SOAP and GraphQL using the following criteria:
- Ease of use
- Performance
- Flexibility
- Typical use cases
Audience: mid-level developers familiar with HTTP.
Format: comparison table + brief conclusion (2–3 sentences) on when REST is the best choice.
```

> **Почему хороший (RU):** Промпт задаёт конкретную задачу (сравнение), аудиторию с известным уровнем знаний, чёткие критерии оценки и точный формат (таблица + вывод). Это исключает неоднозначность и даёт структурированный, практически применимый результат.
>
> **Why it's good (EN):** The prompt specifies a concrete task (comparison), an audience with a known knowledge level, clear evaluation criteria, and an exact format (table + conclusion). This eliminates ambiguity and produces a structured, practically applicable result.

---

### ✅ Хороший промпт #5 — для README / For a README File

**RU:**
```
Ты — технический писатель, специализирующийся на документации для open-source проектов.
Напиши раздел «Что такое REST API» для README.md проекта на GitHub.
Аудитория: разработчики, которые только начали изучать проект и могут не знать основ REST.
Требования:
- Используй Markdown-разметку (заголовки, жирный шрифт, блоки кода)
- Включи краткое определение, 3–4 ключевых принципа и минимальный пример HTTP-запроса (GET /users)
- Объём: не более 200 слов
- Тон: профессиональный, но дружелюбный
```

**EN:**
```
You are a technical writer specializing in documentation for open-source projects.
Write a "What is REST API" section for a project's README.md on GitHub.
Audience: developers who are new to the project and may not know the basics of REST.
Requirements:
- Use Markdown formatting (headings, bold text, code blocks)
- Include a brief definition, 3–4 key principles, and a minimal HTTP request example (GET /users)
- Length: no more than 200 words
- Tone: professional but friendly
```

> **Почему хороший (RU):** Промпт точно имитирует реальный рабочий сценарий. Заданы роль, платформа (GitHub README), аудитория, технические требования к форматированию, конкретный пример для включения и ограничение на объём. Результат можно использовать в продакшене без доработки.
>
> **Why it's good (EN):** The prompt accurately mimics a real-world work scenario. The role, platform (GitHub README), audience, technical formatting requirements, a specific example to include, and a length constraint are all defined. The result can be used in production without modification.

---

## Итог / Summary

| | **RU** | **EN** |
|---|---|---|
| **Роль** | Всегда указывай, кем должна выступать модель | Always define what role the model should play |
| **Аудитория** | Укажи, для кого предназначен ответ | Specify who the response is intended for |
| **Контекст** | Дай модели понять, зачем нужен ответ | Give the model context for why the answer is needed |
| **Формат** | Опиши структуру ответа | Describe the structure of the response |
| **Ограничения** | Задай объём, стиль, запреты | Set length, style, and restrictions |

> **RU:** Хороший промпт — это не вопрос, а техническое задание. Чем точнее ты описываешь контекст и ожидания, тем полезнее и предсказуемее результат.
>
> **EN:** A good prompt is not a question — it is a specification. The more precisely you describe the context and expectations, the more useful and predictable the output.
```
