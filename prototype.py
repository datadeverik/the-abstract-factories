# Dependencies: pygame, opencv, numpy

import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'
import pygame
import cv2 as cv
import numpy as np
from time import time
from censorlib import censor_fast, expand_arr, decensor
import argparse

parser = argparse.ArgumentParser(
    prog='rev-censor',
    description='Reversibly open up and censor/decensor images')

parser.add_argument('image', help='The path to the image which you want to censor/decensor')
parser.add_argument('-o', '--output', help='The path to write the generated image. Must be a PNG file.')
parser.add_argument('-k', '--key-file', help='The path to the keyfile', default='~/.key.jpg')
parser.add_argument('-g', '--generate-key-file',
        help='Whether or not to generate a keyfile at the given path',
        action='store_true')
args = parser.parse_args()

# Image which is opened
FILENAME = args.image
OUTPATH = args.output if args.output else 'censored-' + FILENAME
ZOOMTICKVALUE = 0.9
KEY_PATH = args.key_file
if args.generate_key_file:
    KEY = np.random.randint(0, 256, size=(1000, 100, 3), dtype='uint8')    # TODO: Make size of key adjustable
    cv.imwrite(KEY_PATH, KEY)
else:
    KEY = cv.imread(KEY_PATH)
if KEY is None:
    raise FileNotFoundError("Keyfile not found")
if not OUTPATH.endswith('png'):
    OUTPATH = '.'.join(OUTPATH.split('.')[:-1]) + '.png'

pygame.init()
screen = pygame.display.set_mode((300, 300), pygame.RESIZABLE)
clock = pygame.time.Clock()

def resize(img, shape):
    '"Resizes" the image to the given shape; retains aspect ratio and pads to the given shape.'
    f = min(shape[0] / img.shape[0], shape[1] / img.shape[1])
    arr = cv.resize(img, (0,0), fx=f, fy=f, interpolation=cv.INTER_NEAREST)
    return np.pad(arr, [(0, i - x) for i, x in zip(shape + (3,), arr.shape)])

def blit_img(img, imview, scr):    # TODO Decrease verbosity
    '''Blits a view of an image to the screen.

    The way I imagine this function is as a map from a rectangle (imview) of the whole image (img)
    to the screen(scr). It retains the aspect ratio and resizes appropriately so that the section
    of the image fills the whole screen.'''
    # First get the portion of the image which is shown
    x = np.clip(imview.x, 0, img.shape[0])
    xe = np.clip(imview.x + imview.w, 0, img.shape[0])
    y = np.clip(imview.y, 0, img.shape[1])
    ye = np.clip(imview.y + imview.w, 0, img.shape[1])
    slice = img[x:xe, y:ye]
    # Now pad for parts beyond the edge
    dx1 = max(x - imview.x, 0)
    dx2 = max(imview.x + imview.w - xe, 0)
    dy1 = max(y - imview.y, 0)
    dy2 = max(imview.y + imview.h - ye, 0)
    res = resize(np.pad(slice, [(dx1, dx2), (dy1, dy2), (0, 0)]), scr.get_size())
    pygame.surfarray.blit_array(scr, res)
    return res.shape[:2]

def get_img_pos(pos, imview, scrsize):
    'Maps from raw mouse position to the position on the image. Very basic and easily broken.'
    x, y = pos
    w, h = scrsize
    return (round(x / w * imview.w + imview.x), round(y / h * imview.h + imview.y))  # Simple proportions

im = np.swapaxes(cv.cvtColor(cv.imread(FILENAME), cv.COLOR_BGR2RGB), 0, 1)   # IDK why this is necessary; it shouldn't
mask = np.zeros(im.shape, dtype=bool)
view = pygame.Rect((0, 0), im.shape[:2])        # This is imview in blit_img
scrsize = screen.get_size()

key = expand_arr(KEY, im.shape)    # Try to speed things up by expanding before the mainloop starts (spoiler: doesn't work)

click_start = None      # Records the position where a drag event starts
rbpressed = False       # Right button pressed (better ways of doing this)
sl = 50                 # Selection length (for XORing in the key)
fill_val = True         # True sets mask, False erases censor

print('censor runtime\tupdate runtime')

running = True
while running:
    screen.fill('black')
    pos = get_img_pos(pygame.mouse.get_pos(), view, scrsize)
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False
        elif e.type == pygame.MOUSEBUTTONDOWN:
            if e.button == 1:    # Left click
                click_start = pos
            elif e.button == 3:  # Right click
                rbpressed = True
            elif e.button == 4:  # Zoom in
                view.scale_by_ip(ZOOMTICKVALUE)
            elif e.button == 5:  # Zoom out
                view.scale_by_ip(1/ZOOMTICKVALUE)
            # Some weird things happen when you zoom in too much. Might want to investigate
        elif e.type == pygame.MOUSEBUTTONUP:
            if e.button == 1:
                view = _view
                click_start = None
            elif e.button == 3:
                rbpressed = False
        elif e.type == pygame.KEYDOWN:
            if e.unicode == 'w': sl += 10    # Increase and decrease size of XORed box
            elif e.unicode == 'q': sl -= 10
            elif e.unicode == 't': fill_val = not fill_val
            elif e.unicode == 's':
                res = cv.cvtColor(np.swapaxes(censor_fast(im, mask, key), 0, 1), cv.COLOR_RGB2BGR)
                cv.imwrite(OUTPATH, res)
                print(f'Saved to {OUTPATH}')
            elif e.unicode == 'r':
                r = cv.imread(OUTPATH)
                if r is not None:
                    im = np.swapaxes(cv.cvtColor(r, cv.COLOR_BGR2RGB), 0, 1)
            elif e.unicode == 'd':     # Decensor
                mask.fill(0)      # Erase mask
                im = decensor(im, key)
    if rbpressed:
        mask[pos[0]-sl:pos[0]+sl, pos[1]-sl:pos[1]+sl] = fill_val
    if click_start is not None:
        _view = view.copy()
        _view.x -= pos[0] - click_start[0]
        _view.y -= pos[1] - click_start[1]
    else:
        _view = view
    s1 = time()
    a = censor_fast(im, mask, key)
    s2 = time()
    scrsize = blit_img(a, _view, screen)
    s3 = time()
    print(s2 - s1, s3 - s2, end='\r', sep='    \b\b\b\b\t')
    pygame.display.flip()
    clock.tick(120)
