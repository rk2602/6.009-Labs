#!/usr/bin/env python3

import math

from PIL import Image as Image

# NO ADDITIONAL IMPORTS ALLOWED!


def get_pixel(image, x, y):
    return image['pixels'][x*image['width']+y]

def get_pixel_2(reimage, kernel, x, y, q, r, dim):
    count=0
    lim=round(dim/2-0.5)
    for s in range(0,dim):
        for t in range(0,dim):
            temp1=0
            temp2=0
            temp3=0
            temp4=0
            if x+(s-lim)<0:
                temp1=-(x+(s-lim))
            elif x+(s-lim)>q-1:
                temp2=x+(s-lim)-(q-1)
            if y+(t-lim)<0:
                temp3=-(y+(t-lim))
            elif y+(t-lim)>r-1:
                temp4=y+(t-lim)-(r-1)
            count+=reimage[((x+(s-lim)+temp1-temp2)*r+(y+(t-lim)+temp3-temp4))]*kernel[(s*dim+t)]
    return count

def set_pixel(image, x, y, c):
    r=image['width']
    image['pixels'][x*r+y] = c


def apply_per_pixel(image, func):
    result = {
        'height': image['height'],
        'width': image['width'],
        'pixels': image['pixels'][:],
    }
    for x in range(image['height']):
        for y in range(image['width']):
            color = get_pixel(image, x, y)
            newcolor = func(color)
            set_pixel(result, x, y, newcolor)
    return result


def inverted(image):
    return apply_per_pixel(image, lambda c: 255-c)


# HELPER FUNCTIONS

def correlate(image, kernel, n=0):
    """
    Compute the result of correlating the given image with the given kernel.

    The output of this function should have the same form as a 6.009 image (a
    dictionary with 'height', 'width', and 'pixels' keys), but its pixel values
    do not necessarily need to be in the range [0,255], nor do they need to be
    integers (they should not be clipped or rounded at all).

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.

    DESCRIBE YOUR KERNEL REPRESENTATION HERE:
    I essentially use the same format as what is used for the images' pixels
    (a list in row-major order).
    """
    kreimage=image['pixels'][:]
    for f in kreimage:
        f=round(f)
    oth_reimage=kreimage[:]
    new_image={
        'height': image['height'],
        'width': image['width']
    }
    dim_ker=round(math.sqrt(len(kernel)))
    for x in range(image['height']):
        for y in range(image['width']):
            r=image['width']
            q=image['height']
            new_val=get_pixel_2(kreimage, kernel, x, y, q, r, dim_ker)
            if n==0:
                new_val=round(new_val)
            oth_reimage[x*r+y]=new_val
    new_image.update({'pixels':oth_reimage})
    return new_image

def round_and_clip_image(image):
    """
    Given a dictionary, ensure that the values in the 'pixels' list are all
    integers in the range [0, 255].

    All values should be converted to integers using Python's `round` function.

    Any locations with values higher than 255 in the input should have value
    255 in the output; and any locations with values lower than 0 in the input
    should have value 0 in the output.
    """
    dreimage=image['pixels'][:]
    new_image={
        'height': image['height'],
        'width': image['width']
    }
    for w in range(len(dreimage)):
        if dreimage[w]<0:
            dreimage[w]=0
        elif dreimage[w]>255:
            dreimage[w]=255
        else:
            dreimage[w]=round(dreimage[w])
    new_image.update({'pixels':dreimage})
    return new_image


# FILTERS

def blurred(image, n):
    """
    Return a new image representing the result of applying a box blur (with
    kernel size n) to the given input image.

    This process should not mutate the input image; rather, it should create a
    separate structure to represent the output.
    """
    # first, create a representation for the appropriate n-by-n kernel (you may
    # wish to define another helper function for this)
    kernel=[]
    for w in range(n*n):
        kernel.append(1/(n*n))  

    # then compute the correlation of the input image with that kernel
    fix_image=correlate(image,kernel)

    # and, finally, make sure that the output is a valid image (using the
    # helper function from above) before returning it.
    fixed_image=round_and_clip_image(fix_image)
    return fixed_image

