#!/usr/bin/env python

import os
from subprocess import Popen

keyword = "tree_of_life"

orig_dir = keyword + "/orig_images/"
bmp_dir = keyword + "/bmp_images/"
eps_dir = keyword + "/eps_images/"
hpgl_dir = keyword + "/hpgl_images/"

def main():

    if not os.path.exists(bmp_dir):
       os.makedirs(bmp_dir)
    if not os.path.exists(eps_dir):
        os.makedirs(eps_dir)
    if not os.path.exists(hpgl_dir):
        os.makedirs(hpgl_dir)


    jpgs = os.listdir(orig_dir)

    for jpg in jpgs:
        print "doing:", jpg
        jpg_to_bmp(jpg)
        bmp_to_bmpbmp(jpg + ".bmp")
        bmpbmp_to_eps(jpg + ".bmp.bmp")
        eps_to_hpgl(jpg + ".bmp.bmp.eps")


# sips -s format bmp images/1.jpg --out images/1.bmp
def jpg_to_bmp(filename):
    
    in_name = orig_dir + filename
    out_name = bmp_dir + filename + ".bmp"
    
    print "doing:", in_name, out_name
    p = Popen(["sips", "-s", "format", "bmp", in_name, "--out", out_name])
    p.communicate()

# mkbitmap -f 2 -s 2 -t 0.48 -o images/1.bmp.bmp images/1.bmp
def bmp_to_bmpbmp(filename):
    in_name = bmp_dir + filename
    out_name = in_name + ".bmp"
    
    print "bmp_to_bmpbmp doing:", in_name, out_name
    p = Popen(["mkbitmap", "-f", "2", "-s", "1", "-t", "0.48", "-o",
               out_name, in_name])
    p.communicate()

# potrace -t 5 images/1.bmp.bmp -o images/1.eps
def bmpbmp_to_eps(filename):
    in_name = bmp_dir + filename
    out_name = eps_dir + filename + ".eps"

    print "bmpbmp_to_eps doing:", in_name, out_name
    p = Popen(["potrace", "-t", "5", in_name, "-o", out_name])
    p.communicate()
    
# pstoedit -f hpgl images/1.eps images/1.hpgl
def eps_to_hpgl(filename):
    in_name = eps_dir + filename
    out_name = hpgl_dir + filename + ".hpgl"

    p = Popen(["pstoedit", "-f", "hpgl", in_name, out_name])
    p.communicate()


### run main if called from command line like so:
### $> python jpg_to_hpgl.py
if __name__ == '__main__': main()

