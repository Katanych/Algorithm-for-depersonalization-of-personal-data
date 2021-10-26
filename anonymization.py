import os
import cv2
import re
from .file_processing import *
from pytesseract import pytesseract, Output
from copy import deepcopy
from numpy import pi, copy
from .settings import PYTESSERACT_EXE_FILE_PATH, POPPLER_PATH, OPER_SYS


patterns = dict(
    starts_with_initials = "r'^([А-ЯЁ]{1}\.[А-ЯЁ]{1}\.[А-ЯЁ]{1})\w+'",         # Если слово начинается с инициалов. Пример: И.В.Иванов
    only_initials = "r'^([А-ЯЁ]{1}\.\s*[А-ЯЁ]{1}\.\w*\w*\w*)'",                # Если обнаружены только инициалы с возможным пробелом между и до трех символов после. Пример: И. И.); или И.В.
    patronymic = "r'^([А-ЯЁ]{1})\w+((вич)|(вна))$'",                           # Если найдено отчество в именительном падеже
    capital_letter = "r'^([А-ЯЁ]{1})\w+'",                                     # Если найдена заглавная буква
    one_initial = "r'^([А-ЯЁ]{1}\.\w*)'",
    v_and_d_padechi = "r'^[А-ЯЁ]{1}\w+(((вну)|(вичу)|(вича)|(вне))(.?))$'",          # Если отчество в Винительном или Дательном падеже
    quote = "r'[\"]'"
)

blask_list = [
    "им.",
    "имени",
    "Союза",
]

def is_table(img):
    '''Функция возвращает колличество обнаруженных линий'''

    canny = cv2.Canny(img, 50, 150)
    rho = 1
    theta = rho * pi / 180
    threshold = 50
    minLinLength = 350
    maxLineGap = 6
    linesP = cv2.HoughLinesP(canny, rho, theta, threshold, None, minLinLength, maxLineGap)
    #cv2.imwrite("C:\\Users\\k4t4n\\Desktop\\test1\\1_vlad.jpg", linesP) 
    if linesP is None:
        linesP = []
    return len(linesP), linesP

def is_vertical(line):
    '''Функция осуществляет проверку на вертикальность'''

    return line[0] == line[2]

def is_horizontal(line):
    '''Функция осуществляет проверку на горизонтальность'''

    return line[1] == line[3]

def numbers_lines(linesP, cImage):
    '''Функция классифицирует линии на горизонтальные и вертикальные'''

    if linesP is not None:
        vertical_lines = []
        horizontal_lines = []
        for i in range(0, len(linesP)):
            l = linesP[i][0]
            if (is_vertical(l)):
                l[1] = 0
                l[3] = cImage.shape[0]
                vertical_lines.append(l)
            elif (is_horizontal(l)):
                l[0] = 0
                l[2] = cImage.shape[1]
                horizontal_lines.append(l)
    
    return vertical_lines, horizontal_lines

def overlapping_filter(lines, sorting_index):
    '''Функция фильтра прерывания линий'''

    filtered_lines = []
    
    lines = sorted(lines, key=lambda lines: lines[sorting_index])
    
    for i in range(len(lines)):
            l_curr = lines[i]
            if(i>0):
                l_prev = lines[i-1]
                if ( (l_curr[sorting_index] - l_prev[sorting_index]) > 5):
                    filtered_lines.append(l_curr)
            else:
                filtered_lines.append(l_curr)
    return filtered_lines

def get_cropped_image(image, x, y, w, h):
    '''Функция возвращает обрезанное изображение'''

    return image[y:y+h, x:x+w]

def get_ROI(image, horizontal, vertical, left_line_index, right_line_index, top_line_index, bottom_line_index, offset=4):
    '''Функция обрезает изображенияи возвращает координаты обреза'''

    x1 = vertical[left_line_index][2] + offset
    y1 = horizontal[top_line_index][3] + offset
    x2 = vertical[right_line_index][2] - offset
    y2 = horizontal[bottom_line_index][3] - offset

    w = x2 - x1
    h = y2 - y1
    
    cropped_image = get_cropped_image(image, x1, y1, w, h)
    
    return cropped_image, (x1, y1, w, h)

