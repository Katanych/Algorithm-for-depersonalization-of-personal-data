from copy import deepcopy
from pytesseract import pytesseract, Output
import cv2
import re


patterns = dict(
    starts_with_initials = "r'^([А-ЯЁ]{1}\.[А-ЯЁ]{1}\.[А-ЯЁ]{1})\w+'",         # Если слово начинается с инициалов. Пример: И.В.Иванов
    only_initials = "r'^([А-ЯЁ]{1}\.\s*[А-ЯЁ]{1}\.\w*\w*\w*)'",                # Если обнаружены только инициалы с возможным пробелом между и до трех символов после. Пример: И. И.); или И.В.
    patronymic = "r'^([А-ЯЁ]{1})\w+((вич)|(вна))$'",                           # Если найдено отчество в именительном падеже
    capital_letter = "r'^([А-ЯЁ]{1})\w+'",                                     # Если найдена заглавная буква
    one_initial = "r'^([А-ЯЁ]{1}\.\w*)'",
    v_and_d_padechi = "r'^[А-ЯЁ]{1}\w+(((вну)|(вичу)|(вича)|(вне))(.?))$'",          # Если отчество в Винительном или Дательном падеже
    quote = "r'[\"]'"
)

black_list = [
    "им.",
    "имени",
    "Союза",
    "Собянин",
]

def blur_word(img, word_coords):
    '''Функция блюрит изображение по заданным координатам'''

    x, y, w, h = word_coords[0], word_coords[1], word_coords[2], word_coords[3]
    if x + y + w + h > 0:
        img[y:y+h, x:x+w] = cv2.blur(img[y:y+h, x:x+w], (100, 100))
        #img[y:y+h, x:x+w] = cv2.bitwise_not(img[y:y+h, x:x+w])


def word_satisfies_pattern(word, pattern):
    '''Проверка соответствия слова паттерну'''
    return len(re.findall(eval(patterns[pattern]), word))

def early_word(word, img_data):
    '''Предыдущее слово'''
    if img_data['text'].index(word) - 1 == 0:
        return ""
    i = 1
    while len(img_data['text'][img_data['text'].index(word) - i]) < 2:
        i += 1
        if img_data['text'].index(img_data['text'][img_data['text'].index(word) - i]) == 0:
            return ""
    return img_data['text'][img_data['text'].index(word) - i]

def early_is_not_none(word, img_data):
    if img_data['text'].index(word) - 1 == 0:
        return ""
    i = 1
    while len(img_data['text'][img_data['text'].index(word)-i]) == "":
        i += 1
        if img_data['text'].index(img_data['text'][img_data['text'].index(word) - i]) == 0:
            return ""

    return img_data['text'][img_data['text'].index(word)-i]
    
def after_word(word, img_data):
    '''Следующее слово'''
    if img_data['text'].index(word) == len(img_data['text'])-1:
        return ""
    i = 1
    #print(img_data['text'][155], " ????")

    while len(img_data['text'][img_data['text'].index(word) + i]) < 2 and img_data['text'].index(word) + i != len(img_data['text'])-1:
        i += 1
        if img_data['text'].index((img_data['text'][img_data['text'].index(word) + i])) == len(img_data['text'])-1:
            return ""

    return img_data['text'][img_data['text'].index(word) + i]

