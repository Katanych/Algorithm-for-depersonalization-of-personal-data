import os
import cv2
import re
from pytesseract import pytesseract, Output
from copy import deepcopy
from numpy import pi, copy
from .file_processing import *
from .table_processing import *
# from file_processing import *
# from table_processing import *
from pathlib import Path
from spacy import load

NLP_EN = load("en_core_web_sm")


def anonym_imgs(imgs_paths, pytesseract_exe_file_path, oper_sys="Windows", quality=220):
    '''Функция возвращает список ссылок на обработанные изображения.
    
    Функция принимает на вход список ссылок на изображения,
    находит персональные данные согласно паттернам, блюрит.
    Также в качестве параметра функции передается путь до
    исполнительного файла tesseract.
    
    '''

    # Подключаем тессеракт
    pytesseract.tesseract_cmd = pytesseract_exe_file_path 

    # Создаем директорию, куда будем складывать деперсонализированные изображения
    new_path = Path(imgs_paths[0])
    path = new_path.parent / "blur"
    if not path.is_dir():                                
        path.mkdir()

    # Переменная для складирования результатов
    path_end = []
    # Работаем отдельно с каждым изображением
    for img_path in imgs_paths:
        img = anonym_img(img_path)
        # сохраняем каждое изображение в директорию blur
        end_path = path / f"{img_path.stem}_blur.jpg"
        cv2.imwrite(f"{end_path}", img) 
        path_end.append(end_path)

    return path_end


def anonym_img(img_path):
    '''Функция возвращает деперсонализированное изображения'''

    # считываем изображение с помощью cv2
    img = cv2.imread(f"{img_path}")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    adaptive_threshold = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, \
        cv2.THRESH_BINARY, 81, 71)
    
    # задаем режим распознования текста
    config = "--psm 1"
    
    # преобразуем изображение в текстовый массив
    img_data = pytesseract.image_to_data(adaptive_threshold, output_type=Output.DICT, lang="rus", config=config)
    # print(img_data)
    
    vertical_lines = numbers_lines(is_table(img)[1], img)[0]
    vertical_lines = overlapping_filter(vertical_lines, 0)
    if len(vertical_lines) > 7 and len(vertical_lines) < 12: #and len(vertical_lines) < 10:   # а пока больше позволить мы себе не можем
        return blur_table(img, config)                         # блюрим табличные данные
    else:                                                      # иначе
        return blur_words(img, img_data)                       # находим и блюрим персональные данные


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
        
        file = File(file_dict["saved_path"], poppler_path, 230)
        if file.file_path.suffix == ".pdf":
            print("> PDF конвертируется в изображения...")
            img_path = file.pdf_to_imgs()
            print("> [OK] Готово")
        elif file.file_path.suffix in [".docx", ".xlsx", ".doc", ".jpg", ".rtf", ".png"]:
            print("> DOCX конвертируется в изображения...")
            if file.file_path.suffix == ".xlsx":
                file.quality = 600
            img_path = file.file_to_imgs()
        else:
            print("> [ERROR] Неправильный формат файла")
            file_dict["parsed_path"] = None
            return

        # запускаем функцию деперсонализации получаем ссылки на получившиеся изображения
        print("> Деперсонализация тессерактом...")
        anonym_img_path = anonym_imgs(img_path, pytesseract_exe_file_path, oper_sys)
        print("> [OK] Деперсонализация тессерактом завершена")
        file.file_path = anonym_img_path

        print("> Конвертирование в PDF...")
        parsed_pdf_path = file.imgs_to_pdf()
        print("> [OK] Конвертирование в PDF завершено")

        all_parsed_paths.append(parsed_pdf_path)

    file.file_path = all_parsed_paths
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
            'path': file.pdf_to_zip()
        }

    return (files_dicts, zip_dict)

def anonym_list_files(files_paths, poppler_path, pytesseract_exe_file_path, oper_sys="Windows"):
    ''' Функция возвращает список путей до результата работы'''

    # Это для меня
    end_path = []
    for file_path in files_paths:
        file = File(file_path, poppler_path, 240)
        if file.file_path.suffix == ".pdf":
            imgs_paths = file.pdf_to_imgs()
        elif file.file_path.suffix in [".docx", ".xlsx", ".doc", ".rtf", ".jpg", ".png"]:
            if file.file_path.suffix == ".xlsx":
                file.quality = 600
            imgs_paths = file.file_to_imgs()
        else:
            print("Exception! Йоу, не те файлы подгружаешь, мальчик")

        # запускаем функцию деперсонализации получаем ссылки на получившиеся изображения
        paths = anonym_imgs(imgs_paths, pytesseract_exe_file_path, oper_sys)
        file.file_path = paths
        end_path.append(file.imgs_to_pdf())
    file.file_path = end_path
    end_path.append(file.pdf_to_zip())

    return end_path