def blur_word(img, word_coords):
    '''Функция блюрит изображение по заданным координатам'''

    x, y, w, h = word_coords[0], word_coords[1], word_coords[2], word_coords[3]
    if x + y + w + h > 0:
        img[y:y+h, x:x+w] = cv2.blur(img[y:y+h, x:x+w], (100, 100))
    
def anonym_imgs(imgs_paths, pytesseract_exe_file_path, oper_sys="Windows", quality=220):
    '''Функция возвращает список ссылок на обработанные изображения.
    
    Функция принимает на вход список ссылок на изображения,
    находит персональные данные согласно паттернам, блюрит.
    Также в качестве параметра функции передается путь до
    исполнительного файла tesseract.
    
    '''

    # Подключаем тессеракт
    pytesseract.tesseract_cmd = pytesseract_exe_file_path 

    # разбиваем путь к файлу на сегменты
    file = parse_file_path(imgs_paths[0], oper_sys)

    # определяем слэш, исходя из ОС
    slash = line(oper_sys)

    # Создаем директорию, куда будем складывать деперсонализированные изображения
    path = file["root"] + slash + "blur"
    if not os.path.isdir(path):                                
        os.mkdir(path)

    # Переменная для складирования результатов
    path_end = []

    # Работаем отдельно с каждым изображением
    for img_path in imgs_paths:
        img = anonym_img(img_path)
        # сохраняем каждое изображение в директорию blur
        file = parse_file_path(img_path, oper_sys)
        cv2.imwrite(path + slash + file["name"] + "_blur.jpg", img) 
        path_end.append(path + slash + file["name"] + "_blur.jpg")

    return path_end

def blur_table(img, config):
    cImage =  copy(img)
    img_lines = is_table(img)[1]
    vertical_lines, horizontal_lines = numbers_lines(img_lines, img)
    horizontal_lines = overlapping_filter(horizontal_lines, 1)
    vertical_lines = overlapping_filter(vertical_lines, 0)

    for i, line in enumerate(horizontal_lines):
        cv2.line(cImage, (line[0], line[1]), (line[2], line[3]), (0, 255, 0), 3, cv2.LINE_AA)
    for i, line in enumerate(vertical_lines):
        cv2.line(cImage, (line[0], line[1]), (line[2], line[3]), (0, 0, 255), 3, cv2.LINE_AA)

    for e in range(len(vertical_lines)-1):
        for r in range(len(horizontal_lines)-1):
            crop_img, (x, y, w, h) = get_ROI(cImage, horizontal_lines, vertical_lines, e, e+1, r, r+1)
            if len(crop_img) > 0:
                image_data = pytesseract.image_to_data(crop_img, output_type=Output.DICT, lang="rus", config=config)
                # обнуляем рабочие переменные областей размытия
                blur_words(img, image_data, x, y, w, h)
    return img

def anonym_img(img_path):
    # считываем изображение с помощью cv2
    img = cv2.imread(img_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    adaptive_threshold = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, \
        cv2.THRESH_BINARY, 81, 71)
    
    # задаем режим распознования текста
    config = "--psm 1"

    # преобразуем изображение в текстовый массив
    img_data = pytesseract.image_to_data(adaptive_threshold, output_type=Output.DICT, lang="rus", config=config)
    
    vertical_lines = numbers_lines(is_table(img)[1], img)[0]
    vertical_lines = overlapping_filter(vertical_lines, 0)
    if len(vertical_lines) > 7 and len(vertical_lines) < 10:   # а пока больше позволить мы себе не можем
        return blur_table(img, config)                # блюрим табличные данные
    else:                                             # иначе
        return blur_words(img, img_data)              # находим и блюрим персональные данные

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

