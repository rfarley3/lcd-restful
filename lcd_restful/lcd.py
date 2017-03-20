from Adafruit_CharLCD import Adafruit_CharLCD as AdaLcd


class Lcd(AdaLcd):
    config = {
        'cols': 20,
        'rows': 4,
        'pwm': None,
        'rs': 25,  # LCD Pin 4
        'en': 24,  #         6
        'd4': 23,  #        11
        'd5': 17,  #        12
        'd6': 21,  #        13
        'd7': 22,  #        14
    }

    def __init__(self, config={}):
        super(Lcd, self).__init__(
            config.get('rs', self.config['rs']),
            config.get('en', self.config['en']),
            config.get('d4', self.config['d4']),
            config.get('d5', self.config['d5']),
            config.get('d6', self.config['d6']),
            config.get('d7', self.config['d7']),
            config.get('cols', self.config.get('cols', 20)),
            config.get('rows', self.config.get('rows', 4)),
            backlight=config.get('backlight'),
            gpio=config.get('gpio'),
            pwm=config.get('pwm'))
