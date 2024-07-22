# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !!           BRIGHT LIGHT WARNING                !!
# !! WARNING  AVERTISSEMENT  警告  предупреждение  !!
# !!           Do not stare into the LED           !!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# Do not look directly into the LED light on the Isotope board.
# The light is very bright and can cause damage to your eyes.

import time
import isotope

DEBUG_ENABLED = False

# USB address of the Isotope board.
# For windows machine, this is usually "COMX" where X is the port number;
# for Ubuntu, this is usually "/dev/ttyACMX", where X is the port number;
# and for MacOS, this is usually "/dev/cu.usbmodemXXXXX".
usb_address = '/dev/cu.usbmodem2144101'


def disco_light(isot):
    # Rotate RGB light from red to rose, magenta, purple, blue, cyan, spring green, green, chartreuse, yellow, orange, red
    colors = [
        [255, 0, 0],
        [255, 0, 127],
        [255, 0, 255],
        [127, 0, 255],
        [0, 0, 255],
        [0, 127, 255],
        [0, 255, 255],
        [0, 255, 127],
        [0, 255, 0],
        [127, 255, 0],
        [255, 255, 0],
        [255, 127, 0],
    ]
    
    delay = 1
    delay_ut = 0.01
    delay_step = 0.02
    intensity = 0.1
    while True:
        for color in colors:
            isot.set_RGB_colour(intensity*color[0], intensity*color[1], intensity*color[2])
            time.sleep(delay)
            delay -= delay_step
            if delay < delay_ut:
                delay = delay_ut

def main():    
    # Start the communication
    isot = isotope.Isotope(usb_address, DEBUG_ENABLED, response_timeout=5)
    isot.connect()
    
    # Set the RGB colour to green 50% intensity
    isot.set_RGB_colour(0, 127, 0)
    time.sleep(1)
    
    # Set the RGB colour to green 100% intensity
    isot.set_RGB_colour(0, 255, 0)
    time.sleep(1)
    
    # Set the RGB colour to white 10% intensity
    isot.set_RGB_colour(25, 25, 25)
    time.sleep(1)
    
    # !!! SEIZURE WARNING !!!
    # disco_light() function will cause the RGB light to flash rapidly through a series of colours.
    # This may cause seizures in people with photosensitive epilepsy.
    # If you are sensitive to flashing lights, please do not uncomment and run this function.
    # However, it is fun to watch...
    
    # disco_light(isot)
    
    
    isot.disconnect()


if __name__ == "__main__":
    main()
