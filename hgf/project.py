import numpy as np
import cv2 as cv
import random


def mask_number(channels: int) -> tuple:
    """Generates a random pixel for the mask

    Args:
        channels: number of channels per pixel

    Returns:
        Tupple with 1, 3 or 4 elements, depending on channels, consisting in integers between 0 and 255
    """
    if channels == 1:
        return (random.randint(0, 255),)
    elif channels == 3:
        return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    else:
        return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255), 0)


def censor_decensor_image(img: np.ndarray, key: int, areas: list) -> np.ndarray:
    """Function to censor/decensor listed areas in an image

    Args:
        img (np.ndarray): image to be censored/decensored
        key (int): number for the random seed to generate the mask
        areas (list): list of areas (xStart, yStart, xEnd, yEnd) to censor/decensor

    Returns:
        np.ndarray: censored/decensored image
    """
    random.seed(key)
    res = img.copy()
    channels = res.shape[2]
    for area in areas:
        xs, ys, xe, ye = area
        dx = xe - xs
        dy = ye - ys
        mask = np.array([mask_number(channels) for _ in range(dx*dy)], dtype=np.uint8).reshape(dy, dx, channels)
        np.bitwise_xor(res[ys:ye, xs:xe], mask, out=res[ys:ye, xs:xe])
        # res[ys:ye, xs:xe] ^= mask

    return res


def censor_decensor(kind: str) -> None:
    """Function to censor/decencor a image file:

        - read an image file and a key file
        - censor/decensor the image using the key file
        - shows the image
        - save the image if the user wants to

    Args:
        kind (str): 'censor' or 'decensor'
    """
    print('All image files have to be in the images folder')
    name = input('Image file name: ')
    try:
        img = cv.imread(f'./images/{name}', cv.IMREAD_UNCHANGED)
        try:
            print('All key files have to be in the keys folder')
            name = input('Key file name: ')
            with open(f'./keys/{name}') as f:
                line = f.readline()
                key = int(line)
                areas = []
                for line in f.readlines():
                    areas.append([int(n) for n in line.split()])
            new_img = censor_decensor_image(img, key, areas)
            cv.imshow(f'{kind} Image', new_img)
            _ = cv.waitKey(0)
            print()
            print(f'You want to save the {kind} Image?')
            print('Provide a name bellow or leave it blank for not saving.')
            name = input('Image file name: ')
            if name != '':
                cv.imwrite(f'./images/{name}', new_img)
        except Exception:
            print('Not a valid key file')
    except Exception:
        print('Not a valid image file')


if __name__ == '__main__':
    while True:
        # Main terminal menu
        print()
        print('Censor/Decensor')
        print('-'*20)
        print('1 - Show an image')
        print('2 - Censor an image')
        print('3 - Decensor an image')
        print('4 - Exit')
        option = input('Choose an option (number): ')
        match(option):
            case '1':
                print()
                print('All images have to be in the images folder')
                name = input('Image name: ')
                try:
                    img = cv.imread(f'./images/{name}', cv.IMREAD_UNCHANGED)
                    cv.imshow('Image', img)
                    k = cv.waitKey(0)
                except Exception:
                    print('Not a valid image file')
            case '2':
                censor_decensor('Censored')
            case '3':
                censor_decensor('Decensored')
            case '4':
                break
            case _:
                print()
                print('Invalid option')