def blur_words(img, img_data, x=0, y=0, w=0, h=0):
    # обнуляем рабочие переменные областей размытия
    word_coords = [
        (x, y, w, h),
        (0, 0, 0, 0),
        (0, 0, 0, 0)
    ]
    
    if sum(word_coords[0]) > 0:
        flag = True
    else:
        flag = False

    # исследуемое слово и предыдущее
    word = "00"
    word2 = "00" 

    blur_without_queue = False # блюрим без очереди
    counter = 0 # Количество блюра без очереди

    # проходим по каждому слову
    for i, word in enumerate(img_data['text']):
        # если это не пустое слово или один символ
        if len(word) > 1:
            # определяем границы слова
            if flag:
                word_coords[0] = (x, y, w, h)
            else: 
                word_coords[0] = img_data['left'][i], img_data['top'][i], img_data['width'][i], img_data['height'][i]

            # Если есть команда заблюрить слово вне очереди, то блюрим и переходим к следующему слову
            if blur_without_queue:
                blur_word(img, word_coords[0])
                if counter == 0:
                    blur_without_queue = False
                else:
                    counter -= 1
                continue

            # если слово состоит из более чем четырех символов
            if len(word) >= 4:
                if word_satisfies_pattern(word, 'starts_with_initials'):
                    if word[4:] not in black_list:
                        blur_word(img, word_coords[0])
                # если слово состоит только из инициалов, то блюрим либо предыдущее слово, либо следующее (если в нем нет ковычки),
                elif word_satisfies_pattern(word, 'only_initials'):
                    next_word = after_word(word, img_data)
                    print("NEXT:", next_word)
                    if word_satisfies_pattern(next_word, 'capital_letter') and word_satisfies_pattern(next_word, 'quote') == 0 and (word2 and word and next_word) not in black_list \
                        and abs(word_coords[0][1] - img_data['top'][i+1]) < 50 and word[-1] != ',' and not (word[-1] == '.' and word[-2] == '.') \
                            and img_data['text'][img_data['text'].index(word) + 1] != ',':
                        # в этом условии говорится, что если следующее слово с заглавное буквы, при этом в нем нет кавычки, 
                        # предыдущее слово не в черном списке, а также не где-то снизу, и не имеет в конце запятой, то:
                        if flag:
                            word_coords[1] = (x, y, w, h)
                        else: 
                            word_coords[1] = img_data['left'][i+1], img_data['top'][i+1], img_data['width'][i+1], img_data['height'][i+1]
                        blur_word(img, word_coords[0])
                        blur_word(img, word_coords[1])
                    elif (word_satisfies_pattern(word2, 'capital_letter') or re.findall(r'[А-ЯЁ]', word2[1])) and word_satisfies_pattern(next_word, 'quote') == 0 and (word2 and word and next_word) not in black_list:
                        blur_word(img, word_coords[0])
                        blur_word(img, word_coords[1])
                    print("2: ", word, word2)
                elif (word_satisfies_pattern(word, 'v_and_d_padechi') or word_satisfies_pattern(word, 'patronymic')) \
                    and word_satisfies_pattern(word2, 'capital_letter'):
                    word3 = early_word(word2, img_data)

                    blur_word(img, word_coords[0])
                    blur_word(img, word_coords[1])
                    #print("WORD3:", word3, "T/F:", word_satisfies_pattern(word3, 'capital_letter'), "coords[1]:", word_coords[1][1] - 40, "coords[2]:", word_coords[2][1])
                    if (word_satisfies_pattern(word3, 'capital_letter') or word_satisfies_pattern(word3[1:], 'capital_letter') or word3[-2:] in ["ов", "ин", "ая", "ик"]) \
                        and (word_coords[1][1] - 20 < word_coords[2][1] or word_coords[2][0] + 30 < word_coords[1][0]): # ? or (word_coords[1][0] - 30 < word_coords[2][0] ): # если фамилия не стала чуть выше БЫЛО ДЕСЯТЬ
                        #print("WORD3:", word3)
                        blur_word(img, word_coords[2])
                    else:
                        if flag:
                            word_coords[2] = (x, y, w, h)
                        else: 
                            x2 = word_coords[1][0]
                            y2 = word_coords[1][1]
                            h = word_coords[0][3]
                            w2 = word_coords[1][2]
                            w = word_coords[0][2]
                            word_coords[2] = (x2, y2-h-25, w2+w+15, h+20)
                        blur_word(img, word_coords[2])
                    print("4: ", word, word2, word3)
            elif len(word) == 2 and len(word2) == 2:
                if word_satisfies_pattern(word, 'one_initial') and word_satisfies_pattern(word2, 'one_initial'):
                    next_word = after_word(word, img_data)
                    back_word = early_word(word2, img_data)
                    if word_satisfies_pattern(next_word, 'quote') == 0 and (back_word and next_word) not in black_list and img_data['text'][i+1] not in black_list:
                        blur_word(img, word_coords[0])
                        blur_word(img, word_coords[1])
                        print("5: ", word, word2)
                        blur_without_queue = True     
            
            # храним историю двух предыдущих слов
            word_coords[2] = deepcopy(word_coords[1])
            word_coords[1] = deepcopy(word_coords[0])
            word2 = word
            # print(word2)
        # ТЕПЕРЬ ИЩЕМ ТЕЛЕФОНЫ
        if len(word) > 0:
            if word[0] in ["7", "8", "+"]: # or (word[0] == "+" and word[1] == "7"):
                # определяем границы слова
                if flag:
                    word_coords[0] = (x, y, w, h)
                else: 
                    word_coords[0] = img_data['left'][i], img_data['top'][i], img_data['width'][i], img_data['height'][i]

                if len(word) > 2:
                    if len(word) >= 11 and word[-2].isdigit():
                        blur_word(img, word_coords[0])
                        print("6:", word)
                    else:
                        if after_word(word, img_data).isdigit() \
                            and after_word(after_word(word, img_data), img_data).isdigit():
                            blur_word(img, word_coords[0])
                            print("7:", word)
                            counter = 2
                            blur_without_queue = True
                else:
                    if len(img_data['text']) > i+3:
                        #print("LEN:", len(img_data['text']), "I:", i+3)
                        if img_data['text'][i+3].isdigit():
                            if len(img_data['text'][i+3]) == 2:
                                counter = 3
                            elif len(img_data['text'][i+3]) == 4:
                                counter = 2
                            print("8:", word)
                            blur_word(img, word_coords[0])
                            blur_without_queue = True
        # НУ А ТЕПЕРЬ ИЩЕМ ДАТЫ
        if len(word) > 2:
            if word in ["января", "февраля", "марта", "апреля", "мая", "июня", "июля", \
                "августа", "сентября", "октября", "ноября", "декабря"] and after_word(word, img_data).isdigit() \
                    and early_is_not_none(word, img_data).isdigit():
                counter = 0
                blur_without_queue = True
                blur_word(img, word_coords[0])
                word_coords[1] = img_data['left'][i-1], img_data['top'][i-1], img_data['width'][i-1], img_data['height'][i-1]
                blur_word(img, word_coords[1])
                print("11:", word)
            elif len(re.findall(r'^(\d\d\.\d\d\.\d)', word)) > 0 or len(re.findall(r'(\.\d\d\.\d\d)$', word)):
                blur_word(img, word_coords[0])
                print("10:", word)
        # НУ А ТЕПЕРЬ ЕЩЕ СЕРИЮ И НОМЕР В ВАРИАЦИИ XXXX XXXXXX
        if len(word) > 3:
            if len(re.findall(r'^(\d\d\d\d)$', word)) and len(re.findall(r'^(\d\d\d\d\d\d)$', after_word(word, img_data))):
                word_coords[1] = img_data['left'][i+1], img_data['top'][i+1], img_data['width'][i+1], img_data['height'][i+1]
                blur_word(img, word_coords[0])
                blur_word(img, word_coords[1])
            elif len(re.findall(r'^(\d\d\d\d)$', word)) and after_word(word, img_data) == "номер":
                word_coords[1] = img_data['left'][i+2], img_data['top'][i+2], img_data['width'][i+2], img_data['height'][i+2]
                blur_word(img, word_coords[0])
                blur_word(img, word_coords[1])
            elif len(re.findall(r'^(\d\d\d\d\d\d\d\d\d\d)$', word)) or len(re.findall(r'^(\d\d\d\d№\d\d\d\d\d\d)$', word)):
                blur_word(img, word_coords[0])



                
                

    return img