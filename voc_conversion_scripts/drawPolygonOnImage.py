'''
   Converts labels from LabelmMe program and converts it to hd5 file
'''
import os
import sys
import json
import numpy as np
import xml.etree.ElementTree as et
from yad2k.utils.draw_boxes import draw_boxes
from PIL import Image, ImageDraw
import numpy
import random

debug = False #only load 10 images

# this is before chdir

def random_color():
    rgbl = [255, 0, 0]
    random.shuffle(rgbl)
    rgbl.append(125)
    return tuple(rgbl)


DEBUG = True
baseAnnotationDir = 'images/house/raw/Annotations'
baseImageDir = 'images/house/raw/Images'
imageOutPath = 'images/out_polygon/'


image_labels = []
labelList = []
numFile = 0

os.chdir('..')

try:

    for i, dirName in enumerate(os.listdir(baseAnnotationDir)):
        fullDirPath = baseAnnotationDir + "/" + dirName
        # print(fullDirPath)

        if os.path.isdir(fullDirPath):
            for filename in os.listdir(fullDirPath):
                xmldoc = et.parse(fullDirPath + "/" + filename)
                filename = xmldoc.find('filename').text

                # get the file names
                fullPath = dirName + "/" + filename
                image_labels.append([fullPath])

                objElements = xmldoc.findall('object')
                print()
                print(fullPath)
                print("numFile: " + str(numFile))

                # There are many points. Turn it into a rectangle
                # Get the lowest x, y and the highest x, y
                for k, obj in enumerate(objElements):
                    objName = obj.find('name').text
                    objName = objName.replace(',', '')
                    # print(objName)

                    if objName not in labelList:
                        labelList.append(objName)
                        labelNum = labelList.index(objName)
                    else:
                        labelNum = labelList.index(objName)

                    image_labels[numFile].append([labelNum])

                    ptElements = obj.findall('polygon')[0].findall('pt')
                    for l, pt in enumerate(ptElements):
                        x = int(pt.find('x').text)
                        y = int(pt.find('y').text)
                        image_labels[numFile][k+1].append((x,y))

                numFile += 1

                if DEBUG and numFile == 5:
                    break
        if DEBUG and i == 1:
            break

except:
    print ("x: ")
    raise


labelFile = open("label", "w")
for i, value in enumerate(labelList):
    labelFile.write(str(i) + " , " + str(value) + "\n")
labelFile.close()
# convert

# load images
images = []
for i, labels in enumerate(image_labels):
    imgName = labels.pop(0)
    imgFile = Image.open(os.path.join(baseImageDir, imgName))

    data = imgFile.getdata()
    img = np.array(data,  dtype=np.object)
    imgUInt8 = np.array(imgFile,  dtype=np.uint8)

    images.append(img)
    boxes = [box[1:] for box in labels]
    box_classes = [box[0] for box in labels]


    for label in labels:
        drw = ImageDraw.Draw(imgFile, 'RGBA')
        drw.polygon(label[1:], random_color())
        del drw
        imgFile.save(os.path.join(imageOutPath, str(imgName)), 'PNG' )




    if DEBUG and i == 30:
        break

