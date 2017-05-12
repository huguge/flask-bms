import os
from wand.image import Image
from wand.color import Color

def getImageFromPdf(source_file, target_file, dest_width=100, dest_height=100):
    # print os.path.splitext(source_file)[1] 
    if os.path.splitext(source_file)[1] != '.pdf':
        raise NotImplementedError()
    RESOLUTION = 300
    first_page = source_file+'[1]'
    ret = True
    try:
        with Image(filename=first_page, resolution=(RESOLUTION,RESOLUTION)) as img:
            img.background_color = Color('white')
            img_width = img.width
            ratio     = dest_width / img_width
            img.resize(dest_width, dest_height)
            img.format = 'jpeg'
            img.save(filename = target_file)
    except Exception as e:
        raise e
        ret = False
    return ret
def main():
    source = './test.pdf'
    dest = './test.jpg'
    ret = getImageFromPdf(source,dest)
    if ret is True:
        print 'Convert Success'
if __name__ == '__main__':
    main()