def sharpened(image, n):
    """
    Return a new image representing the result of applying a sharpen filter
    (with kernel size n) to the given input image.
    """
    kernelz=[]
    for w in range(n*n):
        kernelz.append(1/(n*n))
        
    new_image2={
        'height': image['height'],
        'width': image['width']
    }
    reimage2=image['pixels'][:]
    reimage3=image['pixels'][:]
    for r in range(len(reimage2)):
        reimage2[r]+=reimage2[r]
    new_image2.update({'pixels':reimage3})
    blur_image=correlate(new_image2,kernelz,1)
    for l in range(len(reimage2)):
        temp = reimage2[l]-blur_image['pixels'][l]
        reimage2[l] = temp
        reimage2[l] = round(reimage2[l])
    
    new_image2.pop('pixels')
    new_image2.update({'pixels':reimage2})
    reimage5=round_and_clip_image(new_image2)
    
    return reimage5

def edges(image):
    """
    Return a new image representing the result of applying a the Sobel 
    operator to the given input image.
    """
    kernelx=[-1, 0, 1,
             -2, 0, 2,
             -1, 0, 1]
    new_imagex={
        'height': image['height'],
        'width': image['width']
    }
    imagex=image['pixels'][:]
    new_imagex.update({'pixels':imagex})
    
    kernely=[-1, -2, -1,
             0,  0,  0,
             1,  2,  1]
    new_imagey={
        'height': image['height'],
        'width': image['width']
    }
    imagey=image['pixels'][:]
    new_imagey.update({'pixels':imagey})
    
    outx=correlate(new_imagex, kernelx, 1)
    outy=correlate(new_imagey, kernely, 1)
    
    new_imagez={
        'height': image['height'],
        'width': image['width']
    }
    trupixel=[]
    
    for h in range(len(outx['pixels'])):
        temp1=(outx['pixels'][h])**2
        temp2=(outy['pixels'][h])**2
        temp3=round(math.sqrt(temp1+temp2))
        trupixel.append(temp3)
    new_imagez.update({'pixels':trupixel})
    new_imagew=round_and_clip_image(new_imagez)
    return new_imagew  

# HELPER FUNCTIONS FOR LOADING AND SAVING IMAGES

def load_image(filename):
    """
    Loads an image from the given file and returns a dictionary
    representing that image.  This also performs conversion to greyscale.

    Invoked as, for example:
       i = load_image('test_images/cat.png')
    """
    with open(filename, 'rb') as img_handle:
        img = Image.open(img_handle)
        img_data = img.getdata()
        if img.mode.startswith('RGB'):
            pixels = [round(.299 * p[0] + .587 * p[1] + .114 * p[2])
                      for p in img_data]
        elif img.mode == 'LA':
            pixels = [p[0] for p in img_data]
        elif img.mode == 'L':
            pixels = list(img_data)
        else:
            raise ValueError('Unsupported image mode: %r' % img.mode)
        w, h = img.size
        return {'height': h, 'width': w, 'pixels': pixels}


def save_image(image, filename, mode='PNG'):
    """
    Saves the given image to disk or to a file-like object.  If filename is
    given as a string, the file type will be inferred from the given name.  If
    filename is given as a file-like object, the file type will be determined
    by the 'mode' parameter.
    """
    out = Image.new(mode='L', size=(image['width'], image['height']))
    out.putdata(image['pixels'])
    if isinstance(filename, str):
        out.save(filename)
    else:
        out.save(filename, mode)
    out.close()


if __name__ == '__main__':
    # code in this block will only be run when you explicitly run your script,
    # and not when the tests are being run.  this is a good place for
    # generating images, etc.
    
    #inverted image:
    #uninv = load_image('test_images/bluegill.png')
    #inv = inverted(uninv)
    #save_image(inv, 'answers/inv_bluegill.png')
    
    #kernalized image:
    '''unkern = load_image('test_images/pigbird.png')    
    kern99= [0, 0, 0, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0, 0, 0, 0, 0,
             1, 0, 0, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0, 0, 0, 0, 0]
    result = correlate(unkern, kern99)
    result2 = round_and_clip_image(result)
    save_image(result2, 'answers/new_pigbird.png')'''
    
    #box blur image:
    #unbox = load_image('test_images/cat.png')
    #boxed = blurred(unbox, 5)
    #save_image(boxed, 'answers/boxed_cat.png')
    
    #sharpened image:
    #unsharp = load_image('test_images/python.png')
    #sharp = sharpened(unsharp,11)
    #save_image(sharp, 'answers/sharp_python.png')
    
    #sobel image:
    #unsobel = load_image('test_images/construct.png')
    #sobel = edges(unsobel)
    #save_image(sobel, 'answers/sobel_construct.png')
    
