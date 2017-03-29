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

    def encode(self, unicode_str, strict=True):
        # return bytes
        # HD44780U table 4, ROM Code: A00
        # encode_map = (32, ' !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[
        # >>> bytes([c for c in range(32,255)]).decode('shift_jisx0213', "replace")
        # ' !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[¥]^_`abcdefghijklmnopqrstuvwxyz{|}‾\x7f�≠ヤð㊧炎旧克署葬灯楓利劒屆撼泛｡｢｣､･ｦｧｨｩｪｫｬｭｮｯｰｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝﾞﾟ珮粤蒟跚韜挘眙鄯帕戩湌稑薓錑���'`
        def alt_chars(ch):
            base = 222
            simple_map = '° ゙'
            # simple_map += 'αäβεμσρg√-1jˣ¢£ñö'
            simple_map += 'αäβεμσρ √  ˣ¢£ñö'
            # simple_map += 'pqθ∞ΩüΣπx̄y千万円÷ █'
            simple_map += '  θ∞ΩüΣπx̄ 千万円÷ █'
            for i, ch in enumerate(simple_map):
                if ch != ' ':
                    encode_map[ch] = base + i
            # map in alternate encodings
            encode_map['°'] = 222
            encode_map['゜'] = 222
            encode_map['゛'] = 223
            encode_map['∑'] = 246
            return encode_map.get(ch)
        ctrl_ch_byte = '^'.encode('shift_jisx0213')
        unknown_ch_byte = '?'.encode('shift_jisx0213')
        ret_bytes = b''
        for ch in unicode_str:
            jis_byte = ch.encode('shift_jisx0213')
            jis_ord = ord(jis_byte)
            if jis_ord == 10:
                ret_bytes += jis_byte
            elif jis_ord < 32:
                ret_bytes += ctrl_ch_byte
            # NOTE 126 is -> and 127 is <-
            elif jis_ord < 128:
                ret_bytes += jis_byte
            elif jis_ord < 161:
                ret_bytes += unknown_ch_byte
            elif jis_ord < 222:
                ret_bytes += jis_byte
            elif jis_ord > 255:
                ret_bytes += unknown_ch_byte
            else:  # 222 to 255
                ret_bytes += alt_chars(ch)
        return ret_bytes

    def decode(self, bytes_arr):
        # return unicode str
        # TODO
        return bytes_arr.decode('shift_jisx0213')

