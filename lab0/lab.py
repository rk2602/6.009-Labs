# No Imports Allowed!


def backwards(sound):
    y = sound.copy()
    #reverse left
    temp=y.get('left')
    y.pop('left')
    temp=temp[::-1]
    y.update({'left':temp})
    #reverse right
    temp2=y.get('right')
    y.pop('right')
    temp2=temp2[::-1]
    y.update({'right':temp2})
    return y

def mix(sound1, sound2, p):
    new={}
    if sound1['rate']==sound2['rate']:
        new.update({'rate':sound1['rate']})
        #new values for left and right speaker respectively
        L=[len(sound1['left']), len(sound2['left'])]
        R=[]
        small=min(L)
        L.clear()
        for f in range(small):
            L.append((p*(sound1['left'][f]))+((1-p)*(sound2['left'][f])))
            R.append((p*(sound1['right'][f]))+((1-p)*(sound2['right'][f])))
        new.update({'left':L})
        new.update({'right':R})
        return new
    else:
        return None

def echo(sound, num_echos, delay, scale):
    oth=sound.copy()
    interval=round(delay * oth['rate'])
    #oth_left and _right will be the new left and right speakers track
    
    oth_left=oth['left'][:]
    for q in range(len(oth['left'])):    
        echos=num_echos
        orig_sound=oth['left'][q]
        while echos>0:
            #to avoid IndexError, I add a lot of zeroes
            if (q+(interval*(num_echos-echos+1)))>len(oth_left)-1:
                c=(q+(interval*(num_echos-echos+1)))-len(oth_left)+10
                for d in range(c):
                    oth_left.append(0)
            #after every interval, an additional scaled echo is added
            oth_left[q+(interval*(num_echos-echos+1))]+=orig_sound*(scale**(num_echos-echos+1))
            echos-=1
    #trailing zeroes removed
    while oth_left[-1]==0:
        oth_left.pop(-1)        
        
    oth_right=oth['right'][:]
    for q in range(len(oth['right'])):    
        echos=num_echos
        orig_sound=oth['right'][q]
        while echos>0:
            #after every interval, an additional scaled echo is added
            if (q+(interval*(num_echos-echos+1)))>len(oth_right)-1:
                c=(q+(interval*(num_echos-echos+1)))-len(oth_right)+10
                for d in range(c):
                    oth_right.append(0)
            oth_right[q+(interval*(num_echos-echos+1))]+=orig_sound*(scale**(num_echos-echos+1))
            echos-=1
    while oth_right[-1]==0:
        oth_right.pop(-1)
    
    #making sure left and right speaker have the same length    
    L=len(oth_left)
    R=len(oth_right)
    if L>R:
        z=L-R
        for h in range(z):
            oth_right.append(0)
    elif R>L:
        z=R-L
        for h in range(z):
            oth_left.append(0)
    oth.pop('left')
    oth.pop('right')
    oth.update({'left':oth_left})
    oth.update({'right':oth_right})       
    return oth

def pan(sound):
    oth={}
    #for some reason I was getting an assertion error that I was modifying the
    #input, so I took the long route and just updated an empty dictionary.
    oth.update({'rate':sound['rate']})
    L=sound['left'][:]
    R=sound['right'][:]
    oth.update({'left':L})
    oth.update({'right':R})
    N=len(oth['left'])
    #Not sure what to do if N=1 or 2, so I guessed based on the wording.
    if N==1:
        oth['right'][0]=0
    elif N==2:
        oth['right'][0]=0
        oth['left'][1]=0
    else:
        oth['right'][0]=0
        oth['left'][N-1]=0
        for val in range(1,N-1):
            temp=oth['right'][val]
            oth['right'][val]=temp*(val/(N-1))
            temp2=oth['left'][val]
            oth['left'][val]=temp2*(1-(val/(N-1)))
    return oth

def remove_vocals(sound):
    #I'm just going to be safe again.
    oth={}
    oth.update({'rate':sound['rate']})
    L=sound['left'][:]
    R=sound['right'][:]
    oth.update({'left':L})
    oth.update({'right':R})
    for x in range(len(oth['left'])):
        diff=(oth['left'][x]-oth['right'][x])
        oth['left'][x]=diff
        oth['right'][x]=diff
    return oth


# below are helper functions for converting back-and-forth between WAV files
# and our internal dictionary representation for sounds

import io
import wave
import struct

def load_wav(filename):
    """
    Given the filename of a WAV file, load the data from that file and return a
    Python dictionary representing that sound
    """
    f = wave.open(filename, 'r')
    chan, bd, sr, count, _, _ = f.getparams()

    assert bd == 2, "only 16-bit WAV files are supported"

    left = []
    right = []
    for i in range(count):
        frame = f.readframes(1)
        if chan == 2:
            left.append(struct.unpack('<h', frame[:2])[0])
            right.append(struct.unpack('<h', frame[2:])[0])
        else:
            datum = struct.unpack('<h', frame)[0]
            left.append(datum)
            right.append(datum)

    left = [i/(2**15) for i in left]
    right = [i/(2**15) for i in right]

    return {'rate': sr, 'left': left, 'right': right}


def write_wav(sound, filename):
    """
    Given a dictionary representing a sound, and a filename, convert the given
    sound into WAV format and save it as a file with the given filename (which
    can then be opened by most audio players)
    """
    outfile = wave.open(filename, 'w')
    outfile.setparams((2, 2, sound['rate'], 0, 'NONE', 'not compressed'))

    out = []
    for l, r in zip(sound['left'], sound['right']):
        l = int(max(-1, min(1, l)) * (2**15-1))
        r = int(max(-1, min(1, r)) * (2**15-1))
        out.append(l)
        out.append(r)

    outfile.writeframes(b''.join(struct.pack('<h', frame) for frame in out))
    outfile.close()


if __name__ == '__main__':
    # code in this block will only be run when you explicitly run your script,
    # and not when the tests are being run.  this is a good place to put your
    # code for generating and saving sounds, or any other code you write for
    # testing, etc.

    # here is an example of loading a file (note that this is specified as
    # sounds/hello.wav, rather than just as hello.wav, to account for the
    # sound files being in a different directory than this file)
    pass
    #example:
    #hello = load_wav('sounds/hello.wav')
    #write_wav(backwards(hello), 'answers/hello_reversed.wav')
    
    #to get reversed file:
    # wacky = load_wav('sounds/mystery.wav')
    #write_wav(backwards(wacky), 'answers/reversed_mystery.wav')
    
    #to get mixed file:
    #syn = load_wav('sounds/synth.wav')
    #wat = load_wav('sounds/water.wav')
    #write_wav(mix(syn, wat, 0.2), 'answers/mix_synth_water.wav')
    
    #to get echo file:
    #norm = load_wav('sounds/chord.wav')
    #write_wav(echo(norm, 5, 0.3, 0.6), 'answers/chord_echo.wav')
    
    #to get pan file:
    #unpan = load_wav('sounds/car.wav')
    #write_wav(pan(unpan), 'answers/panned_car.wav')
    
    #to get unvocalized file:
    #vocal = load_wav('sounds/coffee.wav')
    #write_wav(remove_vocals(vocal),'answers/somewhat_no_vocal_coffee.wav')
     
    