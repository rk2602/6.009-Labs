#!/usr/bin/env python3

# NO ADDITIONAL IMPORTS!
# (except in the last part of the lab; see the lab writeup for details)
import math
from PIL import Image

# Lab 1 functions

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

# Back to Lab2 2
# VARIOUS FILTERS


def color_filter_from_greyscale_filter(filt):
    """
    Given a filter that takes a greyscale image as input and produces a
    greyscale image as output, returns a function that takes a color image as
    input and produces the filtered color image.
    """
    def doall3(img):
        a=[]
        b=[]
        c=[]
        d=[]
        new_img={
                'height': img['height'],
                'width': img['width']
            }
        for w in range(3):
            val=[]
            for f in range(len(img['pixels'])):
                val.append(img['pixels'][f][w])
            new_img.update({'pixels':val})
            val2=filt(new_img)
            val3=val2['pixels'][:]
            if w==0:
                a=val3[:] 
            elif w==1:
                b=val3[:]
            else:
                c=val3[:]
            new_img.pop('pixels')
        for k in range(len(a)):
            d.append((a[k],b[k],c[k]))
        new_img.update({'pixels':d})
        return new_img
    return doall3


def make_blur_filter(n):
    def blurall3(img):
        a=[]
        b=[]
        c=[]
        d=[]
        new_img={
                'height': img['height'],
                'width': img['width']
            }
        try:
            for w in range(3):
                val=[]
                for f in range(len(img['pixels'])):
                    val.append(img['pixels'][f][w])
                new_img.update({'pixels':val})
                val2=blurred(new_img,n)
                val3=val2['pixels'][:]
                if w==0:
                    a=val3[:] 
                elif w==1:
                    b=val3[:]
                else:
                    c=val3[:]
                new_img.pop('pixels')
            for k in range(len(a)):
                d.append((a[k],b[k],c[k]))
            new_img.update({'pixels':d})
        except TypeError:
            pixels2=img['pixels'][:]
            new_img.update({'pixels':pixels2})
            new_img=blurred(new_img,n)
        return new_img
    return blurall3


def make_sharpen_filter(n):
    def sharpenall3(img):
        a=[]
        b=[]
        c=[]
        d=[]
        new_img={
                'height': img['height'],
                'width': img['width']
            }
        try:
            for w in range(3):
                val=[]
                for f in range(len(img['pixels'])):
                    val.append(img['pixels'][f][w])
                new_img.update({'pixels':val})
                val2=sharpened(new_img,n)
                val3=val2['pixels'][:]
                if w==0:
                    a=val3[:] 
                elif w==1:
                    b=val3[:]
                else:
                    c=val3[:]
                new_img.pop('pixels')
            for k in range(len(a)):
                d.append((a[k],b[k],c[k]))
            new_img.update({'pixels':d})
        except TypeError:
            pixels2=img['pixels'][:]
            new_img.update({'pixels':pixels2})
            new_img=sharpened(new_img,n)
        return new_img
    return sharpenall3


def filter_cascade(filters):
    """
    Given a list of filters (implemented as functions on images), returns a new
    single filter such that applying that filter to an image produces the same
    output as applying each of the individual ones in turn.
    """
    def grandfxn(img):
        b=img.copy()
        while len(filters)>0:
            nextfilt=filters[0]
            b=nextfilt(b)
            filters.pop(0)
        return b
    return grandfxn


# SEAM CARVING

# Main Seam Carving Implementation

def seam_carving(image, ncols):
    """
    Starting from the given image, use the seam carving technique to remove
    ncols (an integer) columns from the image.
    """
    img=image.copy()
    step1 = greyscale_image_from_color_image(img)
    step2 = compute_energy(step1)
    step3 = cumulative_energy_map(step2)
    step4 = minimum_energy_seam(step3)
    step5 = image_without_seam(img, step4)
    for x in range(ncols-1):
        step1 = greyscale_image_from_color_image(step5)
        step2 = compute_energy(step1)
        step3 = cumulative_energy_map(step2)
        step4 = minimum_energy_seam(step3)
        step5 = image_without_seam(step5, step4)
    
    return step5


# Optional Helper Functions for Seam Carving

def greyscale_image_from_color_image(image):
    """
    Given a color image, computes and returns a corresponding greyscale image.

    Returns a greyscale image (represented as a dictionary).
    """
    another_image=image.copy()
    another_image.pop('pixels')
    pix=image['pixels'][:]
    for l in range(len(pix)):
        grey_num=round(.299*pix[l][0]+.587*pix[l][1]+.114*pix[l][2])
        pix[l]=grey_num
    another_image.update({'pixels':pix})
    return another_image


