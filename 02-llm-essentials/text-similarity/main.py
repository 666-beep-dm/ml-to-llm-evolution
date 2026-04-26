"""
Сравнение схожести текстов с помощью косинусного сходства (Cosine Similarity).
Используется модель sentence-transformers для получения эмбеддингов предложений.
"""

from itertools import combinations
from sentence_transformers import SentenceTransformer, util


# --- Конфигурация ---

# Многоязычная модель: хорошо работает с русским и английским текстом.
# При первом запуске модель (~500 МБ) скачается автоматически.
MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"

# Три произвольных предложения для сравнения
SENTENCES = [
    "Кошка сидит на тёплом подоконнике.",
    "Пушистый кот греется на солнечном окне.",
    "Программирование на Python — это увлекательно.",
]


# --- Основная логика ---

def compute_similarities(sentences: list[str], model: SentenceTransformer) -> dict:
    """
    Вычисляет косинусное сходство для всех пар предложений.

    Args:
        sentences: Список предложений для сравнения.
        model:     Загруженная модель sentence-transformers.

    Returns:
        Словарь вида {(i, j): score}, где score — float от -1 до 1.
    """
    # Получаем эмбеддинги (векторные представления) для каждого предложения
    embeddings = model.encode(sentences, convert_to_tensor=True)

    results = {}
    # Перебираем все уникальные пары индексов
    for i, j in combinations(range(len(sentences)), 2):
        score = util.cos_sim(embeddings[i], embeddings[j]).item()
        results[(i, j)] = round(score, 4)

    return results


def print_results(sentences: list[str], similarities: dict) -> None:
    """Выводит таблицу схожести и определяет наиболее похожую пару."""

    print("\n" + "=" * 60)
    print("  РЕЗУЛЬТАТЫ СРАВНЕНИЯ ТЕКСТОВ")
    print("=" * 60)

    # Печатаем исходные предложения
    print("\nПредложения:")
    for idx, sentence in enumerate(sentences, start=1):
        print(f"  [{idx}] {sentence}")

    # Печатаем таблицу сходства
    print("\nТаблица косинусного сходства:")
    print(f"  {'Пара':<12} {'Сходство':>10}   Интерпретация")
    print(f"  {'-'*12} {'-'*10}   {'-'*20}")

    for (i, j), score in similarities.items():
        pair_label = f"[{i+1}] vs [{j+1}]"
        interpretation = interpret_score(score)
        print(f"  {pair_label:<12} {score:>10.4f}   {interpretation}")

    # Определяем наиболее похожую пару
    best_pair = max(similarities, key=similarities.get)
    best_score = similarities[best_pair]
    i, j = best_pair

    print("\n" + "-" * 60)
    print(f"  🏆 Наиболее похожая пара: [{i+1}] и [{j+1}]")
    print(f"     Сходство: {best_score:.4f}")
    print(f'     "{sentences[i]}"')
    print(f'     "{sentences[j]}"')
    print("=" * 60 + "\n")


def interpret_score(score: float) -> str:
    """Возвращает текстовую интерпретацию числового значения сходства."""
    if score >= 0.90:
        return "Практически идентичны"
    elif score >= 0.75:
        return "Очень похожи"
    elif score >= 0.50:
        return "Умеренно похожи"
    elif score >= 0.25:
        return "Слабо похожи"
    else:
        return "Не похожи"


def main():
    print(f"Загрузка модели «{MODEL_NAME}»...")
    model = SentenceTransformer(MODEL_NAME)
    print("Модель загружена.")

    similarities = compute_similarities(SENTENCES, model)
    print_results(SENTENCES, similarities)


if __name__ == "__main__":
    main()