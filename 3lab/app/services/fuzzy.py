# два поиска: Левенштейн и 3-граммы
def levenshtein(a: str, b: str) -> int:
    if a == b: return 0
    if not a:  return len(b)
    if not b:  return len(a)
    v0 = list(range(len(b) + 1))
    v1 = [0] * (len(b) + 1)
    for i, ca in enumerate(a):
        v1[0] = i + 1
        for j, cb in enumerate(b):
            cost = 0 if ca == cb else 1
            v1[j + 1] = min(v1[j] + 1, v0[j + 1] + 1, v0[j] + cost)
        v0, v1 = v1, v0
    return v0[-1]

def ngram(a: str, b: str, n: int = 3) -> int:
    na = {a[i:i+n] for i in range(len(a) - n + 1)}
    nb = {b[i:i+n] for i in range(len(b) - n + 1)}
    return len(na.symmetric_difference(nb))
