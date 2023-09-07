This is my inicial idea follwing what @PradhyumR suggested.

You only have to run the project.py program.

It is a terminal menu driven program. You choose an option.

You will have to put your images in the images folder. I provided some there for our tests.

There is a key folder for the key files.

My idea was to XOR the image with random numbers generated with a seed and rectangular coordinates that we provide in the key file.
So we can censor an image and send it to someone else with the key file to decensor it.

The Key file structure is:
line 1: random seed number - any integer number
lines from 2 on: rectangular coordinates - xStart yStart xEnd yEnd

Some issues:

it only works for tiff images with no compression enabled. If we use ccompression, like in the jpeg file, the compression will change the XORED numbers and we can't get back the orginal file.

If we put the key info in the metadata for the image it can be exposed very easy by anyone with a photo program who reads the info from the image (almost all nowadays). Anad some systems we use to transfer the images take out the metadata, like Facebook and Whatsapp.
