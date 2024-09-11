import json

colors = json.load(open("data/character_colours.json"))

def char_color(character):
    if character in colors.keys():
        return colors[character]
    else:
        return "#ffffff"

def char_font(character):
    color = char_color(character)[1:]
    rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
    intensity = rgb[0]*0.299 + rgb[1]*0.587 + rgb[2]*0.114
    return "white" if intensity < 186 else "black"