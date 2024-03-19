import numpy as np
import pandas as pd
import json
import cv2
import os
from config import get_config
from selenium_color_grabber import get_snapshot_coords

CONFIG = get_config()
BACKGROUNDS_FOLDER = CONFIG["filePath"]["local"]["backgrounds"]
BACKGROUNDS = CONFIG["folderName"]["backgrounds"]
STOUT = CONFIG["filePath"]["local"]["stouts"]
IMAGE_PATH = CONFIG["filePath"]["local"]["images"]
COLORS = CONFIG["fileName"]["colors"]
COORDS = CONFIG["fileName"]["coords"]
color_json = {
    "modeType": {
        "light": {
        },
        "dark": {
        }
    }
}
r = g = b = xpos = ypos = lcount = dcount = 0
light_font_obj = {}
dark_font_obj = {}

# k-nearest neightbor
# def recognize_color(R,G,B):
#     minimum = 10000
#     for i in range(len(csv)):
#         d = abs(R- int(csv.loc[i,"R"])) + abs(G- int(csv.loc[i,"G"]))+ abs(B- int(csv.loc[i,"B"]))
#         if(d<=minimum):
#             minimum = d
#             cname = csv.loc[i,"color_name"]
#     return cname
# populate a color obj depending on the coords

def build_colors(data, img, mode, fileName):
    h, w, c = img.shape
    x = data["modeType"][mode]["font"]["x"]
    y = data["modeType"][mode]["font"]["y"]
    width = data["modeType"][mode]["font"]["width"]
    height = data["modeType"][mode]["font"]["height"]
    backgroundColorRGB = color_at_coords(img, data["modeType"][mode]["backgroundColor"]["x"]+35, data["modeType"][mode]["backgroundColor"]["y"])
    # Save 1 by 1 pixel of background color
    cropped_image = img[data["modeType"][mode]["backgroundColor"]["x"]+35:data["modeType"][mode]["backgroundColor"]["x"]+36, data["modeType"][mode]["backgroundColor"]["y"]:data["modeType"][mode]["backgroundColor"]["y"]+1]
    cv2.imwrite(f"{BACKGROUNDS_FOLDER}/{mode}_{fileName}_bg.png", cropped_image)
    color_json["modeType"][mode]["backgroundColor"] = rgb_to_hex(backgroundColorRGB)
    buttonRGB = color_at_coords(img, data["modeType"][mode]["buttonBackground"]["x"]+3, data["modeType"][mode]["buttonBackground"]["y"]+35)
    color_json["modeType"][mode]["buttonBackground"] = rgb_to_hex(buttonRGB)

    # Build our objects for potential font colors
    for i in range(1, width):
        if x+i == w:
            break
        color_at_coords(img, x+i, y, mode, True)
        ++i
    # Should only run twice
    if (mode == "light"):
        predict_font_color(mode, light_font_obj)
    elif (mode == "dark"):
        predict_font_color(mode, dark_font_obj)
    else:
        print("ERROR in build_colors")
        return

#Takes an image, x + y cords, a mode type and if prediction is required
def color_at_coords(img, x, y, mode = '', predict = False):
    global b,g,r,xpos,ypos,light_font_obj,dark_font_obj, lcount, dcount
    xpos = x
    ypos = y
    r,g,b = img[y,x]
    r = int(r)
    g = int(g)
    b = int(b)
    color = r,g,b
    if predict and mode == 'light':
        if(not (color ==  color_json["modeType"][mode]["backgroundColor"])):
            if f"{color}" in light_font_obj:
                lcount = 1 + lcount
                light_font_obj[f"{color}"] = lcount
            else:
                light_font_obj[f"{color}"] = 1
    elif predict and mode == 'dark':
        if(not (color ==  color_json["modeType"][mode]["backgroundColor"])):
            if f"{color}" in dark_font_obj:
                dcount = 1 + dcount
                dark_font_obj[f"{color}"] = dcount
            else:
                dark_font_obj[f"{color}"] = 1
    else:
        return color
    
def hex_to_rgb(hex):
    hex = hex[slice(1,len(hex))]
    return tuple(int(hex[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb):
    return '#{:02x}{:02x}{:02x}'.format(rgb[0], rgb[1], rgb[2])

def get_RGB_from_int(RGBint):
    blue =  RGBint & 255
    green = (RGBint >> 8) & 255
    red =   (RGBint >> 16) & 255
    return red, green, blue

def get_int_from_color(rgb):
    # If hex conver to rgb otherwise convert
    red = rgb[0]
    green = rgb[1]
    blue = rgb[2]
    RGBint = (red<<16) + (green<<8) + blue
    return RGBint

def predict_font_color(mode, font_obj):
    seenCount = bgRGBInt = seenRGBInt = 0
    # Checks most amounts and checks alpha value to be inverse of background color
    if color_json["modeType"][mode]["backgroundColor"] is not None:
        bgRGBInt = get_int_from_color(hex_to_rgb(color_json["modeType"][mode]["backgroundColor"]))
        for val in font_obj:
            tempRGBInt = get_int_from_color(tuple(map(int, val[slice(1,len(val)-1)].split(', '))))
            if font_obj[val] > seenCount and (tempRGBInt > bgRGBInt and tempRGBInt > seenRGBInt):
                seenCount = font_obj[val]
                seenRGBInt = tempRGBInt
    else:
        return
    color_json["modeType"][mode]["fontColor"] = rgb_to_hex(get_RGB_from_int(seenRGBInt))

def main():
    get_snapshot_coords()
    global img
    
    try:
        for val in os.listdir(IMAGE_PATH):
            #key files
            if(val != ".DS_Store" and val != BACKGROUNDS):
                print(val)
                if val.find("dark") >= 0:
                    color = "dark"
                    colorFile = val[5:-4]
                else:
                    color = "light"
                    colorFile = val[6:-4]

                f = open(f"./stouts/{colorFile}{COORDS}")
                data = json.load(f)
                img = cv2.imread(f"{IMAGE_PATH}{val}")
                build_colors(data, img, color, colorFile)

                f.close()
                print(f"FINISHED READING {colorFile}{COORDS} {color} JSON")

                file = open(f"{STOUT}{colorFile}{COLORS}", "w")
                json.dump(color_json, file)
                file.close()
                print(f"FINISHED WRITING {colorFile}{COLORS} {color} JSON")

    except Exception as e:
        print("error witih color_check")
        print(e)
        return

main()