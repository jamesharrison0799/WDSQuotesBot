from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import requests
import textwrap
import time
from configparser import ConfigParser
import os

#Load Parser
parser = ConfigParser()
parser.read('quotemaker/settings.ini')
print(parser.sections())

#Check for output file
if !os.path.isdir('quotemaker/final'):
    os.mkdir('quotemaker/final')

class ImageMaker:

    def __init__(self,author,message,image_path):
        self.message = '"' + message + '"'
        self.author = author
        self.image_path = image_path
        self.outpath = "quotemaker/final/{}-{}.png".format(self.author.replace(" ",""),time.strftime("%x %X",time.gmtime()).replace("/","_").replace(" ","-").replace(":","_"))

    def last_image(self):
        return(format(self.outpath))

    def create_image(self):

        print("\n\n**Creating Image**\n\nauthor: {}\nMessage: {}\nImg path: {}\n\n** **".format(self.author,self.message,self.image_path))
        #define sizes
        W = parser.getint('image','width')
        H = parser.getint('image','height')
        size = (W, H)
        max_width = parser.getint('text','max_quote_line_length')

        bg = Image.open("quotemaker/assests/bg.png")
        quote = ImageFont.truetype(parser.get('text','quote_font'),parser.getint('text','quote_size'))
        person = ImageFont.truetype(parser.get('text','name_font'),parser.getint('text','name_size'))

        #Get image
        response = requests.get(self.image_path)
        im = Image.open(BytesIO(response.content))

        #resize
        #im = im.resize(size,resample=1)

        #crop type
        crop_type=parser.get('image','crop_type')

        #Get current and desired ratio
        im_ratio = im.size[0]/float(im.size[1])
        ratio = size[0]/float(size[1])

        if ratio > im_ratio:
            im = im.resize((size[0], int(round(size[0] * im.size[1] / im.size[0]))),
                Image.ANTIALIAS)
            # Crop in the top, middle or bottom
            if crop_type == 'top':
                box = (0, 0, im.size[0], size[1])
            elif crop_type == 'middle':
                box = (0, int(round((im.size[1] - size[1]) / 2)), im.size[0],int(round((im.size[1] + size[1]) / 2)))
            elif crop_type == 'bottom':
                box = (0, im.size[1] - size[1], im.size[0], im.size[1])
            else :
                raise ValueError('ERROR: invalid value for crop_type')
            im = im.crop(box)
        elif ratio < im_ratio:
            im = im.resize((int(round(size[1] * im.size[0] / im.size[1])), size[1]),Image.ANTIALIAS)
            # Crop in the top, middle or bottom
            if crop_type == 'top':
                box = (0, 0, size[0], im.size[1])
            elif crop_type == 'middle':
                box = (int(round((im.size[0] - size[0]) / 2)), 0,int(round((im.size[0] + size[0]) / 2)), im.size[1])
            elif crop_type == 'bottom':
                box = (im.size[0] - size[0], 0, im.size[0], im.size[1])
            else :
                raise ValueError('ERROR: invalid value for crop_type')
            im = im.crop(box)
        else :
            im = im.resize((size[0], size[1]),Image.ANTIALIAS)

        #im.show()
        #print(im.size)
        #convert type to ensure match
        im = im.convert("RGBA")
        bg = bg.convert("RGBA")

        #Blend
        comp = Image.blend(bg,im,0.5)

        ##Draw text##
        draw = ImageDraw.Draw(comp)

        #Draw quote
        w1, h1 = draw.textsize(self.message, font=quote)
        #print(len(self.message))
        if len(self.message) < max_width:
            draw.text(((W-w1)/2,(H-h1)/2), self.message, font=quote)
        else:
            lines = textwrap.wrap(self.message, width=max_width)
            y_text = h1
            total_height = 0;
            for line in lines:
                dimensions=quote.getsize(line)
                total_height+=dimensions[1]

            for line in lines:
                #print(line)
                width, height = quote.getsize(line)
                draw.text(((W - width)/2,((H-y_text)/2)),line,font=quote)
                y_text -= height + 80

        #Draw author
        w2, h2 = draw.textsize(self.author,font=person)
        draw.text(((W-w2)/2,1100), self.author, font=person)


        comp.save(self.outpath,"PNG")

        im.close()
        comp.close()
