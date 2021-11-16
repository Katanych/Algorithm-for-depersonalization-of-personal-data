import os
import img2pdf
import zipfile
import time
from pdf2image import convert_from_path
from subprocess import  Popen
# from main import PYTESSERACT_EXE_FILE_PATH, POPPLER_PATH, OPER_SYS, LIBRE_OFFICE
# from .settings import PYTESSERACT_EXE_FILE_PATH, POPPLER_PATH, OPER_SYS, LIBRE_OFFICE
from pathlib import Path, WindowsPath

LIBRE_OFFICE = "C:\\Program Files\\LibreOffice\\program\\soffice.exe"


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