def after_word(word, img_data):
    '''Следующее слово'''
    if img_data['text'].index(word) == len(img_data['text'])-1:
        return ""
    i = 1
    while len(img_data['text'][img_data['text'].index(word) + i]) < 2:
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
                blur_without_queue = False
                continue

            # если слово состоит из более чем четырех символов
            if len(word) >= 4:
                if word_satisfies_pattern(word, 'starts_with_initials'):
                    blur_word(img, word_coords[0])
                # если слово состоит только из инициалов, то блюрим либо предыдущее слово, либо следующее (если в нем нет ковычки),
                elif word_satisfies_pattern(word, 'only_initials'):
                    next_word = after_word(word, img_data)
                    if word_satisfies_pattern(next_word, 'capital_letter') and word_satisfies_pattern(next_word, 'quote') == 0 and word2 not in blask_list \
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
                    elif word_satisfies_pattern(word2, 'capital_letter') and word_satisfies_pattern(next_word, 'quote') == 0 and word2 not in blask_list:
                        blur_word(img, word_coords[0])
                        #print(word_coords[0], word_coords[1])
                        blur_word(img, word_coords[1])
                    #print("2: ", word, word2)
                elif (word_satisfies_pattern(word, 'v_and_d_padechi') or word_satisfies_pattern(word, 'patronymic')) \
                    and word_satisfies_pattern(word2, 'capital_letter'):
                    word3 = early_word(word2, img_data)
                    blur_word(img, word_coords[0])
                    blur_word(img, word_coords[1])
                    if word_satisfies_pattern(word3, 'capital_letter') \
                        and word_coords[1][1] - 10 < word_coords[2][1]: # если фамилия не стала чуть выше
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
                    #print("4: ", word, word2, word3)
            elif len(word) == 2 and len(word2) == 2:
                if word_satisfies_pattern(word, 'one_initial') and word_satisfies_pattern(word2, 'one_initial'):
                    next_word = after_word(word, img_data)
                    back_word = early_word(word2, img_data)
                    if word_satisfies_pattern(next_word, 'quote') == 0 and back_word not in blask_list:
                        blur_word(img, word_coords[0])
                        blur_word(img, word_coords[1])
                        #print("5: ", word, word2)
                        blur_without_queue = True     
            
            # храним историю двух предыдущих слов
            word_coords[2] = deepcopy(word_coords[1])
            word_coords[1] = deepcopy(word_coords[0])
            word2 = word
            # print(word2)
    return img

