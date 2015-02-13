#!/usr/bin/env python
"""
    Image Placeholder Server
    By Arielle B Cruz <http://www.abcruz.com> <arielle.cruz@gmail.com>
    Dedicated to the Public Domain on January 2013.
    
    Description:
        Inspired by http://placehold.it. Generates placeholder images for web
        pages in development but does not require an active Internet connection.
        
        Requires the Python Imaging Library.
    
    Usage:
        Run this script in a terminal.
        
        Point browser or link HTML to http://localhost:5000/(width)x(height)
              or http://localhost:5000/(width)x(height)/(color hex code)
              or http://localhost:5000/(width)x(height)/(bg color)/(txt color)?text=[text to display]
              or http://localhost:5000/(single value assume square)
    
    Credits:
        http://lost-theory.org/python/dynamicimg.html

    Updates by Mark: 
     - Allows Single size variable and will assume Square
     - Allow secondary color for Font Color
     - Allow text=[ what you want it to say] as a URL variable
     - Centered the Text on the Image
"""

from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from PIL import Image, ImageDraw#, ImageFont
import cStringIO

server_port = 8888
default_size = (100, 100)
default_color = "#CCCCCC"

class MyHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        self.text = ''
        self.text_color = '#000000'
        self.text_multiplier = 2
        self.img_color = "#CCCCCC"
        self.img_size = (100,100)
        # Check the requested path.
        self.check_path()
        # Create the image.
        self.create_image()
        # Start responding.
        self.respond()

        
    
    def check_path(self):
        #Check for Variables in the URL        
        variables = self.path.split("?")
        if len(variables) > 1:
            total = variables[1].split("&")
            for x in range(0, len(total)):
                current = total[x].split("=")
                if current[0].lower() == 'text':
                    self.text = current[1].replace("%20"," ")
                if current[0].lower() == 'text_size':
                    self.text_size = current[1].replace("px","").replace("in","")
        
        #Split the URI
        path = variables[0].split("/")[1:]
        
        # Get the size, that's required any way.
        size = path[0].split("x")
        if len(size) == 1:
            if size[0].isdigit():
                self.img_size = (int(size[0]), int(size[0]))
        if len(size) == 2:
            if size[0].isdigit() and size[1].isdigit():
                self.img_size = (int(size[0]), int(size[1]))
        
        # If we have a second component, that should be the color.
        if len(path) > 1:
            bc = [x for x in path[1] if x in "0123456789aAbBcCdDeEfF"]
            if len(bc) == 6 or len(bc) == 3:
                self.img_color = "#" + "".join(bc)
        if len(path) > 2:
            fc = [x for x in path[2] if x in "0123456789aAbBcCdDeEfF"]
            if len(fc) == 6 or len(fc) == 3:
                self.text_color = "#" + "".join(fc)


    
    def create_image(self):

        # The image to be sent out.
        self.img = Image.new("RGB", self.img_size, self.img_color)
        
        # Add the dimensions of the requested image to the image itself.
        img = Image.new("RGB", (10, 10), self.img_color)
        draw = ImageDraw.Draw(img)
        #note25 = ImageFont.truetype('Handlee-Regular.ttf', 25)
        if len(self.text) > 0:
            txw, txh = draw.textsize(self.text)#, font=note25)
        else:
            txw, txh = draw.textsize(str(self.img_size))#, font=note25)
        
        new_img = img.resize( ( txw, txh ) )
        draw = ImageDraw.Draw(new_img)

        if len(self.text) > 0:
            draw.text((0, 0), self.text, fill=self.text_color)#, font=note25)
        else:
            draw.text((0, 0), str(self.img_size), fill=self.text_color)#, font=note25)

        pos = ((self.img_size[0]-txw) / 2, (self.img_size[1]-txh) / 2)

        self.img.paste(new_img, pos)


    
    def respond(self):
        """Sends the response."""
        self.send_response(200)
        self.send_header("Content-Type", "image/png")
        self.end_headers()
        # Save the image to a temporary file-like object.
        f = cStringIO.StringIO()
        self.img.save(f, "PNG")
        f.seek(0)
        self.wfile.write(f.read())


if __name__ == "__main__":
    
    try:
        server = HTTPServer(("", server_port), MyHandler)
        print "Simple HTTP server started on port %s." % server_port
        server.serve_forever()
    
    except KeyboardInterrupt:
        print "\nInterrupted. Goodbye."
        server.socket.close()