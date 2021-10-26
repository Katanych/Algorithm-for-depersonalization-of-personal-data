from file_processing import *
from anonymization import *


PYTESSERACT_EXE_FILE_PATH = "C:\\Users\\k4t4n\\Desktop\\hack\\tes\\tesseract.exe"  			 # Путь до tesseract
LIBRE_OFFICE = "C:\\Program Files\\LibreOffice\\program\\soffice.exe"					 # Путь до LibreOffice
POPPLER_PATH = "C:\\Program Files\\poppler\\bin"							 # Путь до Poppler
FILES_PATHS = ["C:\\Users\\k4t4n\\Desktop\\test7\\27.rtf", "C:\\Users\\k4t4n\\Desktop\\test5\\13.pdf"]   # Константа списка файлов
OPER_SYS = "Windows" 											 # Операционная система

def main():
    end_paths = anonym_list_files(FILES_PATHS, POPPLER_PATH, PYTESSERACT_EXE_FILE_PATH, OPER_SYS) # or oper_sys="Linux"
    # end_paths = anonym_dict_files(FILES_PATHS, POPPLER_PATH, PYTESSERACT_EXE_FILE_PATH, OPER_SYS) # or oper_sys="Linux"
    print(end_paths)

if __name__ == "__main__":
    main()