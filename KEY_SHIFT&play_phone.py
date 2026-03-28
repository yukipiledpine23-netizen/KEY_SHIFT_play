# 20260326

import streamlit as st
import os
import re
import streamlit.components.v1 as components

# --- 1. ブラウザ・ページ基本設定 ---
st.set_page_config(page_title="VOICE TUNER NEO", layout="centered")

# --- 2. UI カスタマイズ (CSS) ---
st.markdown("""
    <style>
    .stApp { background-color: #0e0e10 !important; color: #e1e1e3 !important; }

    /* セレクトボックスの赤枠・重なりを徹底排除 */
    div[data-baseweb="select"] { 
        border: 1px solid #3a3a3c !important; 
        background-color: #1c1c1f !important;
        box-shadow: none !important;
    }
    div[data-baseweb="select"] > div {
        border: none !important;
        box-shadow: none !important;
        outline: none !important;
    }
    div[data-baseweb="select"]:focus-within {
        border-color: #00d4ff !important;
        box-shadow: 0 0 10px rgba(0, 212, 255, 0.2) !important;
    }

    header {visibility: hidden;}
    .main .block-container { padding-top: 2rem; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. ロジック関数群 ---
def list_txt_files():
    return sorted([f for f in os.listdir('.') if f.endswith('.txt') and f != 'requirements.txt'])

def get_base_notes_with_structure(filename):
    if not filename: return [], ""
    note_map = {
        'ド': 0, 'レ': 2, 'ミ': 4, 'ファ': 5, 'ソ': 7, 'ラ': 9, 'シ': 11,
        'ど': 0, 'れ': 2, 'み': 4, 'ふぁ': 5, 'そ': 7, 'ら': 9, 'し': 11,
        'do': 0, 're': 2, 'mi': 4, 'fa': 5, 'so': 7, 'ra': 9, 'si': 11, 'ti': 11,
        'c': 0, 'd': 2, 'e': 4, 'f': 5, 'g': 7, 'a': 9
    }
    try:
        with open(filename, "r", encoding="utf-8") as f:
            original_text = f.read()
    except:
        return [], ""

    clean_text = original_text.lower().replace("ー", "")
    pattern = r"([ァ-ヶぁ-ん]{1,2}|[a-z]{1,2})([#b♭＃＃]?)([0-9])([#b♭＃＃]?)"
    matches = re.finditer(pattern, clean_text)
    base_data = []
    for m in matches:
        name_part = m.group(1)
        acc = m.group(2) if m.group(2) else m.group(4)
        oct_str = m.group(3)
        if name_part in note_map:
            base_val = note_map[name_part]
            adj = 1 if acc in ['#', '＃'] else -1 if acc in ['b', '♭'] else 0
            base_data.append({"abs_pos": int(oct_str) * 12 + base_val + adj})
    return base_data, original_text

# --- 4. メイン実行部 ---
txt_files = list_txt_files()
selected_file = st.selectbox("SELECT TRACK", txt_files, label_visibility="collapsed") if txt_files else None

if selected_file:
    data, raw_text = get_base_notes_with_structure(selected_file)

    if data:
        notes_json = str(data).replace("'", '"')
        safe_raw_text = raw_text.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${").replace("\n", "\\n")

        html_code = f"""
        <div style="background-color:#0e0e10; color:#e1e1e3; font-family:'Segoe UI', Roboto, sans-serif; max-width:500px; margin:auto; padding:15px; border:1px solid #2d2d30; border-radius:24px; box-shadow: 0 15px 40px rgba(0,0,0,0.6); box-sizing: border-box;">

            <div style="text-align:center; padding:15px 0 20px 0; user-select: none;">
                <h2 style="letter-spacing:12px; font-weight:200; color:#00d4ff; margin:0; font-size:14px; opacity:0.8; display:inline-block; position:relative; padding-bottom:12px;">
                    VOICE TUNER NEO
                    <span style="position:absolute; bottom:0; left:50%; transform:translateX(-50%); width:240px; height:1px; background:linear-gradient(90deg, transparent, #00d4ff, transparent); opacity:0.4;"></span>
                </h2>
            </div>

            <div style="display:flex; align-items:center; background:#1c1c1f; border-radius:14px; padding:6px; margin-bottom:18px; border:1px solid #3a3a3c; user-select: none;">
                <button onclick="changeKey(-1)" style="width:55px; height:55px; border:none; background:transparent; color:#00d4ff; font-size:24px; cursor:pointer; outline:none; -webkit-tap-highlight-color: transparent;">➖</button>
                <div id="key-val" style="flex:1; text-align:center; font-weight:bold; font-size:13px; color:#ffb74d; letter-spacing:2px;">KEY: 0</div>
                <button onclick="changeKey(1)" style="width:55px; height:55px; border:none; background:transparent; color:#00d4ff; font-size:24px; cursor:pointer; outline:none; -webkit-tap-highlight-color: transparent;">➕</button>
            </div>

            <div onclick="playCurrent()" style="background:linear-gradient(145deg, #161618, #1c1c1f); border:1px solid #3a3a3c; border-radius:18px; padding:65px 0 55px 0; text-align:center; margin-bottom:18px; cursor:pointer; position:relative; overflow:hidden; user-select: none; -webkit-user-select: none; -webkit-tap-highlight-color: transparent;">
                <p style="font-size:13px; color:#555; letter-spacing:3px; position:absolute; top:18px; width:100%;">TAP TO NEXT ▶</p>
                <h1 id="display-note" style="font-size:95px; color:#fff; text-shadow: 0 0 25px rgba(0,212,255,0.4); margin:0; font-weight:100; line-height:0.8; display:block;">--</h1>
            </div>

            <div style="display:flex; gap:12px; margin-bottom:28px; user-select: none;">
                <button onclick="resetApp()" style="flex:1; height:52px; border-radius:12px; border:1px solid #3a3a3c; background:linear-gradient(180deg, #2a2a2e, #1c1c1f); color:#bbb; font-size:13px; font-weight:600; cursor:pointer; display:flex; align-items:center; justify-content:center; gap:6px; outline:none; -webkit-tap-highlight-color: transparent;">
                    |< 最初へ
                </button>
                <button onclick="prevNote()" style="flex:1; height:52px; border-radius:12px; border:1px solid #3a3a3c; background:linear-gradient(180deg, #2a2a2e, #1c1c1f); color:#bbb; font-size:13px; font-weight:600; cursor:pointer; display:flex; align-items:center; justify-content:center; gap:6px; outline:none; -webkit-tap-highlight-color: transparent;">
                    ◀ 戻る
                </button>
            </div>

            <div style="background:#161618; border-radius:14px; padding:18px; border:1px solid #2d2d30;">
                <div style="margin-bottom:18px;">
                    <span style="font-size:10px; color:#d1d1d6; letter-spacing:1px; font-weight:bold; opacity:0.8; user-select: none;">キー変更後</span>
                    <div id="after-list" style="color:#d1d1d6; font-size:14px; white-space:pre-wrap; line-height:1.8; max-height:150px; overflow-y:auto; padding:10px; margin-top:8px; border:1px solid #2d2d30; border-radius:6px; background:#0e0e10; user-select: text;"></div>
                </div>
                <div>
                    <span style="font-size:10px; color:#444; letter-spacing:1px; font-weight:bold; opacity:0.8; user-select: none;">キー変更前</span>
                    <div id="before-list" style="color:#444; font-size:14px; white-space:pre-wrap; line-height:1.8; max-height:150px; overflow-y:auto; padding:10px; margin-top:8px; border:1px solid #2d2d30; border-radius:6px; background:#0e0e10; user-select: text;"></div>
                </div>
            </div>

            <div style="text-align:center; padding:20px 0 5px 0; font-size:9px; color:#3a3a3c; letter-spacing:3px; user-select: none;">
                DEVELOPED BY 鷺城流
            </div>
        </div>

        <script>
        const baseData = {notes_json};
        const rawText = `{safe_raw_text}`;
        const valToNote = ["ド", "ド#", "レ", "レ#", "ミ", "ファ", "ファ#", "ソ", "ソ#", "ラ", "ラ#", "シ"];
        let currentKey = 0, currentIndex = 0, audioCtx = null, masterGain = null, activeNodes = [];

        function initAudio() {{ 
            if (!audioCtx) {{ 
                audioCtx = new (window.AudioContext || window.webkitAudioContext)(); 
                masterGain = audioCtx.createGain(); 
                masterGain.gain.setValueAtTime(1.5, audioCtx.currentTime); 
                const comp = audioCtx.createDynamicsCompressor(); 
                masterGain.connect(comp); comp.connect(audioCtx.destination); 
            }} 
        }}

        function updateDisplay() {{
            if (!baseData[currentIndex]) return;
            const pos = baseData[currentIndex].abs_pos + currentKey;
            document.getElementById('display-note').innerText = valToNote[((pos % 12) + 12) % 12] + Math.floor(pos / 12);
            document.getElementById('key-val').innerText = "KEY: " + (currentKey > 0 ? "+" : "") + currentKey;
            updateLists();
        }}

        function updateLists() {{
            const pattern = /([ァ-ヶぁ-ん]{{1,2}}|[a-z]{{1,2}})([#b♭＃＃]?)([0-9])([#b♭＃＃]?)/gi;
            const replaceFunc = (isAfter) => {{
                let count = 0;
                return rawText.split('\\n').map(line => line.replace(pattern, (match) => {{
                    const idx = count++; if (!baseData[idx]) return match;
                    let txt = match;
                    if (isAfter) {{ const pos = baseData[idx].abs_pos + currentKey; txt = valToNote[((pos % 12) + 12) % 12] + Math.floor(pos / 12); }}
                    let style = idx === currentIndex ? "color:#00d4ff; font-weight:bold; border-bottom:1px solid #00d4ff;" : "";
                    return `<span style="${{style}}">${{txt}}</span>`;
                }})).join('\\n');
            }};
            document.getElementById('after-list').innerHTML = replaceFunc(true);
            document.getElementById('before-list').innerHTML = replaceFunc(false);
        }}

        function playCurrent() {{
            initAudio(); if (audioCtx.state === 'suspended') audioCtx.resume();
            activeNodes.forEach(n => {{ try {{ n.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.05); }} catch(e) {{}} }}); activeNodes = [];
            const pos = baseData[currentIndex].abs_pos + currentKey, freq = 440 * Math.pow(2, (pos - 57) / 12);
            const createTone = (f, vol, decay) => {{
                const osc = audioCtx.createOscillator(); const g = audioCtx.createGain();
                osc.type = 'sine'; osc.frequency.setValueAtTime(f, audioCtx.currentTime);
                g.gain.setValueAtTime(0, audioCtx.currentTime); g.gain.linearRampToValueAtTime(vol, audioCtx.currentTime + 0.005);
                g.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + decay);
                osc.connect(g); g.connect(masterGain); osc.start(); osc.stop(audioCtx.currentTime + decay + 0.1); return {{osc, g}};
            }};
            activeNodes.push(createTone(freq, 1.0, 1.8), createTone(freq * 2, 0.4, 1.2), createTone(freq * 3, 0.2, 0.8));
            if (currentIndex < baseData.length - 1) {{ currentIndex++; setTimeout(updateDisplay, 50); }}
        }}
        function changeKey(diff) {{ currentKey += diff; updateDisplay(); }}
        function prevNote() {{ if (currentIndex > 0) {{ currentIndex--; updateDisplay(); }} }}
        function resetApp() {{ currentIndex = 0; updateDisplay(); }}
        updateDisplay();
        </script>
        """
        components.html(html_code, height=850, scrolling=True)
