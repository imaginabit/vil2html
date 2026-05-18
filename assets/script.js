/* ── US baseline keycode → display label ── */
const US_KC = {
  KC_TRNS:'▽', KC_NO:'',
  KC_SPACE:'Space', KC_SPC:'Space', KC_BSPACE:'⌫', KC_BSPC:'⌫',
  KC_ENTER:'↩', KC_ENT:'↩', KC_TAB:'Tab', KC_ESC:'Esc', KC_GESC:'Esc',
  KC_DELETE:'Del', KC_DEL:'Del',
  KC_LSFT:'Shift', KC_RSFT:'Shift', KC_LALT:'Alt', KC_RALT:'AltGr',
  KC_LCTL:'Ctrl', KC_RCTL:'Ctrl', KC_LGUI:'⊞', KC_RGUI:'⊞',
  KC_LEFT:'←', KC_RIGHT:'→', KC_UP:'↑', KC_DOWN:'↓',
  KC_HOME:'Home', KC_END:'End', KC_PGUP:'PgUp', KC_PGDOWN:'PgDn', KC_PGDN:'PgDn',
  KC_SCOLON:';', KC_SCLN:';', KC_COMMA:',', KC_COMM:',',
  KC_DOT:'.', KC_SLASH:'/', KC_SLSH:'/',
  KC_MINUS:'-', KC_MINS:'-', KC_EQUAL:'=', KC_EQL:'=',
  KC_LBRACKET:'[', KC_LBRC:'[', KC_RBRACKET:']', KC_RBRC:']',
  KC_BSLASH:'\\', KC_BSLS:'\\', KC_QUOTE:"'", KC_QUOT:"'",
  KC_GRAVE:'`', KC_GRV:'`', KC_NONUS_BSLASH:'<',
  KC_VOLU:'Vol+', KC_VOLD:'Vol-', KC_MUTE:'Mute', KC_KP_SLASH:'KP/',
  KC_PSCREEN:'PrtSc', KC_PSCR:'PrtSc', KC_COPY:'Copy', KC_PSTE:'Paste',
};
for (let i=1;i<=12;i++) US_KC['KC_F'+i]='F'+i;
for (let i=0;i<=9;i++) US_KC['KC_'+i]=String(i);

/* ── US shifted characters (for LSFT combos) ── */
const US_SHIFT = {
  KC_GRAVE:'~', KC_MINUS:'_', KC_EQUAL:'+',
  KC_LBRACKET:'{', KC_RBRACKET:'}', KC_BSLASH:'|',
  KC_SCOLON:':', KC_QUOTE:'"', KC_SLASH:'?', KC_NONUS_BSLASH:'>',
  KC_1:'!', KC_2:'@', KC_3:'#', KC_4:'$', KC_5:'%',
  KC_6:'^', KC_7:'&', KC_8:'*', KC_9:'(', KC_0:')',
  KC_COMMA:'<', KC_DOT:'>',
};

