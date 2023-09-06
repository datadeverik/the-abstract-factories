import numpy as np
import cv2 as cv

def expand_arr(arr, new_size):
    "Expands an array to a new size by repeating the array's elements."
    tile_counts = np.ceil(np.asarray(new_size) / np.asarray(arr.shape)).astype(int)
    return np.tile(arr, tile_counts)[tuple(map(slice, new_size))]

def censor_fast(img, mask, key):
    'Encrypt the portion of the image covered by the mask with a key.'
    xor_key = np.zeros_like(img)
    np.copyto(xor_key, key, where=mask)
    return img ^ xor_key
 
def censor(img, mask, key):
    'Encrypt the portion of the image covered by the mask with a key.'
    _key = expand_arr(key, img.shape)
    return censor_fast(img, mask, _key)

def deepen(arr, n):   # Used for turning (a, b) -> (a, b, n)
    'Copy the same array along a new axis'
    source = range(arr.ndim + 1)
    dest = [arr.ndim] + list(range(arr.ndim))
    return np.moveaxis(np.repeat(arr[np.newaxis, ...], n, axis=0), source, dest)

def decensor(img, key, threshold=0.25):
    'Attempt to detect the censored region and decensor it.'
    mask = deepen(cv.blur(cv.Canny(img, 500, 600), (5, 5)) > threshold, 3)
    return censor(encrypt, mask, key)

def steno_censor(img, cover, mask, key, unitx=2, unity=2):
    'Replacement of censor, except embeds ciphertext into an integrated image.'
    res = img.copy()
    np.copyto(res, cover, where=mask)
    res = cv.resize(res, (0,0), fx=unitx, fy=unity)
    print(res.shape)
    res[::unitx, ::unity] = np.bitwise_xor(img, expand_arr(key, img.shape), where=mask)
    return res

def steno_decensor(img, key, unitx=2, unity=2, threshold=0.25):
    'Decensor output of steno_censor; requires unitx and unity values.'
    return decensor(img[::unitx, ::unity], key, threshold)
