import time


def levenshtein_distance(a: str, b: str) -> int:
    """
    Классическое расстояние Левенштейна между строками a и b.
    Возвращает количество правок (вставка, удаление, замена).
    """
    # если одна из строк пустая
    if not a:
        return len(b)
    if not b:
        return len(a)

    # создаём матрицу (len(a)+1) * (len(b)+1)
    dp = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]

    # инициализация первой строки/столбца
    for i in range(len(a) + 1):
        dp[i][0] = i
    for j in range(len(b) + 1):
        dp[0][j] = j

    # заполнение матрицы
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            cost = 0 if a[i - 1] == b[j - 1] else 1
            dp[i][j] = min(
                dp[i - 1][j] + 1,  # удаление
                dp[i][j - 1] + 1,  # вставка
                dp[i - 1][j - 1] + cost  # замена (или совпадение)
            )
    return dp[len(a)][len(b)]


def damerau_levenshtein_distance(a: str, b: str) -> int:
    """
    Расстояние Дамерау-Левенштейна.
    Включает операцию перестановки двух соседних символов.
    """
    if not a:
        return len(b)
    if not b:
        return len(a)

    dp = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]

    for i in range(len(a) + 1):
        dp[i][0] = i
    for j in range(len(b) + 1):
        dp[0][j] = j

    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            cost = 0 if a[i - 1] == b[j - 1] else 1
            dp[i][j] = min(
                dp[i - 1][j] + 1,  # удаление
                dp[i][j - 1] + 1,  # вставка
                dp[i - 1][j - 1] + cost  # замена/совпадение
            )
            # если возможна перестановка (i>1, j>1) и символы соответствуют
            if i > 1 and j > 1 and a[i - 1] == b[j - 2] and a[i - 2] == b[j - 1]:
                dp[i][j] = min(dp[i][j], dp[i - 2][j - 2] + 1)  # перестановка

    return dp[len(a)][len(b)]


def perform_fuzzy_search(word: str, text: str, algorithm: str):
    """
    Разбиваем text на слова (например, по пробелам/знакам),
    вычисляем расстояние до каждого слова, сортируем и возвращаем результат.
    :param word: искомое слово
    :param text: весь текст корпуса
    :param algorithm: "levenshtein" или "damerau"
    :return: список кортежей (word_in_text, distance)
    """
    # разобьём текст тупо по пробелам и знакам пунктуации
    tokens = text.split()

    results = []
    if algorithm == "levenshtein":
        distance_func = levenshtein_distance
    elif algorithm == "damerau":
        distance_func = damerau_levenshtein_distance
    else:
        raise ValueError(f"Unknown algorithm: {algorithm}")

    for token in tokens:
        dist = distance_func(word, token)
        results.append((token, dist))

    # сортируем по distance
    results.sort(key=lambda x: x[1])
    return results
