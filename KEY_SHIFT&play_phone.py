# 20260326



import streamlit as st
import os
import re
import unicodedata
import streamlit.components.v1 as components

# ブラウザ設定
st.set_page_config(page_title="ボイスチューナー", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #111 !important; color: #eee !important; }
    .viewerBadge_container__1QSob, #MainMenu, footer, header { display: none; }
    [data-testid="stSelectbox"] {
        margin-left: -10px !important;
        margin-right: -10px !important;
        width: calc(100% + 20px) !important;
        margin-top: -20px;
        margin-bottom: 10px;
    }
    div[data-baseweb="select"] > div {
        border: 1px solid #444 !important;
        background-color: #1a1a1a !important;
        border-radius: 10px !important;
    }
    </style>
    <div style="text-align:center; padding: 5px 0; margin-top: -30px;">
        <h2 style="color: #999; font-size: 16px; margin-bottom: 5px; font-weight: normal; letter-spacing: 1px;">🎼 VOICE TUNER</h2>
    </div>
    """, unsafe_allow_html=True)


def list_txt_files():
    files = [f for f in os.listdir('.') if f.endswith('.txt') and f != 'requirements.txt']
    return sorted(files)


txt_files = list_txt_files()
selected_file = st.selectbox("曲を選択", txt_files, label_visibility="collapsed") if txt_files else None


def get_base_notes_with_structure(filename):
    if not filename: return [], ""
    note_map = {
        'ド': 0, 'c': 0, 'ど': 0, 'do': 0, 'レ': 2, 'd': 2, 'れ': 2, 're': 2,
        'ミ': 4, 'e': 4, 'み': 4, 'mi': 4, 'ファ': 5, 'f': 5, 'ふぁ': 5, 'fa': 5,
        'ソ': 7, 'g': 7, 'そ': 7, 'so': 7, 'ラ': 9, 'a': 9, 'ra': 9, 'ら': 9,
        'シ': 11, 'b': 11, 'si': 11, 'ti': 11, 'し': 11
    }
    try:
        with open(filename, "r", encoding="utf-8") as f:
            original_text = f.read()
    except:
        return [], ""
    clean_text = unicodedata.normalize('NFKC', original_text).lower().replace("ー", "")
    pattern = r"([a-zぁ-んァ-ヶ]{1,3}|[ドレミファソラシ])([#b♭＃]?)([0-9])([#b♭＃]?)"
    matches = re.finditer(pattern, clean_text)
    base_data = []
    for m in matches:
        name_part = m.group(1);
        acc = m.group(2) if m.group(2) else m.group(4);
        oct_str = m.group(3)
        base_val = None
        for l in range(len(name_part), 0, -1):
            if name_part[:l] in note_map:
                base_val = note_map[name_part[:l]];
                break
        if base_val is None: continue
        val = base_val + (-1 if acc in ['b', '♭'] else 1 if acc in ['#', '＃'] else 0)
        base_data.append({"abs_pos": int(oct_str) * 12 + val, "original": m.group(0)})
    return base_data, original_text


if selected_file:
    data, raw_text = get_base_notes_with_structure(selected_file)
    if data:
        notes_json = str(data).replace("'", '"')
        safe_raw_text = raw_text.replace("\\", "\\\\").replace("`", "\\`").replace("${", "\\${").replace("\\n", "\\n")

        html_code = f"""
        <div style="background-color:#111; color:#eee; font-family:sans-serif; user-select:none; padding:5px;">
            <div style="display:flex; gap:8px; margin-bottom:12px;">
                <button onclick="changeKey(-1)" style="flex:1; height:55px; font-size:18px; border-radius:10px; border:1px solid #444; background:#2A2A2A; color:#81d4fa;">➖</button>
                <div id="key-val" style="flex:1.8; height:55px; font-size:16px; font-weight:bold; border-radius:10px; border:1px solid #444; background:#222; color:#ffb74d; display:flex; justify-content:center; align-items:center;">KEY：0</div>
                <button onclick="changeKey(1)" style="flex:1; height:55px; font-size:18px; border-radius:10px; border:1px solid #444; background:#2A2A2A; color:#81d4fa;">➕</button>
            </div>
            <div style="text-align:center;">
                <div onclick="playCurrent()" style="background-color:#222; padding:25px 5px; border-radius:15px; margin-bottom:12px; border:1px solid #333; box-shadow: 0 4px 10px rgba(0,0,0,0.5);">
                    <p style="font-size:10px; color:#ffb74d; font-weight:bold; margin-bottom:0px; letter-spacing:2px;">TAP TO NEXT</p>
                    <h1 id="display-note" style="font-size:85px; color:#81d4fa; margin:0; line-height:1.0; font-weight:300;">--</h1>
                </div>
                <div style="display:flex; gap:8px; margin-bottom:20px;">
                    <button onclick="prevNote()" style="flex:1; height:55px; font-size:14px; border-radius:10px; border:1px solid #444; background:#2A2A2A; color:#aaa;">⏪ 戻る</button>
                    <button onclick="resetApp()" style="flex:1; height:55px; font-size:14px; border-radius:10px; border:1px solid #444; background:#2A2A2A; color:#aaa;">↺ 最初</button>
                </div>
            </div>
            <div style="border-top:1px solid #333; padding-top:12px; font-family:monospace;">
                <p style="font-weight:bold; margin:0; font-size:11px; color:#555; letter-spacing: 1px;">AFTER (歌う音)</p>
                <div id="after-list" style="color:#aaa; font-size:14px; margin-bottom:18px; white-space:pre-wrap; line-height:1.6; letter-spacing: 0.5px;"></div>
                <p style="font-weight:bold; margin:0; font-size:10px; color:#333; letter-spacing: 1px;">BEFORE (元の音)</p>
                <div id="before-list" style="font-size:11px; color:#444; white-space:pre-wrap; line-height:1.4;"></div>
            </div>
        </div>

        <script>
        const baseData = {notes_json};
        const rawText = `{safe_raw_text}`;
        const valToNote = ["ド", "ド#", "レ", "レ#", "ミ", "ファ", "ファ#", "ソ", "ソ#", "ラ", "ラ#", "シ"];
        let currentKey = 0; let currentIndex = 0;
        let audioCtx = null;
        let compressor = null;
        let masterGain = null;
        let activeNodes = [];

        function initAudio() {{
            if (audioCtx) return;
            audioCtx = new (window.AudioContext || window.webkitAudioContext)();

            // 全体音量を引き上げるためのゲイン
            masterGain = audioCtx.createGain();
            masterGain.gain.setValueAtTime(1.5, audioCtx.currentTime); // 他サイトに負けない音圧

            compressor = audioCtx.createDynamicsCompressor();
            compressor.threshold.setValueAtTime(-15, audioCtx.currentTime);
            compressor.knee.setValueAtTime(30, audioCtx.currentTime);
            compressor.ratio.setValueAtTime(12, audioCtx.currentTime);
            compressor.attack.setValueAtTime(0, audioCtx.currentTime);
            compressor.release.setValueAtTime(0.25, audioCtx.currentTime);

            masterGain.connect(compressor);
            compressor.connect(audioCtx.destination);
        }}

        function updateDisplay() {{
            const pos = baseData[currentIndex].abs_pos + currentKey;
            document.getElementById('display-note').innerText = valToNote[((pos % 12) + 12) % 12] + Math.floor(pos / 12);
            document.getElementById('key-val').innerText = "KEY：" + (currentKey > 0 ? "+" : "") + currentKey;
            updateLists();
        }}

        function updateLists() {{
            const pattern = /([a-zぁ-んァ-ヶ]{{1,3}}|[ドレミファソラシ])([#b♭＃]?)([0-9])([#b♭＃]?)/gi;
            const replaceFunc = (isAfter) => {{
                let count = 0;
                return rawText.replace(pattern, (match) => {{
                    const idx = count++;
                    let txt = match;
                    if (isAfter) {{
                        const pos = baseData[idx].abs_pos + currentKey;
                        txt = valToNote[((pos % 12) + 12) % 12] + Math.floor(pos / 12);
                    }}
                    let style = idx === currentIndex ? "background:#ffff00;color:#000;font-weight:bold;border-radius:3px;padding:0 3px;" : "";
                    return `<span style="${{style}}">${{txt}}</span>`;
                }});
            }};
            document.getElementById('after-list').innerHTML = replaceFunc(true);
            document.getElementById('before-list').innerHTML = replaceFunc(false);
        }}

        function playCurrent() {{
            initAudio();
            if (audioCtx.state === 'suspended') audioCtx.resume();

            // ノイズ防止：前の音を即座にフェードアウト
            activeNodes.forEach(n => {{
                try {{ n.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.05); }} catch(e) {{}}
            }});
            activeNodes = [];

            const pos = baseData[currentIndex].abs_pos + currentKey;
            const freq = 440 * Math.pow(2, (pos - 57) / 12);

            const createTone = (f, vol, decay) => {{
                const osc = audioCtx.createOscillator();
                const g = audioCtx.createGain();
                osc.type = 'sine';
                osc.frequency.setValueAtTime(f, audioCtx.currentTime);
                g.gain.setValueAtTime(0, audioCtx.currentTime);
                g.gain.linearRampToValueAtTime(vol, audioCtx.currentTime + 0.005);
                g.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + decay);
                osc.connect(g);
                g.connect(masterGain);
                osc.start();
                osc.stop(audioCtx.currentTime + decay + 0.1);
                return {{osc, g}};
            }};

            activeNodes.push(createTone(freq, 1.0, 1.8));      // 基音
            activeNodes.push(createTone(freq * 2, 0.4, 1.2));  // 第2倍音
            activeNodes.push(createTone(freq * 3, 0.2, 0.8));  // 第3倍音

            if (currentIndex < baseData.length - 1) {{ 
                currentIndex++; 
                setTimeout(updateDisplay, 50); 
            }}
        }}

        function changeKey(diff) {{ currentKey += diff; updateDisplay(); }}
        function prevNote() {{ if (currentIndex > 0) {{ currentIndex--; updateDisplay(); }} }}
        function resetApp() {{ currentIndex = 0; updateDisplay(); }}
        updateDisplay();
        </script>
        """
        components.html(html_code, height=800, scrolling=True)
