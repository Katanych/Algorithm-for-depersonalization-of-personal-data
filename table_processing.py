from numpy import pi, copy
import cv2
from words_processing import blur_words
from pytesseract import pytesseract, Output


def blur_table(img, config):
    '''Функция деперсонализирует таблицу'''
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
