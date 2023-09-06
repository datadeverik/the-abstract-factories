# Dependencies: pygame, opencv, numpy
# Usage:
#   Set FILENAME to the inputted file and run the program.
#   (Optional) set KEY to a random numpy array. Its shape doesn't matter.
#   Click to drag and drag while right-clicking to censor
#   Scroll to zoom

import pygame
import cv2 as cv
import numpy as np
from time import time
from censorlib import censor_fast, expand_arr

# Image which is opened
FILENAME = 'a.jpg'
ZOOMTICKVALUE = 0.9
KEY = 255*np.ones((100, 100, 3), dtype='uint8')

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
    dx1 = x - imview.x
    dx2 = imview.x + imview.w - xe
    dy1 = y - imview.y
    dy2 = imview.y + imview.h - ye
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
            if e.unicode == 'q': sl -= 10
    if rbpressed:
        mask[pos[0]-sl:pos[0]+sl, pos[1]-sl:pos[1]+sl] = True
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
    print(s2 - s1, s3 - s2, end='\r', sep='\t')   # On my computer, ~0.1s for censor and ~0.5 for render for a 480KB image (I think)
    pygame.display.flip()
    clock.tick(120)
