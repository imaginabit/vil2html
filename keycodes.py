"""Keycode mapping and parsing.

Pure logic for translating QMK/Vial keycode strings into display labels
and a semantic class. No HTML generation here.
"""

import re

# Keycode -> display label mapping
KC_MAP = {
    'KC_TRNS': '▽', 'KC_NO': '',
    'KC_SPACE': 'Space', 'KC_SPC': 'Space',
    'KC_BSPACE': '⌫', 'KC_BSPC': '⌫',
    'KC_ENTER': '↩', 'KC_ENT': '↩',
    'KC_TAB': 'Tab', 'KC_ESC': 'Esc', 'KC_GESC': 'Esc',
    'KC_DELETE': 'Del', 'KC_DEL': 'Del',
    'KC_LSFT': 'Shift', 'KC_RSFT': 'Shift',
    'KC_LALT': 'Alt', 'KC_RALT': 'AltGr',
    'KC_LCTL': 'Ctrl', 'KC_RCTL': 'Ctrl',
    'KC_LGUI': '⊞', 'KC_RGUI': '⊞',
    'KC_LEFT': '←', 'KC_RIGHT': '→', 'KC_UP': '↑', 'KC_DOWN': '↓',
    'KC_HOME': 'Home', 'KC_END': 'End',
    'KC_PGUP': 'PgUp', 'KC_PGDOWN': 'PgDn', 'KC_PGDN': 'PgDn',
    'KC_SCOLON': ';', 'KC_SCLN': ';',
    'KC_COMMA': ',', 'KC_COMM': ',',
    'KC_DOT': '.', 'KC_SLASH': '/', 'KC_SLSH': '/',
    'KC_MINUS': '-', 'KC_MINS': '-',
    'KC_EQUAL': '=', 'KC_EQL': '=',
    'KC_LBRACKET': '[', 'KC_LBRC': '[',
    'KC_RBRACKET': ']', 'KC_RBRC': ']',
    'KC_BSLASH': '\\', 'KC_BSLS': '\\',
    'KC_QUOTE': "'", 'KC_QUOT': "'",
    'KC_GRAVE': '`', 'KC_GRV': '`',
    'KC_NONUS_BSLASH': '<',
    'KC_VOLU': 'Vol+', 'KC_VOLD': 'Vol-', 'KC_MUTE': 'Mute',
    'KC_KP_SLASH': 'KP/',
    'KC_PSCREEN': 'PrtSc', 'KC_PSCR': 'PrtSc',
    'KC_COPY': 'Copy', 'KC_PSTE': 'Paste', 'KC_CUT': 'Cut',
    **{f'KC_F{i}': f'F{i}' for i in range(1, 25)},
    **{f'KC_{i}': str(i) for i in range(10)},
}

# Modifier short forms used in mod-tap hold labels
MOD_SHORT = {
    'LALT': 'Alt', 'RALT': 'Ag', 'LSFT': 'Sft', 'RSFT': 'Sft',
    'LCTL': 'Ctl', 'RCTL': 'Ctl', 'LGUI': '⊞',  'RGUI': '⊞',
}

_MODIFIER_KEYS = {
    'KC_LSFT', 'KC_RSFT', 'KC_LALT', 'KC_RALT',
    'KC_LCTL', 'KC_RCTL', 'KC_LGUI', 'KC_RGUI',
}
_SPECIAL_KEYS = {
    'KC_SPACE', 'KC_SPC', 'KC_BSPACE', 'KC_BSPC',
    'KC_ENTER', 'KC_ENT', 'KC_TAB',
    'KC_ESC', 'KC_GESC', 'KC_DELETE', 'KC_DEL',
}

_SINGLE_MOD_PREFIX = {
    'LSFT': '⇧', 'RSFT': '⇧',
    'RALT': 'Ag+', 'LALT': 'Al+',
    'RCTL': 'C+', 'LCTL': 'C+',
    'RGUI': '⊞+', 'LGUI': '⊞+',
}


def kc(code):
    """Return the display label for a raw keycode."""
    return KC_MAP.get(code, re.sub(r'^KC_', '', code))


def parse(raw):
    """Parse a raw keycode into ``(tap_label, hold_label, css_class)``."""
    if raw == -1:        return '',  '',   'none'
    if raw == 'KC_TRNS': return '▽', '',   'trns'
    if raw == 'KC_NO':   return '',  '',   'empty'

    # Mod-tap: LALT_T(KC_F) -> (key, mod, 'modtap')
    m = re.fullmatch(r'([A-Z]+)_T\((.+)\)', raw)
    if m:
        return kc(m[2]), MOD_SHORT.get(m[1], m[1]), 'modtap'

    # Layer-tap: LT2(KC_SPACE) -> (key, layer#, 'layertap')
    m = re.fullmatch(r'LT(\d+)\((.+)\)', raw)
    if m:
        return kc(m[2]), f'L{m[1]}', 'layertap'

    # Ctrl+Shift combo: C_S(KC_P) -> ('C+S K', '', 'combo')
    m = re.fullmatch(r'C_S\((.+)\)', raw)
    if m:
        return f'C+S {kc(m[1])}', '', 'combo'

    # Single modifier wrapper: LSFT(KC_1), RALT(KC_GRAVE), RCTL(KC_J) ...
    m = re.fullmatch(r'([A-Z]+)\((.+)\)', raw)
    if m:
        pfx = _SINGLE_MOD_PREFIX.get(m[1], m[1] + '+')
        return f'{pfx}{kc(m[2])}', '', 'combo'

    # Plain keycode
    label = kc(raw)
    if raw in _MODIFIER_KEYS:
        return label, '', 'modifier'
    if re.match(r'KC_F\d+$', raw):
        return label, '', 'func'
    if raw in _SPECIAL_KEYS:
        return label, '', 'special'
    return label, '', 'normal'
