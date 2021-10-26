import os
import img2pdf
import zipfile
import time
from pdf2image import convert_from_path
from docx2pdf import convert
from subprocess import  Popen
from .settings import PYTESSERACT_EXE_FILE_PATH, POPPLER_PATH, OPER_SYS, LIBRE_OFFICE


def line(oper_sys):
    if oper_sys == "Windows":
        return "\\"
    elif oper_sys == "Linux":
        return "/"

def parse_file_path(file_path, oper_sys=OPER_SYS):
    '''Функция возвращает словарь составных частей файла.
    
    На вход подается полное имя пути до файла, а возвращается
    объект типа словарь, в котором 4 ключа: формат, имя, корен,
    полный путь.

    '''

    slash = line(oper_sys)
    
    return dict(
        format = file_path.split(".")[-1],
        name = (file_path.split(slash)[-1]).split(".")[-2],
        root = slash.join(file_path.split(slash)[:-1]),
        path = file_path
    )

def pdf_to_imgs(file_path, poppler_path=None, oper_sys=OPER_SYS, quality=240):
    '''Функция возвращает список имен путей изображений, преобразованных из pdf.

    Функиция преобразует pdf в изображения и 
    сохраняет. 
    
    '''
    
    slash = line(oper_sys)
    print("PATH: " + file_path)
    imgs = convert_from_path(file_path, dpi=quality, poppler_path=poppler_path)
    
    imgs_paths = []
    path = slash.join(file_path.split(slash)[:-1])
    file_name = (file_path.split(slash)[-1]).split('.')[0]
    if not os.path.isdir(path + slash + file_name):
        os.mkdir(f"{path}{slash}{file_name}")

    for img in imgs:
        # enhancer_filter(img)
        # contrast_filter(img)
        imgs_paths.append(f"{path}{slash}{file_name}{slash}{file_name}_{imgs.index(img)}.jpg")
        print("> [OK] Создано изображение: " + imgs_paths[-1])
        img.save(imgs_paths[-1])
    
    return imgs_paths

def docx_to_imgs(file_path, poppler_path=POPPLER_PATH, oper_sys=OPER_SYS, quality=230):
    slash = line(oper_sys)
    file = parse_file_path(file_path, oper_sys)
    path = file["root"] + slash + file["name"] + ".pdf"
    p = Popen([LIBRE_OFFICE, '--headless', '--convert-to', 'pdf', '--outdir', \
        file["root"], file_path])
    p.communicate()

    return pdf_to_imgs(path, poppler_path, oper_sys, quality=240)

def imgs_to_pdf(files_paths, oper_sys=OPER_SYS):
    slash = line(oper_sys)
    
    path = slash.join(files_paths[0].split(slash)[:-2]) + "_blur.pdf"
    # print("PATH:", path)
    with open(path,"wb") as f:
	    f.write(img2pdf.convert(files_paths))
    print("> [OK] Создан файл: " + path)
    return path

def pdf_to_zip(files_paths, oper_sys=OPER_SYS):
    file = parse_file_path(files_paths[0], oper_sys)
    slash = line(oper_sys)

    filename = 'blurs_' + str(round(time.time() * 1000)) + '.zip'
    full_path = file['root'] + slash + filename

    with zipfile.ZipFile(full_path, 'w') as myzip:
        for file_path in files_paths:
            file = parse_file_path(file_path, oper_sys)
            myzip.write(file['root'] + slash + file['name'] + "." + file['format'], \
                arcname=file['name'] + "." + file['format'])
            print("> [OK] Создан архив: " + full_path)
    return 'static/' + filename

def xlsx_to_imgs(file_path, poppler_path=POPPLER_PATH, oper_sys=OPER_SYS, quality=240):
    slash = line(oper_sys)
    file = parse_file_path(file_path, oper_sys)
    path = file["root"] + slash + file["name"] + ".pdf"
    p = Popen([LIBRE_OFFICE, '--headless', '--convert-to', 'pdf', '--outdir', \
        file["root"], file_path])
    p.communicate()
    return pdf_to_imgs(path, poppler_path, oper_sys, quality=240)

def doc_to_imgs(file_path, poppler_path=POPPLER_PATH, oper_sys=OPER_SYS, quality=240):
    slash = line(oper_sys)
    file = parse_file_path(file_path, oper_sys)
    path = file["root"] + slash + file["name"] + ".pdf"
    p = Popen([LIBRE_OFFICE, '--headless', '--convert-to', 'pdf', '--outdir', \
        file["root"], file_path])
    p.communicate()
    return pdf_to_imgs(path, poppler_path, oper_sys, quality=240)

def rtf_to_imgs(file_path, poppler_path=POPPLER_PATH, oper_sys=OPER_SYS, quality=240):
    slash = line(oper_sys)
    file = parse_file_path(file_path, oper_sys)
    path = file["root"] + slash + file["name"] + ".pdf"
    p = Popen([LIBRE_OFFICE, '--headless', '--convert-to', 'pdf', '--outdir', \
        file["root"], file_path])
    p.communicate()
    return pdf_to_imgs(path, poppler_path, oper_sys, quality=240)