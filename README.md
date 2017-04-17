https://learn.adafruit.com/character-lcd-with-raspberry-pi-or-beaglebone-black/usage

NOTE The old Adafruit wiring used different pins
LCD Pinout: https://www.engineersgarage.com/sites/default/files/Lcd_0.jpg
  GND Vcc Vee RS RW EN DB0 1  2  3  4  5  6  7  Vled GNDled
  1   2   3   4  5  6  7   8  9  10 11 12 13 14 15   16

Install dependencies:
Make sure you are in a Python3 virtualenv
# git clone https://github.com/adafruit/Adafruit_Python_CharLCD.git
# cd Adafruit_Python_CharLCD
# Apply patch (Adafruit_CharLCD.patch in root of this repo)
# pip install .

Clone git clone git@github.com:dbrgn/RPLCD.git
Until RPLCD dependency updates from 0.4.0, use repo clone, tested on 3c3a486

