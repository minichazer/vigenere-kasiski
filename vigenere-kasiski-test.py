import string
import random
import re
import collections
import math
import functools


ALPHABET = string.ascii_lowercase
KEY_LENGTH = 10
NGRAMM_LENGTH = 2
FILE_NAME = "pin.txt"
WEIGHTS = {
    "a": 0.08167,
    "b": 0.01492,
    "c": 0.02782,
    "d": 0.04253,
    "e": 0.12702,
    "f": 0.02228,
    "g": 0.02015,
    "h": 0.06094,
    "i": 0.06966,
    "j": 0.00153,
    "k": 0.00772,
    "l": 0.04025,
    "m": 0.02406,
    "n": 0.06749,
    "o": 0.07507,
    "p": 0.01929,
    "q": 0.00095,
    "r": 0.05987,
    "s": 0.06327,
    "t": 0.09056,
    "u": 0.02758,
    "v": 0.00978,
    "w": 0.02360,
    "x": 0.00150,
    "y": 0.01974,
    "z": 0.00074,
}


def generate_key(n):
    """
    Generate a random key (lowercase latin) with a given length (n).
    """
    return "".join(random.choices(ALPHABET, k=n))


def find_closest(f):
    """
    Iterate through the dictionary (Relative Frequencies of Letters in the English Language)
    and finds the nearest value to given frequency (f).
    """
    res_key, res_val = min(WEIGHTS.items(), key=lambda x: abs(f - x[1]))
    return (res_key, res_val)


