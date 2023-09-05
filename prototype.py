import pygame
import cv2 as cv
import numpy as np
from time import time
from censorlib import censor

FILENAME = 'img.jpg'
ZOOMTICKVALUE = 0.9

key = 255*np.ones((100, 100,3), dtype='uint8')

pygame.init()
screen = pygame.display.set_mode((300, 300), pygame.RESIZABLE)
clock = pygame.time.Clock()

def resize(img, shape):
    f = min(shape[0] / img.shape[0], shape[1] / img.shape[1])
    arr = cv.resize(img, (0,0), fx=f, fy=f, interpolation=cv.INTER_NEAREST)
    return np.pad(arr, [(0, i - x) for i, x in zip(shape + (3,), arr.shape)])

def blit_img(img, imview, scr):    # TODO Decrease verbosity
    x = np.clip(imview.x, 0, img.shape[0])
    xe = np.clip(imview.x + imview.w, 0, img.shape[0])
    y = np.clip(imview.y, 0, img.shape[1])
    ye = np.clip(imview.y + imview.w, 0, img.shape[1])
    slice = img[x:xe, y:ye]
    dx1 = x - imview.x
    dx2 = imview.x + imview.w - xe
    dy1 = y - imview.y
    dy2 = imview.y + imview.h - ye
    res = resize(np.pad(slice, [(dx1, dx2), (dy1, dy2), (0, 0)]), scr.get_size())
    pygame.surfarray.blit_array(scr, res)
    return res.shape[:2]

def get_img_pos(pos, imview, scrsize):
    x, y = pos
    w, h = scrsize
    return (round(x / w * imview.w + imview.x), round(y / h * imview.h + imview.y))

im = np.swapaxes(cv.cvtColor(cv.imread(FILENAME), cv.COLOR_BGR2RGB), 0, 1)
mask = np.zeros(im.shape, dtype=bool)
view = pygame.Rect((100, 100), im.shape[:2])
scrsize = screen.get_size()

click_start = None
rbpressed = False
sl = 50    # Selection length

running = True
while running:
    screen.fill('black')
    pos = get_img_pos(pygame.mouse.get_pos(), view, scrsize)
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False
        elif e.type == pygame.MOUSEBUTTONDOWN:
            if e.button == 1:
                click_start = pos
            elif e.button == 3:
                rbpressed = True
            elif e.button == 4:
                view.scale_by_ip(ZOOMTICKVALUE)
            elif e.button == 5:
                view.scale_by_ip(1/ZOOMTICKVALUE)
        elif e.type == pygame.MOUSEBUTTONUP:
            if e.button == 1:
                view = _view
                click_start = None
            elif e.button == 3:
                rbpressed = False
        elif e.type == pygame.KEYDOWN:
            if e.unicode == 'w': sl += 10
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
    a = censor(im, mask, key)
    s2 = time()
    scrsize = blit_img(a, _view, screen)
    s3 = time()
    print(s2 - s1, s3 - s2, end='\r')
    pygame.display.flip()
    clock.tick(120)
