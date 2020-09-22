from PIL import Image
import os
#
img = Image . new( 'RGB' , (400,400) , (0,0,0) )
#
t = 0
#
while t < img . width :
    #
    img . putpixel( (t,t) , (255,255,0) )
    #
    t += 1
#
img . save( os.path.join(os.path.dirname(os.path.abspath(__file__)), 'demo.ppm') )
#
print( img . getpixel( (100,100) ) )
print( img . getpixel( (100,101) ) )
#
print( 'done' )
#
# end of file
