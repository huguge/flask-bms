import os
from wand.image import Image
from wand.color import Color

def getImageFromPdf(source_file, target_file, dest_width=200, dest_height=300):
    # print os.path.splitext(source_file)[1] 
    if os.path.splitext(source_file)[1] != '.pdf':
        raise NotImplementedError()
    # RESOLUTION = 200
    first_page = source_file+'[0]'
    ret = True
    try:
        with Image(filename=first_page) as img:
            img.background_color = Color('white')
            # img_width = img.width
            # ratio     = dest_width / img_width
            img.resize(dest_width, dest_height)
            img.format = 'jpeg'
            img.save(filename = target_file)
    except Exception as e:
        raise e
        ret = False
    return ret


