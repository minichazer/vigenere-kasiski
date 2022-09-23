import string
import random
import re
import collections
import math
import functools
import sys


ALPHABET = string.ascii_lowercase
KEY_LIMIT = 32
KEY_START = 2
KEY_LENGTH = random.randint(KEY_START, KEY_LIMIT)
FILE_NAME = "pin2.txt"
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


def encrypt(text, key, decode=False, j=0):
    """
    Applies Viginere's Cipher method to the given text with use of key.
    """
    output = ""
    for i in text:
        text_shift = ALPHABET.index(i) + 1
        key_shift = ALPHABET.index(key[j % len(key)]) % len(ALPHABET)
        if not decode:
            new_letter = ALPHABET[(text_shift + key_shift - 1) % len(ALPHABET)]
        else:
            temp = text_shift - key_shift - 1
            if temp < 0:
                temp = 26 + temp
            new_letter = ALPHABET[(temp) % len(ALPHABET)]
        output += new_letter
        j += 1
    return output


if __name__ == "__main__":
    orig_stdout = sys.stdout
    f = open("log.txt", "w")
    sys.stdout = f

    content = ""
    with open(FILE_NAME, "r") as f:
        content = "".join(f.readlines())
    print(f"Plain text:\n{content}\n")

    content = re.sub("[^a-zA-Z\n]", "", content).lower()
    print(
        f"Deleting all spaces and excessive symbols (dots / commas / specials):\n{content}\n"
    )

    secret_key = generate_key(KEY_LENGTH)
    print(f"Generated random key: {secret_key}\n")

    cipher_text = encrypt(content, secret_key)
    print(f"Cipher text:\n{cipher_text}\n")

    repeats = get_repeats(cipher_text, 2)
    # print(f"Collection of {str(2)}-sized repetitive substrings:\n{repeats}\n")

    list_of_ngrammas = list(repeats.keys())[:KEY_LIMIT]
    print(f"List of {str(2)}-sized most occurent ngrammas:\n{list_of_ngrammas}\n")

    all_factors = {}
    # ищем расстояние между повторяющимися n-граммами
    for j in range(len(list_of_ngrammas)):
        distances = [len(i) + 2 for i in cipher_text.split(list_of_ngrammas[j])][:-1]
        # print(f"For '{list_of_ngrammas[j]}', distances between occurancies are: {distances[1:]}")
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

        # print(f"Common factors between all denominators: {sorted_dfactors}\n")
        sorted_all_factors = dict(
            sorted(all_factors.items(), key=lambda item: item[1], reverse=True)[
                1 : int(KEY_LIMIT / 2) + 1
            ]
        )
        # int(len(all_factors) / 2)
        # int(KEY_LIMIT / 2) + 1

    # print(f"[DEBUG]Factors frequencies: {sorted_all_factors}\n")
    saf_sum = sum(sorted_all_factors.values())
    all_factors_list = list(sorted_all_factors)

    saf_sum = sum(sorted_all_factors.values())
    for key, value in sorted_all_factors.items():
        sorted_all_factors[key] = round(value / saf_sum, 5)
    print(f"Best possible assumptions on key length: {sorted_all_factors}\n")

    # possible_key = int(input("Choose one of factors to check if its a key length: "))
    possible_keys = {}
    # possible_factors = list(sorted_all_factors)
    distances_mean = {}
    distances_min = {}
    for factor in list(sorted_all_factors):
        # нет смысла искать возможный ключ, длина которого больше, чем максимально нами допускаемая
        if factor > KEY_LIMIT:
            break

        # если нужно посмотреть на то, как делится текст на N-ные блоки
        # matrix = re.findall("." * factor, cipher_text)
        # print(f"Text divided by each {str(possible_key)}th char:\n {matrix}\n")

        # создаем двумерный список, где каждый элемент в списке - все Nth символы, объединенные в одну строку
        nth_elems_of_matrix = [[] for i in range(factor)]
        for i in range(len(cipher_text)):
            nth_elems_of_matrix[i % len(nth_elems_of_matrix)].append(cipher_text[i])

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
            predictions = list(dict(sorted(temp.items(), key=lambda item: item[1])[:3]))

            # Prediction Vector - расположенные по убыванию возможные варианты сдвигов относительно
            # начала алфавита для текущего столбца
            # условно, predictions[0] - наиболее вероятный сдвиг, а он же Nth-ый индекс ключа
            # print(f"Most likely {entry_idx}th shift from prediction vector"
            #    f" {predictions[0]} => (26 - {predictions[0]}) % 26 = {(26 - predictions[0]) % 26}")

            prediction_key += ALPHABET[(26 - predictions[0]) % 26]
            entry_idx += 1

        print(f"Predicted key for length {factor} - {prediction_key}")
        possible_keys[factor] = prediction_key
        distances_mean[prediction_key] = sum(distances) / len(distances)
        distances_min[prediction_key] = min(distances)

    # print(f"[DEBUG] All predictions for all factors: {possible_keys}")

    distances_mean = dict(sorted(distances_mean.items(), key=lambda item: item[1], reverse=True))
    distances_min = dict(sorted(distances_min.items(), key=lambda item: item[1]))
    
    # Mean value of Euclid distance of shifts in key | Euclid distances for all keys
    print(f"\nMethod 1: mean value of Euclid distance of shifts in key: {distances_mean}")
    print(f"\nMethod 2: min value of Euclid distance of shifts in key: {distances_min}\n")

    # также удаляет строки с повторяющимся паттерном подстрок
    final_predictions = []
    print(f"[DEBUG] The actual used key (l - {len(secret_key)}) is '{secret_key}'\n")
    print(f"Predictions with weights:")
    for key, value in distances_mean.items():
        print(f"'{key}' : {round(value, 4)}")
        final_predictions.append(key)

    prediction_result = False
    # применяем дешифрование шифртекста для каждого предсказанного ключа
    for key in final_predictions:
        print(f"\nFor '{key}' key the original text would look like:")
        final_text = encrypt(cipher_text, key, decode=True)
        if final_text == content:
            prediction_result = True
        print(f"{final_text[:64]}...")

    if prediction_result:
        print(f"\nKey is '{secret_key}' (l - {len(secret_key)})")
    if not prediction_result:
        print(
            f"\nAccurate keystring was not found, the best prediction is '{max(final_predictions, key=len)}' (l - {len(secret_key)})"
        )

    sys.stdout = orig_stdout
    f.close()