def compute_energy(grey):
    """
    Given a greyscale image, computes a measure of "energy", in our case using
    the edges function from last week.

    Returns a greyscale image (represented as a dictionary).
    """
    image2=grey
    image3=edges(image2)
    return image3


def cumulative_energy_map(energy):
    """
    Given a measure of energy (e.g., the output of the compute_energy function),
    computes a "cumulative energy map" as described in the lab 2 writeup.

    Returns a dictionary with 'height', 'width', and 'pixels' keys (but where
    the values in the 'pixels' array may not necessarily be in the range [0,
    255].
    """
    img=energy.copy()
    for x in range(img['height']):
        for y in range(img['width']):
            comp=[]
            r=energy['width']
            val=energy['pixels'][x*r+y]
            if x!=0:
                comp.append(energy['pixels'][(x-1)*r+y])
                if y!=0:
                    comp.append(energy['pixels'][(x-1)*r+(y-1)])
                if y!=r-1:
                    comp.append(energy['pixels'][(x-1)*r+(y+1)])
            if len(comp)!=0:
                val+=min(comp)
            img['pixels'][x*r+y]=val
    return img
            
        


def minimum_energy_seam(cem):
    """
    Given a cumulative energy map, returns a list of the indices into the
    'pixels' list that correspond to pixels contained in the minimum-energy
    seam (computed as described in the lab 2 writeup).
    """
    #basically, reverse the list, find the min on the FIRST row, and go adjacent
    #DOWN (for ties, favor RIGHT) until bottom.
    seam_list=[]
    q=cem['height']
    r=cem['width']
    pix=cem['pixels'][len(cem['pixels'])-r:len(cem['pixels'])]
    start_v=None
    start_i=None
    for w in range(len(pix)):
        if start_v is None or pix[w]<start_v:
            start_v=pix[w]
            start_i=q*r+w
            ref=w
    #have to remove a row because arrays start at 0
    seam_list.append(start_i-r)
    hcount=q-2
    while hcount>-1:
        #get indices and values of labove, rabove, and above. Find min and append
        #it's index. Favor left. Set index as ref and reduce count by 1.
        if ref-1>-1:
            labove=hcount*r+ref-1
        else:
            labove=cem['pixels'].index(max(cem['pixels']))
        above=hcount*r+ref
        if ref+1<r:
            rabove=hcount*r+ref+1
        else:
            rabove=cem['pixels'].index(max(cem['pixels']))
        
        if cem['pixels'][labove]<=cem['pixels'][above]:
            if cem['pixels'][labove]<=cem['pixels'][rabove]:
                ref=labove-(hcount*r)
                seam_list.append(labove)
            else:
                ref=rabove-(hcount*r)
                seam_list.append(rabove)
        elif cem['pixels'][above]<=cem['pixels'][rabove]:
            ref=above-(hcount*r)
            seam_list.append(above)
        else:
            ref=rabove-(hcount*r)
            seam_list.append(rabove)
        hcount-=1
    return seam_list

def image_without_seam(image, seam):
    """
    Given a (color) image and a list of indices to be removed from the image,
    return a new image (without modifying the original) that contains all the
    pixels from the original image except those corresponding to the locations
    in the given list.
    """
    #Switch seam indices with "None" and after all Nones made, remove them.
    new_img=image.copy()
    pix=new_img['pixels'][:]
    for w in seam:
        pix.pop(w)
    r=image['width']
    new_img.pop('pixels')
    new_img.update({'pixels':pix})
    new_img.update({'width':r-1})
    return new_img