/* ── Layout override tables ── */
const LAYOUTS = {
  US: { name:'US ANSI',       plain:{}, shift:{}, altgr:{} },
  ES: {
    name:'Español (ES)',
    plain: {
      KC_GRAVE:'º',   KC_MINUS:"'",  KC_EQUAL:'¡',
      KC_LBRACKET:'`',KC_RBRACKET:'+',KC_BSLASH:'ç',
      KC_SCOLON:'ñ',  KC_QUOTE:'´',  KC_NONUS_BSLASH:'<', KC_SLASH:'-',
    },
    shift: {
      KC_GRAVE:'ª',   KC_MINUS:'?',  KC_EQUAL:'¿',
      KC_LBRACKET:'^',KC_RBRACKET:'*',KC_BSLASH:'Ç',
      KC_SCOLON:'Ñ',  KC_QUOTE:'¨',  KC_NONUS_BSLASH:'>',KC_SLASH:'_',
      KC_2:'"', KC_3:'·', KC_6:'&', KC_7:'/', KC_8:'(', KC_9:')', KC_0:'=',
    },
    altgr: {
      KC_GRAVE:'\\',  KC_LBRACKET:'[',KC_RBRACKET:']',
      KC_BSLASH:'}',  KC_QUOTE:'{',   KC_NONUS_BSLASH:'|',
      KC_1:'|', KC_2:'@', KC_3:'#',   KC_4:'~',
    },
  },
  UK: {
    name:'UK',
    plain: { KC_NONUS_BSLASH:'\\', KC_BSLASH:'#' },
    shift: { KC_2:'"', KC_3:'£',   KC_BSLASH:'~', KC_NONUS_BSLASH:'|' },
    altgr: { KC_4:'€' },
  },
  DE: {
    name:'Deutsch (DE)',
    plain: {
      KC_Y:'z',      KC_Z:'y',
      KC_GRAVE:'^',  KC_MINUS:'ß',  KC_EQUAL:'´',
      KC_LBRACKET:'ü',KC_RBRACKET:'+',KC_BSLASH:'#',
      KC_SCOLON:'ö', KC_QUOTE:'ä',  KC_NONUS_BSLASH:'<', KC_SLASH:'-',
    },
    shift: {
      KC_Y:'Z',      KC_Z:'Y',
      KC_GRAVE:'°',  KC_MINUS:'?',  KC_EQUAL:'`',
      KC_LBRACKET:'Ü',KC_RBRACKET:'*',KC_BSLASH:"'",
      KC_SCOLON:'Ö', KC_QUOTE:'Ä',  KC_NONUS_BSLASH:'>',KC_SLASH:'_',
      KC_2:'"', KC_3:'§', KC_6:'&', KC_7:'/', KC_8:'(', KC_9:')', KC_0:'=',
    },
    altgr: {
      KC_Q:'@', KC_E:'€', KC_2:'²', KC_3:'³',
      KC_7:'{', KC_8:'[', KC_9:']', KC_0:'}',
      KC_MINUS:'\\', KC_RBRACKET:'~', KC_NONUS_BSLASH:'|',
    },
  },
  FR: {
    name:'Français (FR)',
    plain: {
      KC_GRAVE:'²',
      KC_1:'&', KC_2:'é', KC_3:'"',  KC_4:"'", KC_5:'(', KC_6:'-',
      KC_7:'è', KC_8:'_', KC_9:'ç',  KC_0:'à', KC_MINUS:')', KC_EQUAL:'=',
      KC_Q:'a', KC_W:'z', KC_LBRACKET:'^',KC_RBRACKET:'$',
      KC_A:'q', KC_SCOLON:'m', KC_QUOTE:'ù', KC_BSLASH:'*',
      KC_NONUS_BSLASH:'<',
      KC_Z:'w', KC_M:',', KC_COMMA:';', KC_DOT:':', KC_SLASH:'!',
    },
    shift: {
      KC_1:'1', KC_2:'2', KC_3:'3',  KC_4:'4', KC_5:'5', KC_6:'6',
      KC_7:'7', KC_8:'8', KC_9:'9',  KC_0:'0', KC_MINUS:'°', KC_EQUAL:'+',
      KC_Q:'A', KC_W:'Z', KC_LBRACKET:'¨',KC_RBRACKET:'£',
      KC_A:'Q', KC_SCOLON:'M', KC_QUOTE:'%', KC_BSLASH:'µ',
      KC_NONUS_BSLASH:'>',
      KC_Z:'W', KC_M:'?', KC_COMMA:'.', KC_DOT:'/', KC_SLASH:'§',
    },
    altgr: {
      KC_0:'@', KC_3:'#', KC_4:'{', KC_5:'[', KC_6:'|',
      KC_7:'`', KC_8:'\\', KC_9:'^', KC_MINUS:']', KC_EQUAL:'}', KC_E:'€',
    },
  },
};

const MOD_J = {
  LALT:'Alt', RALT:'Ag', LSFT:'Sft', RSFT:'Sft',
  LCTL:'Ctl', RCTL:'Ctl', LGUI:'⊞',  RGUI:'⊞',
};
const SPECIALS = new Set(['KC_SPACE','KC_SPC','KC_BSPACE','KC_BSPC','KC_ENTER','KC_ENT','KC_TAB','KC_ESC','KC_GESC','KC_DELETE','KC_DEL']);
const MODKEYS  = new Set(['KC_LSFT','KC_RSFT','KC_LALT','KC_RALT','KC_LCTL','KC_RCTL','KC_LGUI','KC_RGUI']);

