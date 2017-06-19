'''
   Converts labels from LabelmMe program and converts it to hd5 file
'''
import os
import sys
import json
import numpy as np
from xml.dom import minidom
from yad2k.utils.draw_boxes import draw_boxes
from PIL import Image
import numpy

debug = True #only load 10 images

# this is before chdir


DEBUG = True
baseAnnotationDir = 'images/house/raw/Annotations'
baseImageDir = 'images/house/raw/Images'
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
            xmldoc = minidom.parse(fullDirPath + "/" + filename)
            elements = xmldoc.getElementsByTagName('filename')

            # get the file names
            fullPath = dirName + "/" + elements[0].firstChild.nodeValue
            image_labels.append([fullPath])
            objElements = xmldoc.getElementsByTagName('object')
            print()
            print(fullPath)
            print("numFile: " + str(numFile))

            # There are many points. Turn it into a rectangle
            # Get the lowest x, y and the highest x, y
            for k, obj in enumerate(objElements):
                objName = obj.getElementsByTagName('name')[0].firstChild.nodeValue
                objName = objName.replace(',', '')
                print(objName)

                xElements = obj.getElementsByTagName('polygon')[0].getElementsByTagName('x')

                xList = []
                for e in xElements:
                    xList.append(e.firstChild.nodeValue)
                yElements = obj.getElementsByTagName('polygon')[0].getElementsByTagName('y')

                yList = []
                for e in xElements:
                    yList.append(e.firstChild.nodeValue)

                xmin = min(xList)
                xmax = max(xList)
                ymin = min(xList)
                ymax = max(xList)



                if objName not in labelList:
                    labelList.append(objName)
                    labelNum = labelList.index(objName)
                else:
                    labelNum = labelList.index(objName)

                image_labels[numFile].append([labelNum, xmin, ymin, xmax, ymax])

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

    images_with_boxes = draw_boxes(imgUInt8, boxes, box_classes, labelList)

    # Save the image:
    image = Image.fromarray(images_with_boxes)
    # print("Image saved" + str(label[0]))

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
images = np.asarray(images)
image_labels = [np.array(image_label[1:]) for image_label in image_labels]# remove the file names
image_labels = np.array(image_labels)

#save dataset
np.savez("houseImages", images=images, boxes=image_labels)
print('Data saved: houseImages.npz')