def blinds(img, rc='r', bars='y', num=1):
    """
    Takes an image (grey or color) and, if bars is 'y', replaces either rows('r')
    or columns ('c') with black bars at a ratio of 1:num (for every 1 row/column,
    turn num black). If bars is 'n', just remove the rows or columns which would
    be turned black if bars was 'y'.
    """
    new_img=img.copy()
    q=img['height']
    r=img['width']
    new_img.pop('pixels')
    pix=[]
    if bars=='y':
        if rc=='r':
            count=0
            c=0
            while count<q:
                #add pixel if row #| num+1:
                if count%(num+1)==0:
                    pix.append(img['pixels'][count*r+c])
                else:
                    #add in black pixel
                    if len(img['pixels'][count*r+c])==3:
                        pix.append((0,0,0))
                    else:
                        pix.append(0)
                c+=1
                #go to a new row if all pixels accounted for:
                if c==r:
                    count+=1
                    c=0
            new_img.update({'height':round(len(pix)/r)})
            new_img.update({'pixels':pix})
            return new_img
        elif rc=='c':
            c=0
            keep=[]
            for w in range(r):
                if w%(num+1)==0:
                    keep.append(w)
            count=0
            while count<q:
                #add pixel if c is in keep:
                if c in keep:
                    pix.append(img['pixels'][count*r+c])
                else:
                    #add in black pixel
                    if len(img['pixels'][count*r+c])==3:
                        pix.append((0,0,0))
                    else:
                        pix.append(0)
                c+=1
                #go to a new row if all pixels accounted for:
                if c==r:
                    count+=1
                    c=0
            new_img.update({'width':round(len(pix)/q)})
            new_img.update({'pixels':pix})
            return new_img
        else:
            refusal = "rc needs to be either 'r' or 'c'."
            return refusal
    elif bars=='n':
        if rc=='r':
            count=0
            c=0
            while count<q:
                #add if row #| num+1:
                if c<r and count%(num+1)==0:
                    pix.append(img['pixels'][count*r+c])
                c+=1
                #go to a new row if all pixels accounted for:
                if c==r:
                    count+=1
                    c=0
            new_img.update({'height':round(len(pix)/r)})
            new_img.update({'pixels':pix})
            return new_img
        elif rc=='c':
            c=0
            keep=[]
            for w in range(r):
                if w%(num+1)==0:
                    keep.append(w)
            count=0
            while count<q:
                #add if c is in keep:
                if c in keep:
                    pix.append(img['pixels'][count*r+c])
                c+=1
                #go to a new row if all pixels accounted for:
                if c==r:
                    count+=1
                    c=0
            new_img.update({'width':round(len(pix)/q)})
            new_img.update({'pixels':pix})
            return new_img
        else:
            refusal = "rc needs to be either 'r' or 'c'."
            return refusal
    else:
        refusal = "bars needs to be either 'y' or 'n'."
        return refusal

# HELPER FUNCTIONS FOR LOADING AND SAVING COLOR IMAGES

def load_color_image(filename):
    """
    Loads a color image from the given file and returns a dictionary
    representing that image.

    Invoked as, for example:
       i = load_color_image('test_images/cat.png')
    """
    with open(filename, 'rb') as img_handle:
        img = Image.open(img_handle)
        img = img.convert('RGB')  # in case we were given a greyscale image
        img_data = img.getdata()
        pixels = list(img_data)
        w, h = img.size
        return {'height': h, 'width': w, 'pixels': pixels}


def save_color_image(image, filename, mode='PNG'):
    """
    Saves the given color image to disk or to a file-like object.  If filename
    is given as a string, the file type will be inferred from the given name.
    If filename is given as a file-like object, the file type will be
    determined by the 'mode' parameter.
    """
    out = Image.new(mode='RGB', size=(image['width'], image['height']))
    out.putdata(image['pixels'])
    if isinstance(filename, str):
        out.save(filename)
    else:
        out.save(filename, mode)
    out.close()

def load_greyscale_image(filename):
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


def save_greyscale_image(image, filename, mode='PNG'):
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
    
    #color filter:
    #color_inv = color_filter_from_greyscale_filter(inverted)
    #inv = color_inv(load_color_image('test_images/cat.png'))    
    #save_color_image(inv, 'answers/inv_cat.png')
    
    #blur filter:
    #unblur = load_color_image('test_images/python.png')
    #blurit= make_blur_filter(9)
    #blurs = blurit(unblur)
    #save_color_image(blurs, 'answers/blurred_python.png')
    
    #sharpen filter:
    #unsharpen = load_color_image('test_images/sparrowchick.png')
    #sharpenit= make_sharpen_filter(7)
    #sharpens = sharpenit(unsharpen)
    #save_color_image(sharpens, 'answers/sharpened_sparrowchick.png')
    
    #cascade filter:
    #uncascade = load_color_image('test_images/frog.png')
    #filter1 = color_filter_from_greyscale_filter(edges)
    #filter2 = color_filter_from_greyscale_filter(make_blur_filter(5))
    #filt = filter_cascade([filter1, filter1, filter2, filter1])
    #cascaded = filt(uncascade)
    #save_color_image(cascaded, 'answers/cascade_frog.png')
    
    #seam filter:
    #unseam = load_color_image('test_images/twocats.png')
    #seamed = seam_carving(unseam, 100)
    #save_color_image(seamed, 'answers/100off_twocats.png')
    
    #creative filter:
    #unblind = load_color_image('test_images/twocats.png')
    #bar1=blinds(unblind,'r','y')
    #save_color_image(bar1,'answers/bar1.png')
    #bar2=blinds(unblind,'r','n')
    #save_color_image(bar2,  'answers/bar2.png')
    #bar3=blinds(unblind,'c','y')
    #save_color_image(bar3,  'answers/bar3.png')
    #bar4=blinds(unblind,'c','n')
    #save_color_image(bar4,  'answers/bar4.png')
    pass  