def factors(n):
    """
    Finds all factors of the given number (n) and returns a set.
    """
    step = 2 if n % 2 else 1
    return set(
        functools.reduce(
            list.__add__,
            ([i, n // i] for i in range(1, int(math.sqrt(n)) + 1, step) if n % i == 0),
        )
    )


def get_repeats(s, k):
    """
    Iterates through all the given text (s) and finds all possible substrings of length (k) (and number of entries).
    Returns dictionary -> {substring : number_of_entries, ... }
    """
    ctr = collections.Counter(s[i : i + k] for i in range(len(s) - k + 1))
    dct = {sub: c for sub, c in ctr.items() if c > 1}
    return dict(sorted(dct.items(), key=lambda item: item[1], reverse=True))


def shift(text):
    """
    Applies Caesar's shift by +1 to the given text.
    """
    output = ""
    for i in text:
        output += ALPHABET[(ALPHABET.index(i) + 1) % len(ALPHABET)]
    return output


def encrypt(text, key, j=0):
    """
    Applies Viginere's Cipher method to the given text with use of key.
    """
    output = ""
    for i in text:
        text_shift = ALPHABET.index(i) + 1
        key_shift = ALPHABET.index(key[j % len(key)]) % len(ALPHABET)
        new_letter = ALPHABET[(text_shift + key_shift - 1) % len(ALPHABET)]
        output += new_letter
        j += 1
    return output


if __name__ == "__main__":

    content = ""
    with open(FILE_NAME, "r") as f:
        content = "".join(f.readlines())
    print(f"Plain text:\n{content}\n")

    content = re.sub("[^a-zA-Z0-9\n]", "", content).lower()
    print(f"Deleting all spaces and excessive symbols (dots / commas / specials):\n{content}\n")

    # for DEBUG purpose:
    # secret_key = "anwlgpooxv"
    secret_key = generate_key(KEY_LENGTH)
    print(f"Generated random key: {secret_key}\n")

    cipher_text = encrypt(content, secret_key)
    print(f"Cipher text:\n{cipher_text}\n")

    repeats = get_repeats(cipher_text, NGRAMM_LENGTH)
    print(f"Collection of {str(NGRAMM_LENGTH)}-sized repetitive substrings:\n{repeats}\n")

    list_of_ngrammas = list(repeats.keys())[:5]
    print(f"List of {str(NGRAMM_LENGTH)}-sized most occurent ngrammas:\n{list_of_ngrammas}\n")

    # инициализация словаря для 5 наиболее часто встречающихся n-грамм
    ocr_count_dict = {ngramma: [] for ngramma in list_of_ngrammas}
    all_factors = {}

    # ищем расстояние между повторяющимися n-граммами
    for j in range(len(ocr_count_dict)):
        distances = [len(i) + 2 for i in cipher_text.split(list_of_ngrammas[j])][:-1]
        print(f"For '{list_of_ngrammas[j]}', distances between occurancies are: {distances[1:]}")
        possible_denominators = [list(factors(i)) for i in distances[1:]]

        # проверяем, если НОД уже есть в словаре
        # словари показываются частично, так как на вряд ли длина ключа
        # будет кратна факторам с маленьким количеством вхождений
        dfactors = {}
        for subarray in possible_denominators:
            for elem in subarray:
                if elem not in dfactors:
                    dfactors[elem] = 1
                else:
                    dfactors[elem] = dfactors.get(elem, 0) + 1

                if elem not in all_factors:
                    all_factors[elem] = 1
                else:
                    all_factors[elem] = all_factors.get(elem, 0) + 1

        # 1:10 => первый элемент списка всегда 1 (она является делителем любого числа)
        sorted_dfactors = dict(
            sorted(dfactors.items(), key=lambda item: item[1], reverse=True)[
                1 : 10 % len(dfactors)
            ]
        )
        print(f"Common factors between all denominators: {sorted_dfactors}\n")

        sorted_all_factors = dict(
            sorted(all_factors.items(), key=lambda item: item[1], reverse=True)[
                1 : 10 % len(all_factors)
            ]
        )

    print(f"Best possible assumptions on key length: {sorted_all_factors}\n")

    # possible_key = int(input("Choose one of factors to check if its a key length: "))
    possible_key = 10
    matrix = re.findall("." * possible_key, cipher_text)
    print(f"Assume, we have {str(possible_key)}-sized key.\n")
    print(f"Text divided by each {str(possible_key)}th char:\n {matrix}\n")

    # создаем двумерный список, где каждый элемент в списке - все Nth символы, объединенные в одну строку
    nth_elems_of_matrix = [[] for i in range(possible_key)]
    for i in range(len(cipher_text)):
        nth_elems_of_matrix[i % len(nth_elems_of_matrix)].append(cipher_text[i])

    print("Now, assumptions with use of frequency analysis for each nth symbol in divided parts:")

    prediction_key = ""
    entry_idx = 1
    for subarray in nth_elems_of_matrix:
        distances = []
        # for DEBUG purpose:
        # print(f"Current column number - {entry_idx}")

        # для применения частотного анализа к каждой из 10 полученных подстрок,
        # необходимо сделать сдвиг на +1 каждой подстроки 26 раз
        # это нужно для того, чтобы понять какая из возможных 26 получаемых комбинаций
        # наиболее "близка" (Эйлерская дистанций между векторами) к таблице частот букв
        # в английском языке
        for i in range(26):
            substr_freqs = {}
            for elem in subarray:
                if elem not in substr_freqs:
                    substr_freqs[elem] = subarray.count(elem)
            sorted_dict = dict(
                sorted(substr_freqs.items(), key=lambda item: item[1], reverse=True)
            )

            # вывод Nth-символьных столбцов и их буквенные частоты
            # print("".join(subarray[:len(subarray) - 1]))
            # print(
            #    f"[SHIFT-{i}] - Most frequent {entry_idx}th symbols in parts - {sorted_dict}"
            # )

            # замена количества вхождений на проценты (для сравение весов между двумя словарями)
            for key, value in substr_freqs.items():
                substr_freqs[key] = value / len(subarray)

            # Распределение (буква - частота (в %))
            # print(
            #    f"[SHIFT-{i}] - Distribution - {substr_freqs}"
            # )

            # расчет Эйлерской дистанции (сумма квадратов разниц значений между двумя векторами)
            # distance = (freq1[char] - freq2[char])^2 + ... (freq1[char] - freq2[char])^2,
            # n - длина алфавита
            distance = 0
            for letter, freq in WEIGHTS.items():
                if letter in substr_freqs:
                    distance += (substr_freqs[letter] - WEIGHTS[letter]) ** 2
                else:
                    distance += WEIGHTS[letter] ** 2
            distances.append(distance)

            # если нужно знать расстояние для каждого отдельного шифта (далее будет как элемент массива distances)
            # print(f"[SHIFT-{i}] distance - {distance}")

            # здесь сдвигаем строку вправо по алфавиту на +1 (Цезарь)
            subarray = shift(subarray)
            # вариант с функцией encrypt, но я честно говоря думаю это удалить xd
            # for char_index in range(len(subarray)):
            #    subarray[char_index] = encrypt(subarray[char_index], ALPHABET[(i + 1) % 26])

            # выводим расстояние между частотами в английском алфавите и рабочей подстрокой
            # print(f"For {entry_idx}th row the distance is - {distance}")
            # print()

        # находим наиболее вероятные (по убыванию) варианты сдвигов для каждого Nth столбца
        temp = {}
        for i in range(len(distances)):
            temp[i] = distances[i]
        predictions = list(dict(sorted(temp.items(), key=lambda item: item[1])[:10]))

        # Prediction Vector - расположенные по убыванию возможные варианты сдвигов относительно
        # начала алфавита для текущего столбца
        # условно, predictions[0] - наиболее вероятный сдвиг, а он же Nth-ый индекс ключа
        print(f"Most likely {entry_idx}th shift from prediction vector" 
              f"{predictions} => (26 - {predictions[0]}) % 26 = {(26 - predictions[0]) % 26}")

        prediction_key += ALPHABET[(26 - predictions[0]) % 26]
        entry_idx += 1

    print(f"\nPredicted key - {prediction_key}")
    print(f"The actual used key - {secret_key}")
