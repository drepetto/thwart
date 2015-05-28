import os
import os.path
from subprocess import Popen
import sys
import time
from urllib import FancyURLopener
import urllib2
import simplejson
import copy
import random

from chiplotle import *
from chiplotle.hpgl.commands import PA, PR, PU, PD, IN, SP

# just testing github stuff...

# tranpose, rotate, scale and return munged copy
# connect is whether or not we insert PU/PD between chunks to avoid connection lines
def munge(orig, steps = 10, connect = False):
    
    i = 0
    i_incr = 1
    i_float_incr = i_incr * (1.0 / steps)
    len_cleaned = len(orig)
    
    bounds = tools.hpgltools.get_bounding_box(orig)
    width = bounds[1].x - bounds[0].x
    height = bounds[1].y - bounds[0].y
    print "w:", width, "h:", height
    
    munged = []
    #copy.deepcopy(orig)
    
    while i < steps:
        i_float = i * i_float_incr
        start = int(len_cleaned * i_float)
        end = int(len_cleaned * (i_float + i_float_incr))
        #print "start:", start, "end:", end
        chunk = copy.deepcopy(orig[start:end])
        tools.hpgltools.transpose(chunk, [random.randint(0,int(width * 0.25)), random.randint(0, int(width * 0.25))])
        tools.hpgltools.rotate_hpglprimitives(chunk, random.randint(0,360))
        tools.hpgltools.scale(chunk, random.random() + 0.5)
        
        if not connect:
            first = -1
            j = 0
            while first < 0:
                if isinstance(chunk[j], (PA, PR)):
                    first = j
                else:
                    j += 1
                    
            chunk.insert(j, PU())
            chunk.insert(j + 2, PD())
            
            #print chunk[j], chunk[j+1], chunk[j+2]
            
        munged.extend(chunk)
        i += i_incr

    return munged

# get list of pu/pd/pa commands from file
def clean_commands_from_file(filename):

    hpgl_commands = tools.io.import_hpgl_file(filename)
    stripped_hpgl_commands = tools.hpgltools.pens_updown_to_papr(hpgl_commands)
    cleaned = []

    for command in stripped_hpgl_commands:
        if isinstance(command, (PU, PD, PA, PR)):
            cleaned.append(command)

    return cleaned


# the whole enchilada
def search_to_hpgl(search_term, save_dir = "./", num_sets = 1):

    if not save_dir.endswith("/"):
        save_dir += "/"

    images = get_images(search_term, save_dir, num_sets)

    image_num = 0
    
    saved_filenames = []
    
    for image in images:
        out_filename = save_dir + search_term + "_" + str(image_num) + ".hpgl"
        file_saved = image_to_hpgl(image, out_filename)
        if file_saved == None:
            print "uh oh, couldn't save", out_filename
        else:
            saved_filenames.append(file_saved)
            image_num += 1


    return saved_filenames


'''
    search for images
'''
    
def get_images(search_term, save_dir = "./", num_sets = 1):

    # Replace spaces ' ' in search term for '%20' in order to comply with request
    search_term = search_term.replace(' ','%20')

    myopener = MyOpener()

    # make sure our save_dir is gonna work right...
    if not os.path.exists(save_dir):
        #print "making:", save_dir
        os.makedirs(save_dir)

    if not save_dir.endswith("/"):
        save_dir += "/"

    save_filenames = []
    
    # Set count to 0
    count= 0
    
    for i in range(0,num_sets):
        # Notice that the start changes for each iteration in order to request a new set of images for each loop
        url = ('https://ajax.googleapis.com/ajax/services/search/images?' + 'v=1.0&q='+search_term+'&start='+str(i*4)+'&userip=MyIP'+'&imgtype=lineart')
        #print url
        request = urllib2.Request(url, None, {'Referer': 'testing'})
        response = urllib2.urlopen(request)
        
        # Get results using JSON
        results = simplejson.load(response)
        data = results['responseData']
        dataInfo = data['results']
        
        # Iterate for each result and get unescaped url
        # i think these are always sets of four images
        for myUrl in dataInfo:
            count = count + 1
            #print "URL:", myUrl['unescapedUrl']
            ending = myUrl['url'].split('.')[-1]
            # in case there's weird stuff after then file type
            ending = ending[0:3]
            
        
            out_filename = save_dir + str(count)+"." + ending
            #print "saving:", out_filename
            myopener.retrieve(myUrl['unescapedUrl'], out_filename)
            
            save_filenames.append(out_filename)
        
        # Sleep for one second to prevent IP blocking from Google
        time.sleep(1)
        
    return save_filenames

# Start FancyURLopener with defined version
class MyOpener(FancyURLopener):
    version = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11'



'''
    convert images to hpgl code 
'''


def image_to_hpgl(in_file, out_file):

    #print "converting", in_file, "to hpgl..."
    
    out_path = os.path.dirname(out_file)
    
    saved_bmp = image_to_bmp(in_file, out_path + "/tmp.bmp")
    if saved_bmp == None:
        print "couldn't do image_to_bmp() for", in_file
        return None
    #print "saved:", saved_bmp
    
    saved_bmpbmp = bmp_to_bmpbmp(saved_bmp, out_path + "/tmp.bmp.bmp")
    if saved_bmpbmp == None:
        print "couldn't do bmp_to_bmpbmp() for", saved_bmp
        return None
    #print "saved:", saved_bmpbmp

    saved_eps = bmpbmp_to_eps(saved_bmpbmp, out_path + "/tmp.eps")
    if saved_eps == None:
        print "couldn't do bmpbmp_to_eps() for", saved_bmpbmp
        return None
    #print "saved:", saved_eps
    
    
    saved_hpgl = eps_to_hpgl(saved_eps, out_file)
    if saved_hpgl == None:
        print "couldn't do eps_to_hpgl() for", saved_eps
        return None
    #print "saved:", saved_hpgl

    os.remove(saved_bmp)
    os.remove(saved_bmpbmp)
    os.remove(saved_eps)

    return saved_hpgl

# sips -s format bmp images/1.jpg --out images/1.bmp
def image_to_bmp(in_file, out_file):
    
    # sips doesn't like ./ notation in paths!?!
    #print "doing:", in_file, out_file
    p = Popen(["sips", "-s", "format", "bmp", in_file, "--out", out_file])
    p.communicate()
    
    if not os.path.exists(out_file):
        print "operation failed for", out_file
        return None
        
    return out_file

# mkbitmap -f 2 -s 2 -t 0.48 -o images/1.bmp.bmp images/1.bmp
def bmp_to_bmpbmp(in_file, out_file):
    
    #print "bmp_to_bmpbmp doing:", in_file, out_file
    p = Popen(["mkbitmap", "-f", "2", "-s", "1", "-t", "0.48", "-o", out_file, in_file])
    p.communicate()
    
    if not os.path.exists(out_file):
        print "operation failed for", out_file
        return None
        
    return out_file

# potrace -t 5 images/1.bmp.bmp -o images/1.eps
def bmpbmp_to_eps(in_file, out_file):

    #print "bmpbmp_to_eps doing:", in_file, out_file
    p = Popen(["potrace", "-t", "5", in_file, "-o", out_file])
    p.communicate()

    if not os.path.exists(out_file):
        print "operation failed for", out_file
        return None
        
    return out_file
    
# pstoedit -f hpgl images/1.eps images/1.hpgl
def eps_to_hpgl(in_file, out_file):

    p = Popen(["pstoedit", "-f", "hpgl", in_file, out_file])
    p.communicate()

    if not os.path.exists(out_file):
        print "operation failed for", out_file
        return None
        
    return out_file
