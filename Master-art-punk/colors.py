import PIL
import csv
import cv2
import math
import random
import settings
import numpy as np
from matplotlib import image
from sklearn.cluster import KMeans
from os import listdir
import png
from imageData.subject import canvas

k = 30
init = 'random'
random_state = 88


def box_method(color_data, group_distance):
    color_data_random_box = []
    for i in range(0, 8):
        color_data_random_box.append(
            color_data[(len(color_data) - 1) - (i * group_distance + random.randint(0, group_distance - 1))])
    return color_data_random_box


def rgb_to_hex(rgb):
    color = ''
    for i in rgb:
        num = round(float(i))
        color += str(hex(num))[-2:].replace('x', '0').lower()
    # print(color)
    # print(rgb)
    return color


def get_all_colors_list(model, k):
    colors = []
    labels_list = np.arange(0, k + 1)
    (proportion, _) = np.histogram(model.labels_, bins=labels_list)
    proportion = proportion.astype("float")
    proportion /= proportion.sum()
    for (_, color) in sorted(zip(proportion, model.cluster_centers_), key=lambda x: x[0], reverse=True):
        colors.append(list(map(int, color)))
        # print(colors)
    return colors


def get_main_colors(directory):
    colors_all_out = []
    for filename in listdir(directory):
        img = cv2.imread(directory + filename)
        try:
            PIL.Image.fromarray(image.imread(directory + filename))
        except FileNotFoundError:
            continue
        img_data = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        r, g, _ = cv2.split(img_data)
        # 行*列和颜色通道数（因RGB而为3个）
        img = img.reshape((img_data.shape[0] * img_data.shape[1], 3))
        print("加载" + filename + "中......")
        model = KMeans(n_clusters=k, init=init, random_state=random_state)
        model.fit(img)
        colors_all_out += get_all_colors_list(model, k)
        print("完成" + filename + "提取!")
    return colors_all_out


def get_color_data():
    f = open(settings.color_distance_filepath, "r+", encoding="utf-8-sig")
    reader = csv.reader(f)
    color_data_sort = list(reader)
    case_number = 8
    box = box_method(color_data_sort, len(color_data_sort) // case_number)
    return [rgb_to_hex(i[:3]) for i in box]


def colour_distance(rgb_1, rgb_2):
    R_1, G_1, B_1 = rgb_1
    R_2, G_2, B_2 = rgb_2
    rmean = (R_1 + R_2) / 2
    R = R_1 - R_2
    G = G_1 - G_2
    B = B_1 - B_2
    return math.sqrt((2 + rmean / 256) * (R ** 2) + 4 * (G ** 2) + (2 + (255 - rmean) / 256) * (B ** 2))


def random_colors():
    colorArr = ['1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f']
    color = ""
    for random_value in range(6):
        color += colorArr[random.randint(0, 14)]
    return color


def merge(sticker0, sticker1):
    colors = sticker0['colors']
    index = {}
    for i, color in enumerate(sticker1['colors']):
        if color not in colors:
            colors.append(color)
            index[i] = colors.index(color)
            print(colors.index(color))
        else:
            index[i] = colors.index(color)

    for i, row in enumerate(sticker1['data']):
        for j, color in enumerate(row):
            if color > 0:
                sticker0['data'][i][j] = index[color]
    return sticker0


def merges(stickers):
    if len(stickers) >= 2:
        sticker = merge(stickers.pop(0), stickers.pop(0))
        stickers.insert(0, sticker)
    else:
        return stickers[0]
    return merges(stickers)


def generate(image_data, name):
    # colors = image['colors'][1:]
    palette = [(255, 255, 255, 0)]
    # colors = ['000000'] + [random_colors() for i in range(0,8)] #随机颜色
    colors = ['000000'] + get_color_data()  # 艺术家风格
    # print(colors)
    for color in colors:
        color = [int(c, 16) for c in (color[:2], color[2:4], color[4:])]
        palette.append(tuple(color))
        # print(palette)
    pixel_picture_file = png.Writer(len(canvas['data'][0]), len(
        canvas['data']), palette=palette, bitdepth=4)
    pixel_picture = open(f'output/{name}.png', 'wb')
    pixel_picture_file.write(pixel_picture, image_data['data'])
