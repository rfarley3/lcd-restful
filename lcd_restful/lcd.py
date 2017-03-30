from Adafruit_CharLCD import Adafruit_CharLCD as AdaLcd
from Adafruit_CharLCD import LCD_ENTRYLEFT



# HD44780U table 4, ROM Code: A00
# >>> bytes([c for c in range(32,255)]).decode('shift_jisx0213', "replace")
HITACHI_CHAR_MAP = (
    ' ' * 32 +
    ' !"#$%&\'()*+,-./' +
    '0123456789:;<=>?' +
    '@ABCDEFGHIJKLMNO' +
    'PQRSTUVWXYZ[¥]^_' +
    '`abcdefghijklmno' +  # gj should be above line
    'pqrstuvwxyz{|}→←' +  # pqy should be above line
    ' ' * 32 +
    ' ｡｢｣､･ｦｧｨｩｪｫｬｭｮｯ' +
    'ｰｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿ' +
    'ﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏ' +
    'ﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝ゛゜' +
    'αäβεμσρg√⁻jˣ¢£ñö' +  # ⁻ should be superscript -1
    'pqθ∞ΩüΣπxy千万円÷ █')  # + ' █') using x for x̄


def hitachi_utf_map():
    """Creates map, given an int 0..255 return a utf-8 chr"""
    mapping = {}
    for i, ch in enumerate(HITACHI_CHAR_MAP):
        mapping[i] = ch
    return mapping


def utf_hitachi_map():
    """Creates map, given an utf-8 chr return an int 0..255"""
    mapping = {}
    mapping[' '] = 32
    for i, ch in enumerate(HITACHI_CHAR_MAP[32:]):
        # use the first occurence of characters
        # NOTE this means gjpqy are technically the above line versions
        if ch != ' ' and ch not in mapping:
            mapping[ch] = i + 32
    # handle alternate mappings
    mapping['°'] = 222
    mapping['゜'] = 222
    mapping['ﾟ'] = 222
    mapping['ﾞ'] = 223
    mapping['゛'] = 223
    mapping['∑'] = 246
    mapping['x̄'] = 248
    return mapping


class Lcd(AdaLcd):
    config = {
        'cols': 20,
        'rows': 4,
        'pwm': None,
        'rs': 25,  # LCD Pin 4
        'en': 24,  # -       6
        'd4': 23,  # -      11
        'd5': 17,  # -      12
        'd6': 21,  # -      13
        'd7': 22,  # -      14
    }

    def __init__(self, config={}):
        self.config.update(config)
        super(Lcd, self).__init__(
            self.config['rs'],
            self.config['en'],
            self.config['d4'],
            self.config['d5'],
            self.config['d6'],
            self.config['d7'],
            self.config['cols'],
            self.config['rows'],
            backlight=self.config.get('backlight'),
            gpio=self.config.get('gpio'),
            pwm=self.config.get('pwm'))
        self.enc_map = utf_hitachi_map()
        self.dec_map = hitachi_utf_map()

    # def message(self, text):
    #     """Write text to display.  Note that text can include newlines."""
    #     line = 0
    #     # Iterate through each character.
    #     for char in text:
    #         # Advance to next line if character is a new line.
    #         if char == '\n':
    #             line += 1
    #             # Move to left or right side depending on text direction.
    #             col = 0 if self.displaymode & LCD_ENTRYLEFT > 0 else self._cols-1
    #             self.set_cursor(col, line)
    #         # Write the character to the display.
    #         else:
    #             self.write8(ord(char), True)

    def encode_map(self, utf_char):
        return self.enc_map.get(utf_char, ord(' '))
        # get as many values for free as possible:
        # MAYBE if none, then return utf_char.encode('shift_jisx0213')

    def decode_map(self, hitachi_byte):
        return self.dec_map.get(ord(hitachi_byte), ' ')

    def encode_char(self, utf_char):
        # the custom chars are stored as 0-7
        if ord(utf_char) < 8:
            return ord(utf_char)
        # new lines should pass through for message to parse
        if utf_char == '\n':
            # TODO handle \r
            return '\n'
        # catch the out of range chars
        unknown_ch_byte = '?'.encode('shift_jisx0213')
        if ord(utf_char) < 32 or ord(utf_char) > 255:
            return ord(unknown_ch_byte)
        if ord(utf_char) > 127 and ord(utf_char) < 161:
            return ord(' ')  # TODO determine LCD actual behavior for this range
            # return ord(unknown_ch_byte)
        return self.encode_map(utf_char)

    def encode(self, utf_str, strict=True):
        ret_str = ''
        for ch in utf_str:
            ret_str += chr(self.encode_char(ch))
        return ret_str

    def decode(self, bytes_arr):
        # return unicode str
        # TODO
        return bytes_arr.decode('shift_jisx0213')

