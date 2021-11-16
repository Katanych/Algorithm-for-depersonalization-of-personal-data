import os
import img2pdf
import zipfile
import time
from pdf2image import convert_from_path
from subprocess import  Popen
# from main import PYTESSERACT_EXE_FILE_PATH, POPPLER_PATH, OPER_SYS, LIBRE_OFFICE
# from .settings import PYTESSERACT_EXE_FILE_PATH, POPPLER_PATH, OPER_SYS, LIBRE_OFFICE
from pathlib import Path, WindowsPath


# PYTESSERACT_EXE_FILE_PATH = "C:\\Users\\k4t4n\\Desktop\\hack\\tes\\tesseract.exe"  			             # Путь до tesseract
LIBRE_OFFICE = "C:\\Program Files\\LibreOffice\\program\\soffice.exe"					                 # Путь до LibreOffice
# POPPLER_PATH = "C:\\Program Files\\poppler\\bin"							                             # Путь до Poppler
# FILES_PATHS = ["C:\\Users\\k4t4n\\Desktop\\test10\\13.rtf", "C:\\Users\\k4t4n\\Desktop\\test10\\14.pdf"] # Константа списка файлов
# OPER_SYS = "Windows" 											                                         # Операционная система

class File:
    '''Класс файла, представленного к конвертации'''
    def __init__(self, file_path, poppler_path, quality=240):
        '''Конструктор, инициализирующий основные свойства класса'''
        if isinstance(file_path, str):
            self.file_path = Path(file_path)
        elif isinstance(file_path, WindowsPath):
            self.file_path = file_path
        else:
            print("Exception! Переданы неправильные данные")
        self.poppler_path = poppler_path
        self.quality = quality
        self.result_files = None

    def pdf_to_imgs(self):
        '''Метод возвращает список имен путей изображений, преобразованных из pdf'''

        imgs = convert_from_path(self.file_path, dpi=self.quality, poppler_path=self.poppler_path)

        path = self.file_path.parent / self.file_path.stem
        if not path.is_dir():
            path.mkdir()

        imgs_paths = []
        for img in imgs:
            img_path = path / f"{path.stem}_{imgs.index(img)}.jpg"
            imgs_paths.append(img_path)
            print("> [OK] Создано изображение:", imgs_paths[-1])
            img.save(imgs_paths[-1])
        self.file_path = imgs_paths
        return self.file_path

    def file_to_imgs(self):
        '''Метод возвращается ссылки на сконвертированные изображения из любых форматов'''

        path = self.file_path.parent / f"{self.file_path.stem}.pdf"
        p = Popen([LIBRE_OFFICE, '--headless', '--convert-to', 'pdf', '--outdir', \
            self.file_path.parent.__str__(), self.file_path.__str__()])
        p.communicate()
        self.file_path = path
        return self.pdf_to_imgs()

    def imgs_to_pdf(self):
        '''Метод соирает изображения в pdf'''
        path = self.file_path[0].parent.parent.parent / f"{self.file_path[0].parent.parent.stem}_blur.pdf"
        print("PATH:", path)

        for i, file_path in enumerate(self.file_path):
            self.file_path[i] = file_path.__str__()
        with open(path,"wb") as f:
            f.write(img2pdf.convert(self.file_path))

        print("> [OK] Создан файл: ", path)
        self.file_path = path.__str__()
        return self.file_path
    
    def pdf_to_zip(self):
        '''Метод конвертирует из pdf в zip'''
        filename = 'blurs_' + str(round(time.time() * 1000)) + '.zip'
        file = Path(self.file_path[0])
        full_path = file.parent / filename

        # for i, file_path in enumerate(files_paths):
        #     files_paths[i] = file_path.__str__()

        with zipfile.ZipFile(full_path.__str__(), 'w') as myzip:
            for file_path in self.file_path:
                # file = parse_file_path(file_path, oper_sys)
                file_path = Path(file_path)
                arc_name = file_path.stem.__str__() + file_path.suffix.__str__()
                myzip.write(file_path.__str__(), \
                    arcname=arc_name)
                print("> [OK] Создан архив: ", full_path)
        return 'static/' + filename

# def pdf_to_imgs(file_path, poppler_path=None, oper_sys=OPER_SYS, quality=240):
#     '''Функция возвращает список имен путей изображений, преобразованных из pdf.

#     Функиция преобразует pdf в изображения и 
#     сохраняет. 
    
#     '''
    
#     imgs = convert_from_path(file_path, dpi=quality, poppler_path=poppler_path)
    
#     imgs_paths = []
#     path = file_path.parent / file_path.stem

#     if not path.is_dir():
#         path.mkdir()

#     for img in imgs:
#         img_path = path / f"{path.stem}_{imgs.index(img)}.jpg"
#         imgs_paths.append(img_path)
#         print("> [OK] Создано изображение:", imgs_paths[-1])
#         img.save(imgs_paths[-1])
    
#     return imgs_paths

# def file_to_imgs(file_path, poppler_path=POPPLER_PATH, oper_sys=OPER_SYS, quality=230):
#     file = Path(file_path)
#     path = file.parent / f"{file.stem}.pdf"
#     p = Popen([LIBRE_OFFICE, '--headless', '--convert-to', 'pdf', '--outdir', \
#         file.parent.__str__(), file_path.__str__()])
#     p.communicate()
#     print(path)

#     return pdf_to_imgs(path, poppler_path, oper_sys, quality=240)

# def imgs_to_pdf(files_paths, oper_sys=OPER_SYS):
#     path = files_paths[0].parent.parent.parent / f"{files_paths[0].parent.parent.stem}_blur.pdf"
#     print("PATH:", path)

#     for i, file_path in enumerate(files_paths):
#         files_paths[i] = file_path.__str__()
#     with open(path,"wb") as f:
# 	    f.write(img2pdf.convert(files_paths))

#     print("> [OK] Создан файл: ", path)
#     return path.__str__()

# def pdf_to_zip(files_paths, oper_sys=OPER_SYS):
#     # file = parse_file_path(files_paths[0], oper_sys)
#     # slash = line(oper_sys)

#     file = Path(files_paths[0])

#     filename = 'blurs_' + str(round(time.time() * 1000)) + '.zip'
#     full_path = file.parent / filename

#     # for i, file_path in enumerate(files_paths):
#     #     files_paths[i] = file_path.__str__()

#     with zipfile.ZipFile(full_path.__str__(), 'w') as myzip:
#         for file_path in files_paths:
#             # file = parse_file_path(file_path, oper_sys)
#             file_path = Path(file_path)
#             arc_name = file_path.stem.__str__() + file_path.suffix.__str__()
#             myzip.write(file_path.__str__(), \
#                 arcname=arc_name)
#             print("> [OK] Создан архив: ", full_path)
#     return 'static/' + filename
