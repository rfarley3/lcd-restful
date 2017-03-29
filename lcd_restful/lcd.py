from Adafruit_CharLCD import Adafruit_CharLCD as AdaLcd


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
        self.enc_map = None
        self.dec_map = None

    def encode_map(self, utf_char):
        if self.enc_map is None:
            self.make_enc_map()
        return self.enc_map.get(utf_char, ord(' '))
        # get as many values for free as possible:
        # MAYBE if none, then return utf_char.encode('shift_jisx0213')

    def decode_map(self, hitachi_byte):
        if self.dec_map is None:
            self.make_dec_map()
        return self.dec_map.get(ord(hitachi_byte), ' ')

    def make_dec_map(self):
        self.dec_map = {}
        base = 32
        simple_map = ' !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[¥]^_`abcdefghijklmnopqrstuvwxyz{|}‾'
        for i, ch in enumerate(simple_map):
            if ch != ' ':
                self.dec_map[base + i] = ch
        # TODO \x7e -> self.enc_map[126] = ->
        # TODO \x7f <- self.enc_map[127] = <-
        base = 161
        simple_map = '｡｢｣､･ｦｧｨｩｪｫｬｭｮｯｰｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝﾞﾟ'
        for i, ch in enumerate(simple_map):
            if ch != ' ':
                self.dec_map[base + i] = ch
        base = 222
        simple_map = '° ゙'
        # simple_map += 'αäβεμσρg√-1jˣ¢£ñö'
        simple_map += 'αäβεμσρg√ jˣ¢£ñö'
        # simple_map += 'pqθ∞ΩüΣπx̄y千万円÷ █'
        simple_map += 'pqθ∞ΩüΣπx̄y千万円÷ █'
        for i, ch in enumerate(simple_map):
            if ch != ' ':
                self.dec_map[base + i] = ch


    def make_enc_map(self):
        self.enc_map = {}
        # HD44780U table 4, ROM Code: A00
        # encode_map = (32, ' !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[
        # >>> bytes([c for c in range(32,255)]).decode('shift_jisx0213', "replace")
        # ≠ヤð㊧炎旧克署葬灯楓利劒屆撼泛
        # 珮粤蒟跚韜挘眙鄯帕戩湌稑薓錑���'`
        base = 32
        simple_map = ' !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[¥]^_`abcdefghijklmnopqrstuvwxyz{|}‾'
        for i, ch in enumerate(simple_map):
            if ch != ' ':
                self.enc_map[ch] = base + i
        # TODO \x7e -> self.enc_map[''] = 126
        # TODO \x7f <- self.enc_map[''] = 127
        base = 161
        simple_map = '｡｢｣､･ｦｧｨｩｪｫｬｭｮｯｰｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝﾞﾟ'
        for i, ch in enumerate(simple_map):
            if ch != ' ':
                self.enc_map[ch] = base + i
        base = 222
        simple_map = '° ゙'
        # simple_map += 'αäβεμσρg√-1jˣ¢£ñö'
        simple_map += 'αäβεμσρ √  ˣ¢£ñö'
        # simple_map += 'pqθ∞ΩüΣπx̄y千万円÷ █'
        simple_map += '  θ∞ΩüΣπx̄ 千万円÷ █'
        for i, ch in enumerate(simple_map):
            if ch != ' ':
                self.enc_map[ch] = base + i
        # map in alternate encodings
        self.enc_map['°'] = 222
        self.enc_map['゜'] = 222
        self.enc_map['ﾟ'] = 222
        self.enc_map['ﾞ'] = 223
        self.enc_map['゛'] = 223
        self.enc_map['∑'] = 246

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