function kcLabel(code, lid) {
  const p = LAYOUTS[lid]?.plain;
  if (p && p[code] !== undefined) return p[code];
  return US_KC[code] !== undefined ? US_KC[code] : code.replace(/^KC_/,'');
}
function shiftOf(code, lid) {
  const s = LAYOUTS[lid]?.shift;
  if (s && s[code] !== undefined) return s[code];
  if (US_SHIFT[code] !== undefined) return US_SHIFT[code];
  const plain = kcLabel(code, lid);
  return /^[a-zA-Z]$/.test(plain) ? plain.toUpperCase() : '⇧'+plain;
}
function altgrOf(code, lid) {
  const a = LAYOUTS[lid]?.altgr;
  return (a && a[code] !== undefined) ? a[code] : null;
}

function parseKey(raw, lid) {
  if (raw === '-1' || raw === -1) return {tap:'', hold:'', cls:'none'};
  if (raw === 'KC_TRNS') return {tap:'▽', hold:'', cls:'trns'};
  if (raw === 'KC_NO')   return {tap:'',  hold:'', cls:'empty'};

  let m;
  // Mod-tap
  if ((m = raw.match(/^([A-Z]+)_T\((.+)\)$/)))
    return {tap: kcLabel(m[2],lid), hold: MOD_J[m[1]]||m[1], cls:'modtap'};
  // Layer-tap
  if ((m = raw.match(/^LT(\d+)\((.+)\)$/)))
    return {tap: kcLabel(m[2],lid), hold:'L'+m[1], cls:'layertap'};
  // Ctrl+Shift
  if ((m = raw.match(/^C_S\((.+)\)$/)))
    return {tap:'C+S '+kcLabel(m[1],lid), hold:'', cls:'combo'};
  // Single modifier wrapper
  if ((m = raw.match(/^([A-Z]+)\((.+)\)$/))) {
    const [,fn,inner] = m;
    if (fn==='LSFT'||fn==='RSFT') return {tap: shiftOf(inner,lid), hold:'', cls:'combo'};
    if (fn==='RALT'||fn==='LALT') {
      const ag = altgrOf(inner,lid);
      return {tap: ag!==null ? ag : 'Ag+'+kcLabel(inner,lid), hold:'', cls:'combo'};
    }
    const pfx = {RCTL:'C+',LCTL:'C+',RGUI:'⊞+',LGUI:'⊞+'}[fn]||fn+'+';
    return {tap: pfx+kcLabel(inner,lid), hold:'', cls:'combo'};
  }
  // Plain
  const label = kcLabel(raw, lid);
  const cls = MODKEYS.has(raw) ? 'modifier' : /^KC_F\d+$/.test(raw) ? 'func' : SPECIALS.has(raw) ? 'special' : 'normal';
  return {tap: label, hold:'', cls};
}

function applyLayout(lid) {
  document.querySelectorAll('.layout-btn').forEach(b => b.classList.remove('active'));
  const btn = document.getElementById('layout-'+lid);
  if (btn) btn.classList.add('active');

  document.querySelectorAll('.key[data-raw]').forEach(el => {
    const raw = el.dataset.raw;
    if (!raw) return;
    const {tap, hold, cls} = parseKey(raw, lid);
    el.className = 'key ' + cls;

    let te = el.querySelector('.tap');
    if (!te) { te = document.createElement('span'); te.className='tap'; el.prepend(te); }
    te.textContent = tap;

    let he = el.querySelector('.hold');
    if (hold) {
      if (!he) { he = document.createElement('span'); he.className='hold'; el.appendChild(he); }
      he.textContent = hold;
    } else if (he) { he.remove(); }
  });
}

function show(n) {
  document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.getElementById('p'+n).classList.add('active');
  document.getElementById('t'+n).classList.add('active');
}
