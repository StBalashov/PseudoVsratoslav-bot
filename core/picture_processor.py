from PIL import Image, ImageDraw, ImageFont
import random
import json
import face_recognition
import os

RESOURCES_PATH = os.path.abspath('./resources/')


def getRandomPhrase():
    with open(RESOURCES_PATH + "/phrases.json", "r") as f:
        phrases = json.load(f)
    return random.choice(phrases)


def addText(picturePath, phrase, output):
    img = Image.open(picturePath)
    width, height = img.size
    drawing = ImageDraw.Draw(img)
    font = ImageFont.truetype(RESOURCES_PATH + '/Lobster-Regular.ttf', round(height * 0.1))
    font_color = (242, 242, 242)
    textW, textH = drawing.textsize(phrase, font)
    proportion = textH / textW
    font = ImageFont.truetype(RESOURCES_PATH + '/Lobster-Regular.ttf',
                              min(round(height * 0.2), round(width * 0.64 * proportion)))
    textW, textH = drawing.textsize(phrase, font)
    start_pos = (round((width - textW) / 2), round((height - textH) * 0.9))
    drawing.text(start_pos, phrase, font=font, fill=font_color)
    img.save(RESOURCES_PATH + output)


def doMakeUp(picturePath):
    image = face_recognition.load_image_file(picturePath)
    face_landmarks_list = face_recognition.face_landmarks(image)
    pil_image = Image.fromarray(image)
    d = ImageDraw.Draw(pil_image, 'RGBA')

    # Eyebrows
    d.polygon(face_landmarks_list[0]['left_eyebrow'], fill=(68, 54, 39, 128))
    d.polygon(face_landmarks_list[0]['right_eyebrow'], fill=(68, 54, 39, 128))
    d.line(face_landmarks_list[0]['left_eyebrow'], fill=(68, 54, 39, 150), width=5)
    d.line(face_landmarks_list[0]['right_eyebrow'], fill=(68, 54, 39, 150), width=5)

    # Lips
    d.polygon(face_landmarks_list[0]['top_lip'], fill=(150, 0, 0, 128))
    d.polygon(face_landmarks_list[0]['bottom_lip'], fill=(150, 0, 0, 128))
    d.line(face_landmarks_list[0]['top_lip'], fill=(150, 0, 0, 64), width=8)
    d.line(face_landmarks_list[0]['bottom_lip'], fill=(150, 0, 0, 64), width=8)

    # Eyes
    d.polygon(face_landmarks_list[0]['left_eye'], fill=(255, 255, 255, 30))
    d.polygon(face_landmarks_list[0]['right_eye'], fill=(255, 255, 255, 30))
    d.line(face_landmarks_list[0]['left_eye'] + [face_landmarks_list[0]['left_eye'][0]], fill=(0, 0, 0, 110), width=6)
    d.line(face_landmarks_list[0]['right_eye'] + [face_landmarks_list[0]['right_eye'][0]], fill=(0, 0, 0, 110), width=6)

    pil_image.save(RESOURCES_PATH + '/makeup.jpg')

    addText(RESOURCES_PATH + '/makeup.jpg', "все бабы как бабы, а я - богиня...", "/makeup.jpg")

    if len(face_landmarks_list) > 0:
        return True
    return False