def anonym_dict_files(files_dicts, poppler_path, pytesseract_exe_file_path, oper_sys="Windows"):
    ''' Функция возвращает массив всех файлов-словарей и словарь архива
    
    Функция принимает массив словарей файлов, которые содержат пути до хохнанненых в /storage файлов
    Она обрабатывает каждый файл-словарь, записывая в его свойство 'parsed_path' путь до обработанной pdf
    В конце она собирает также zip из обработанных файлов/
    
    '''

    # Вспомогательный массив, в который будут падать ссылки на все обработанные файлы
    # Мы используем его, чтобы быстро передать список для архивации в zip
    all_parsed_paths = []

    for file_dict in files_dicts:
        print("> Идёт обработка файла " + file_dict['title'] + "...")
        # Для не загруженных файлов мы ничего не обрабатываем
        if file_dict["success"] is False:
            print("> Файл " + file_dict['title'] + " не нуждается в обработке")
            continue
    
        file = parse_file_path(file_dict["saved_path"], oper_sys)                                      # разбиваем путь к файлу на сегменты
        if file['format'] == "pdf":
            print("> PDF конвертируется в изображения...")                                                      # если на вход подали pdf файл
            img_path = pdf_to_imgs(file['path'], poppler_path, oper_sys)
            print("> [OK] Готово")               # то получаем список путей до изображений, полученных при конвертации из pdf
        elif file['format'] == "docx":                                                   # если на вход подали docx файл
            print("> DOCX конвертируется в изображения...")
            img_path = docx_to_imgs(file['path'], poppler_path, oper_sys)              # то получаем список путей до изображений, полученных при конвертации из doc
        elif file['format'] == "xlsx":
            print("> XLSX конвертируется в изображения...")
            img_path = xlsx_to_imgs(file['path'], poppler_path, oper_sys, quality=300) # то получаем список путей до изображений, полученных при конвертации из doc
            print("> [OK] Готово")
        elif file['format'] == "doc":
            print("> DOC конвертируется в изображения...")
            img_path = doc_to_imgs(file['path'], poppler_path, oper_sys, quality=300) # то получаем список путей до изображений, полученных при конвертации из doc
            print("> [OK] Готово")
        elif file['format'] == "rtf":
            print("> rtf конвертируется в изображения...")
            imgs_paths = rtf_to_imgs(file['path'], poppler_path, oper_sys, quality=240) # то получаем список путей до изображений, полученных при конвертации из doc
            print("> [OK] Готово")
        else:
            print("> [ERROR] Неправильный формат файла")
            file_dict["parsed_path"] = None
            return

        # запускаем функцию деперсонализации получаем ссылки на получившиеся изображения
        print("> Деперсонализация тессерактом...")
        anonym_img_path = anonym_imgs(img_path, pytesseract_exe_file_path, oper_sys)
        print("> [OK] Деперсонализация тессерактом завершена")

        print("> Конвертирование в PDF...")
        parsed_pdf_path = imgs_to_pdf(anonym_img_path, oper_sys)
        # file_dict["parsed_path"] = parsed_pdf_path
        print("> [OK] Конвертирование в PDF завершено")

        all_parsed_paths.append(parsed_pdf_path)

    print("> [OK] Работа с файлами завершена")

    print("> Создание архива...")
    if len(all_parsed_paths) < 1:
        zip_dict = {
            'type': 'zip',
            'success': False,
            'path': None
        }
    else:
        zip_dict = {
            'type': 'zip',
            'success': True,
            'path': pdf_to_zip(all_parsed_paths, oper_sys)
        }

    return (files_dicts, zip_dict)

def anonym_list_files(files_paths, poppler_path, pytesseract_exe_file_path, oper_sys="Windows"):
    ''' Функция возвращает список путей до результата работы'''

    # Это для меня
    end_path = []
    for file_path in files_paths:
        file = parse_file_path(file_path, oper_sys)                                      # разбиваем путь к файлу на сегменты
        if file['format'] == "pdf":                                                      # если на вход подали pdf файл
            imgs_paths = pdf_to_imgs(file['path'], poppler_path, oper_sys)               # то получаем список путей до изображений, полученных при конвертации из pdf
        elif file['format'] == "docx":                                                   # если на вход подали docx файл
            imgs_paths = docx_to_imgs(file['path'], poppler_path, oper_sys)              # то получаем список путей до изображений, полученных при конвертации из doc
        elif file['format'] == "xlsx":
            imgs_paths = xlsx_to_imgs(file['path'], poppler_path, oper_sys, quality=240) # то получаем список путей до изображений, полученных при конвертации из xlsx
        elif file['format'] == "doc":
            imgs_paths = doc_to_imgs(file['path'], poppler_path, oper_sys, quality=240) # то получаем список путей до изображений, полученных при конвертации из doc
        elif file['format'] == "rtf":
            imgs_paths = rtf_to_imgs(file['path'], poppler_path, oper_sys, quality=240) # то получаем список путей до изображений, полученных при конвертации из doc
        else:
            print("Йоу, не те файлы подгружаешь, мальчик")

        # запускаем функцию деперсонализации получаем ссылки на получившиеся изображения
        paths = anonym_imgs(imgs_paths, pytesseract_exe_file_path, oper_sys)
        end_path.append(imgs_to_pdf(paths, oper_sys))
    end_path.append(pdf_to_zip(end_path, oper_sys))

    return end_path

