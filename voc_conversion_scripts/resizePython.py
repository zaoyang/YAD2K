from PIL import Image, ImageOps
import os

def resizecrop(src, out, width, height):
	img = Image.open(src)
	img = ImageOps.fit(img, (width, height), Image.ANTIALIAS, 0, (0.5, 0.5))
	img.save(out)

baseImageDir = '/Users/zaoyang/Sites/LabelMeAnnotationTool/ImagesOrig/'
imageOutPath = '/Users/zaoyang/Sites/LabelMeAnnotationTool/Images/'


# have to resize in 32 by 32

for i, dirName in enumerate(os.listdir(baseImageDir)):
  fullDirPath = baseImageDir + dirName
  if os.path.isdir(fullDirPath):
    for filename in os.listdir(fullDirPath):
      fullPath = fullDirPath + "/" + filename
      fullOutPath = imageOutPath + dirName + "/" + filename

      print(fullPath)
      print(fullOutPath)
      resizecrop(fullPath, fullOutPath, 640, 480)