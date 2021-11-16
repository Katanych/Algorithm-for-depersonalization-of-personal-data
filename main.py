from file_processing import *
from anonymization import *
from pathlib import Path


PYTESSERACT_EXE_FILE_PATH = "C:\\Users\\k4t4n\\Desktop\\hack\\tes\\tesseract.exe"    # Путь до tesseract
LIBRE_OFFICE = "C:\\Program Files\\LibreOffice\\program\\soffice.exe"                # Путь до LibreOffice
POPPLER_PATH = "C:\\Program Files\\poppler\\bin"                                     # Путь до Poppler
FILES_PATHS = ["C:\\Users\\k4t4n\\Desktop\\test12\\brit.jpg"]                        # Константа списка файлов
OPER_SYS = "Windows"                                                                 # Операционная система

def main():
    end_paths = anonym_list_files(FILES_PATHS, POPPLER_PATH, PYTESSERACT_EXE_FILE_PATH, OPER_SYS)
    print(end_paths)

if __name__ == "__main__":
    main()
