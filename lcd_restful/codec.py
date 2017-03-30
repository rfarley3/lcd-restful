# HD44780U table 4, ROM Code: A00
# a predecessor to shift_jisx0213 similar to https://en.wikipedia.org/wiki/JIS_X_0201
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
