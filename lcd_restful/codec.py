# coding=utf-8
"""Provides encoding from UTF characters to HD44780U-A00 and back again"""


class HitachiEncodeError(BaseException):
    pass


class HitachiDecodeError(BaseException):
    pass


# HD44780U datasheet table 4, ROM Code: A00
# a predecessor to shift_jisx0213 similar to
#    https://en.wikipedia.org/wiki/JIS_X_0201
# >>> bytes([c for c in range(32,255)]).decode('shift_jisx0213', "replace")
# 2.1.1. JIS X 0201 http://www.sljfaq.org/afaq/encodings.html
#    #encodings-Overview-of-the-encoding-schemes
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
    'ﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝ゛゜' +  # TODO find 1/2 width ゛゜
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
    # NOTE you probably don't mean to use chr(<some int>) as a key
    #   for instance: chr(HITACHI_CHAR_MAP.index('¥')) == '\'
    #   and mapping['\\'] does not exist
    #   also fails when (eg ¢,£) char has different ord in utf vs this encoding
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


def decode_char(hitachi_byte):
    utf_char = decoding_map.get(hitachi_byte)
    if utf_char is None:
        raise HitachiDecodeError(
            'Invalid or char not in hitachi mapping: \'%s\'' %
            hitachi_byte)
    return utf_char


def encode_char(utf_char):
    # the custom chars are stored as 0-7
    if ord(utf_char) < 8:
        return ord(utf_char)
    # assumes no newlines
    # TODO test for newlines?
    if ord(utf_char) < 32:
        return 32
    hitachi_val = encoding_map.get(utf_char)
    if hitachi_val is None:
        raise HitachiEncodeError(
            'Invalid or not found input char: \'%s\' with utf ord: %s' %
            (utf_char, ord(utf_char)))
    return hitachi_val


encoding_map = utf_hitachi_map()
decoding_map = hitachi_utf_map()

