# -*- coding: utf-8 -*-
from urllib.request import urlretrieve
import csv
import colormath
import matplotlib
import numpy as np
import requests
import json
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager, rc

from colormath.color_objects import sRGBColor, LabColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000
from colorthief import ColorThief
from operator import eq

import urllib
import os
import re


class Combination:
    def __init__(self, keyword, image, color1, color2, color3):
        self.keyword = keyword
        self.image = image
        self.color1 = color1
        self.color2 = color2
        self.color3 = color3


def remove_blanks(a_list):
    new_list = []
    for item in a_list:
        if item != "" and item != "\n":
            new_list.append(item)
    return new_list


def get_ht_hash():
    temp_list = []

    # 윈도우 인코딩
    f = open('hueAndTone.csv', 'r', encoding='utf-8')
    i = 0
    while True:
        if i == 0:
            i = i + 1
            continue

        v = f.readline()
        if v == "":
            break

        # v = v.replace(" ", "")
        s = v.split(',')

        s[6] = str(s[6])
        s[6] = str(s[6])[0:-1]

        if s[0] == "":
            break
        s = remove_blanks(s)
        temp_list.append(s)

    ht_num_list = []
    ht_rgb_list = []
    ht_color_list = []

    # 범위 1부터 : 첫줄 (헤더) 건너뜀
    for i in range(1, len(temp_list)):
        ht_num = temp_list[i][0]
        ht_color = temp_list[i][1]
        ht_rgb = []

        v = temp_list[i]

        r = v[4]
        g = v[5]
        b = v[6]

        rgb = sRGBColor(r, g, b)
        ht_rgb.append(rgb)

        ht_num_list.append(ht_num)
        ht_rgb_list.append(ht_rgb)
        ht_color_list.append(ht_color)

    ht_color_hash = dict(zip(ht_color_list, ht_rgb_list))
    ht_num_rgb_hash = dict(zip(ht_num_list, ht_rgb_list))

    f.close()

    return ht_num_rgb_hash


def get_combi_list():
    temp_list = []

    # 윈도우 인코딩
    f = open('num_combin.csv', 'r', encoding='utf-8')
    i = 0
    while True:
        if i == 0:
            i = i + 1
            continue

        v = f.readline()
        if v == "":
            break

        v = v.replace("\"", "")
        s = v.split(',')

        s[4] = str(s[4])[0:-1]

        if s[0] == "":
            break
        s = remove_blanks(s)
        temp_list.append(s)

    keyword_list = []
    image_list = []
    color1_list = []
    color2_list = []
    color3_list = []
    combi_list = []

    # 범위 1부터 : 첫줄 (헤더) 건너뜀
    for i in range(1, len(temp_list)):
        keyword = temp_list[i][0]
        image = temp_list[i][1]
        color1 = temp_list[i][2]
        color2 = temp_list[i][3]
        color3 = temp_list[i][4]

        combi = Combination(keyword, image, color1, color2, color3)

        keyword_list.append(keyword)
        image_list.append(image)
        color1_list.append(color1)
        color2_list.append(color2)
        color3_list.append(color3)

        combi_list.append(combi)

    f.close()

    return combi_list


def match_combi(webtoon_combi):
    combi_list = get_combi_list()

    result_keyword = ""
    result_image = ""

    for i in range(0, len(combi_list)):
        print("i:", i)
        diff, keyword, image, f_color1, f_color2, f_color3 = match_combi_color(webtoon_combi, combi_list[i])
        if i == 0:
            result = diff
        else:
            if result > diff:
                print("#####FOUND!", i)
                print("Found WORD : ", combi_list[i].keyword, combi_list[i].image)
                result = diff
                result_keyword = keyword
                result_image = image
                result_color1 = f_color1
                result_color2 = f_color2
                result_color3 = f_color3

    # print("result: ", result)
    print("result_keyword: ", result_keyword)
    print("result_image: ", result_image)
    print("result_color1: ", result_color1)
    print("result_color2: ", result_color2)
    print("result_color3: ", result_color3)
    return result_image


def match_combi_color(webtoon_combi, combi):
    ht_hash = get_ht_hash()

    color1 = ht_hash.get(combi.color1)[0]
    color2 = ht_hash.get(combi.color2)[0]
    color3 = ht_hash.get(combi.color3)[0]

    print("\tcombi: ", combi.keyword, combi.image)
    print("\tcombi.color1: ", combi.color1)
    print("\tcombi.color2: ", combi.color2)
    print("\tcombi.color3: ", combi.color3)

    # print("\tcombi_RGB1: ", color1)
    # print("\tcombi_RGB2: ", color2)
    # print("\tcombi_RGB3: ", color3)

    # webtoon_combi 첫번째 색 : b1 비교
    lab_wc_color1 = convert_color(ht_hash.get(str(webtoon_combi[2]))[0], LabColor)
    lab_wc_color2 = convert_color(ht_hash.get(str(webtoon_combi[3]))[0], LabColor)
    lab_wc_color3 = convert_color(ht_hash.get(str(webtoon_combi[4]))[0], LabColor)
    lab_wc_list = [lab_wc_color1, lab_wc_color2, lab_wc_color3]

    lab_cb_color1 = convert_color(ht_hash.get(combi.color1)[0], LabColor)
    lab_cb_color2 = convert_color(ht_hash.get(combi.color2)[0], LabColor)
    lab_cb_color3 = convert_color(ht_hash.get(combi.color3)[0], LabColor)
    lab_cb_list = [lab_cb_color1, lab_cb_color2, lab_cb_color3]

    total_diff = 0
    for i in range(0, 3):

        diff = 0
        for j in range(0, 3):
            # print("for i: ", i)

            if j == 0:
                diff = colormath.color_diff.delta_e_cie2000(lab_wc_list[i], lab_cb_list[j], 1, 1, 1)
            else:
                if diff > colormath.color_diff.delta_e_cie2000(lab_wc_list[i], lab_cb_list[j], 1, 1, 1):
                    diff = colormath.color_diff.delta_e_cie2000(lab_wc_list[i], lab_cb_list[j], 1, 1, 1)

        total_diff = total_diff + diff

    keyword = combi.keyword
    image = combi.image
    # print("total_diff: ", total_diff)
    return total_diff, keyword, image, combi.color1, combi.color2, combi.color3


if __name__ == '__main__':
    # 비교용 테스트 색조합
    test_combi = ('modern', 'masculine', 143, 151, 114)

    match_combi(test_combi)
