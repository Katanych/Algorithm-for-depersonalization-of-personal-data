from file_processing import *
from anonymization import *
from pathlib import Path


PYTESSERACT_EXE_FILE_PATH = "C:\\Users\\k4t4n\\Desktop\\hack\\tes\\tesseract.exe"  			             # Путь до tesseract
LIBRE_OFFICE = "C:\\Program Files\\LibreOffice\\program\\soffice.exe"					                 # Путь до LibreOffice
POPPLER_PATH = "C:\\Program Files\\poppler\\bin"							                             # Путь до Poppler
FILES_PATHS = ["C:\\Users\\k4t4n\\Desktop\\test12\\brit.jpg"]#, "C:\\Users\\k4t4n\\Desktop\\test11\\11-10.doc",\
   # "C:\\Users\\k4t4n\\Desktop\\test11\\11-11.pdf", "C:\\Users\\k4t4n\\Desktop\\test11\\11-12.xlsx",\
   #     "C:\\Users\\k4t4n\\Desktop\\test11\\11-13.pdf"]#, "C:\\Users\\k4t4n\\Desktop\\test11\\11-6.pdf",\
           #"C:\\Users\\k4t4n\\Desktop\\test11\\11-7.pdf","C:\\Users\\k4t4n\\Desktop\\test11\\11-8.pdf"] # "C:\\Users\\k4t4n\\Desktop\\hack\\test4\\8.pdf", \
    #"C:\\Users\\k4t4n\\Desktop\\hack\\test4\\9.pdf"] # "C:\\Users\\k4t4n\\Desktop\\test10\\14.pdf"] # Константа списка файлов
OPER_SYS = "Windows" 											                                         # Операционная система

def main():
    end_paths = anonym_list_files(FILES_PATHS, POPPLER_PATH, PYTESSERACT_EXE_FILE_PATH, OPER_SYS)        # Win
    # end_paths = anonym_dict_files(FILES_PATHS, POPPLER_PATH, PYTESSERACT_EXE_FILE_PATH, OPER_SYS)      # Lin
    print(end_paths)

if __name__ == "__main__":
    main()