'''
   Converts labels from LabelmMe program and converts it to hd5 file
'''
import os
import sys
import json
import numpy as np
from yad2k.utils.draw_boxes import draw_boxes
from PIL import Image
import numpy

import xml.etree.ElementTree as et

debug = False #only load 10 images

# this is before chdir


DEBUG = False


# baseAnnotationDir = '/home/ubuntu/Code/LabelMeAnnotationTool/Annotations'
# baseImageDir = '/home/ubuntu/Code/LabelMeAnnotationTool/Images'
baseAnnotationDir = '/Users/zaoyang/Sites/LabelMeAnnotationTool/Annotations'
baseImageDir = '/Users/zaoyang/Sites/LabelMeAnnotationTool/Images'
imageOutPath = 'images/out/'


image_labels = []
labelList = []
numFile = 0

os.chdir('..')

for i, dirName in enumerate(os.listdir(baseAnnotationDir)):
    fullDirPath = baseAnnotationDir + "/" + dirName
    # print(fullDirPath)

    if os.path.isdir(fullDirPath):
        for filename in os.listdir(fullDirPath):
            xmlFile = fullDirPath + "/" + filename
            xmldoc = et.parse(xmlFile)
            filename = xmldoc.find('filename').text

            # get the file names
            fullPath = dirName + "/" + filename
            image_labels.append([fullPath])
            objElements = xmldoc.findall('object')
            # print()
            print(xmlFile)

            # There are many points. Turn it into a rectangle
            # Get the lowest x, y and the highest x, y
            for k, obj in enumerate(objElements):
                if (obj.find('type') is not None and obj.find('type').text == 'bounding_box'): #and filename == '0621239607d82648_3377-w500-h666-b0-p0-industrial-bathroom.jpg'
                    objName = obj.find('name').text
                    objName = objName.replace(',', '')

                    ptElements = obj.findall('polygon')[0].findall('pt')
                    xList = []
                    yList = []
                    for l, pt in enumerate(ptElements):
                        x = int(float(pt.find('x').text))
                        y = int(float(pt.find('y').text))
                        xList.append(x)
                        yList.append(y)

                    xmin = min(xList)
                    xmax = max(xList)
                    ymin = min(yList)
                    ymax = max(yList)

                    if(len(xList) == 4 and len(yList) == 4):
                        if objName not in labelList:
                            labelList.append(objName)
                            labelNum = labelList.index(objName)
                        else:
                            labelNum = labelList.index(objName)

                        # image_labels[numFile].append([labelNum, xmin, ymin, xmax, ymax])
                        image_labels[numFile].append([labelNum, ymax, xmin, ymin, xmax])

            numFile += 1

            if DEBUG and numFile == 5:
                break
    if DEBUG and i == 1:
        break


#
labelFile = open("label", "w")
for i, value in enumerate(labelList):
    labelFile.write(str(i) + " , " + str(value))
labelFile.close()

# load images
images = []
for i, labels in enumerate(image_labels):
    imgName = labels.pop(0)
    imgFile = Image.open(os.path.join(baseImageDir, imgName))
    imgUInt8 = np.array(imgFile,  dtype=np.uint8)

    images.append(imgUInt8)
    boxes = [box[1:] for box in labels]
    box_classes = [box[0] for box in labels]

    images_with_boxes = draw_boxes(imgUInt8, boxes, box_classes, labelList)

    # Save the image:
    image = Image.fromarray(images_with_boxes)

    image.save(os.path.join(imageOutPath, str(imgName)), 'PNG' )

    if DEBUG and i == 30:
        break

#shuffle dataset
np.random.seed(13)
imageWithLabel = [(images[i], image_labels[i]) for i in range(len(images))]
np.random.shuffle(imageWithLabel)
images = [pair[0] for pair in imageWithLabel]
image_labels = [pair[1] for pair in imageWithLabel]


#convert to numpy for saving
images = np.asarray(images, dtype=np.uint8)
image_labels = [np.array(image_label[1:]) for image_label in image_labels]# remove the file names
image_labels = np.array(image_labels)

#save dataset
np.savez("houseImages", images=images, boxes=image_labels)
print('Data saved: houseImages.npz')
