'''
    This program packages the labels and images
from the underwater dataset and converts them
to an hdf5 database file.m

    Thanks, Thomas, for labeling all of those images.
        -shadySource
'''
import os
import sys
import json
import numpy as np
from xml.dom import minidom
from yad2k.utils.draw_boxes import draw_boxes
from PIL import Image

debug = True #only load 10 images

# this is before chdir


DEBUG = True
baseAnnotationDir = 'images/house/raw/Annotations'
baseImageDir = 'images/house/raw/Images'
imageOutPath = 'images/out/'


image_labels = []
labelFile = open("labels", "w")
labelList = []
box_classes = []

os.chdir('..')

labelNum = 0
for i, dirName in enumerate(os.listdir(baseAnnotationDir)):
    fullDirPath = baseAnnotationDir + "/" + dirName
    # print(fullDirPath)

    if os.path.isdir(fullDirPath):
        for j, filename in enumerate(os.listdir(fullDirPath)):
            xmldoc = minidom.parse(fullDirPath + "/" + filename)
            elements = xmldoc.getElementsByTagName('filename')

            # get the file names
            fullPath = dirName + "/" + elements[0].firstChild.nodeValue
            # print(fullPath)

            objElements = xmldoc.getElementsByTagName('object')

            # There are many points. Turn it into a rectangle
            # Get the lowest x, y and the highest x, y
            for obj in objElements:
                objName = obj.getElementsByTagName('name')[0].firstChild.nodeValue

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

            objName = objName.replace(',','')
            labelFile.write(objName + "\n")


            image_labels.append([fullPath, [labelNum,  xmin + " " + ymin + " " + xmax + " " + ymax]])
            box_classes.append(labelNum)
            labelList.append(objName)
            labelNum = labelNum+1


            if DEBUG and j == 5:
                break
    if DEBUG and i == 1:
        break

labelFile.close()
# convert

# load images
images = []
for i, label in enumerate(image_labels):
    # with open('Images/' + label[0], 'rb') as in_file:
    #     data = in_file.read()
    # img = np.fromstring(data, dtype='uint8')

    imgFile = Image.open(os.path.join(baseImageDir, label[0]))
    # if imgFile.mode != "RGB":
    #     imgFile = imgFile.convert("RGB")

    # data = imgFile.getdata()
    # img = np.array(data,  dtype=np.object)
    imgUInt8 = np.array(imgFile,  dtype=np.uint8)
    # img = np.fromstring(imgFile.tobytes(), dtype=np.uint8)


    # [label[1][0]]
    images.append(imgFile)
    images_with_boxes = draw_boxes(imgUInt8 , [label[1][1].split(' ')], [0] , [labelList[label[1][0]]])

    # Save the image:
    image = Image.fromarray(images_with_boxes)
    print("Image saved" + str(label[0]))

    image.save(os.path.join(imageOutPath, str(label[0])), 'PNG' )

    if DEBUG and i == 30:
        break

#shuffle dataset
np.random.seed(13)
imageWithLabel = [(images[i], image_labels[i]) for i in range(len(images))]
np.random.shuffle(imageWithLabel)
images = [pair[0] for pair in imageWithLabel]
image_labels = [pair[1] for pair in imageWithLabel]


# images = images[0:2]
# for img in images:
#     print(img)
#     print(type(img))
#     print("------------")

# exit()

#convert to numpy for saving
images = np.asarray(images)
image_labels = [np.array(i[1:]) for i in image_labels]# remove the file names
image_labels = np.array(image_labels)

#save dataset
np.savez("houseImages", images=images, boxes=image_labels)
print('Data saved: houseImages.npz')
