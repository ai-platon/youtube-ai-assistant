import streamlit as st
from groq import Groq
from youtube_transcript_api import YouTubeTranscriptApi
import re
import requests

# --- 1. КОНФИГУРАЦИЯ СТРАНИЦЫ ---
st.set_page_config(
    page_title="YouTube AI Summary",
    page_icon="🎬",
    layout="centered"
)

# --- 2. СЛОВАРЬ ПЕРЕВОДОВ ---
translations = {
    'RU': {
        'settings': '⚙️ Настройки',
        'get_key': '1. Получите API ключ',
        'key_link': '[Перейти в Groq Console](https://console.groq.com/keys) 🔑',
        'vpn_note': '(Используйте VPN, если сайт не открывается)',
        'enter_key': '2. Введите ваш ключ:',
        'key_saved': 'Ключ сохранён',
        'key_clear': '🗑️ Забыть ключ',
        'summary_lang': 'Язык конспекта',
        'summary_len': 'Длина конспекта',
        'len_short': 'Кратко',
        'len_long': 'Подробно',
        'emojify_label': '😄 Emojify',
        'emojify_help': 'Добавить эмодзи в конспект',
        'model_info': 'Модель: Llama-3.3-70b',
        'title': 'YouTube AI Assistant',
        'subtitle': 'Вставьте ссылку на видео для создания конспекта',
        'url_label': 'URL видео',
        'url_placeholder': 'https://youtu.be/...',
        'btn_generate': '🚀 Создать конспект',
        'status_start': '⌛ Обработка...',
        'status_done': '✅ Готово!',
        'err_no_key': '⚠️ Введите API ключ в боковой панели!',
        'err_bad_url': '❌ Не удалось распознать ссылку. Проверьте формат.',
        'err_no_sub': '❌ Субтитры не найдены или доступ заблокирован.',
        'err_bad_key': '❌ Неверный API ключ Groq. Проверьте ключ в настройках и нажмите «Забыть ключ», затем введите заново.',
        'app_lang_label': 'Язык интерфейса',
        'fetching_sub': '📥 Получаем субтитры...',
        'generating': '🤖 Генерируем конспект...',
    },
    'EN': {
        'settings': '⚙️ Settings',
        'get_key': '1. Get API Key',
        'key_link': '[Go to Groq Console](https://console.groq.com/keys) 🔑',
        'vpn_note': '(Use VPN if the site does not open)',
        'enter_key': '2. Enter your key:',
        'key_saved': 'Key saved',
        'key_clear': '🗑️ Forget key',
        'summary_lang': 'Summary language',
        'summary_len': 'Summary length',
        'len_short': 'Brief',
        'len_long': 'Detailed',
        'emojify_label': '😄 Emojify',
        'emojify_help': 'Add emojis to the summary',
        'model_info': 'Model: Llama-3.3-70b',
        'title': 'YouTube AI Assistant',
        'subtitle': 'Paste a video link to generate a summary',
        'url_label': 'Video URL',
        'url_placeholder': 'https://youtu.be/...',
        'btn_generate': '🚀 Generate Summary',
        'status_start': '⌛ Processing...',
        'status_done': '✅ Done!',
        'err_no_key': '⚠️ Enter API Key in the sidebar!',
        'err_bad_url': '❌ Could not recognize the link. Check the format.',
        'err_no_sub': '❌ Subtitles not found or access blocked.',
        'err_bad_key': '❌ Invalid Groq API key. Check your key, click "Forget key" and enter it again.',
        'app_lang_label': 'Interface language',
        'fetching_sub': '📥 Fetching subtitles...',
        'generating': '🤖 Generating summary...',
    }
}

RU_COUNTRIES = {
    'RU','BY','KZ','KG','TJ','UZ','TM','UA','MD','AM','AZ','GE',
    'PL','CZ','SK','HU','RO','BG','RS','HR','SI','BA','MK','ME','AL',
    'EE','LV','LT','MN','IL'
}

def detect_language_by_ip():
    try:
        r = requests.get("https://ipapi.co/json/", timeout=3)
        country = r.json().get("country_code", "")
        return "RU" if country in RU_COUNTRIES else "EN"
    except Exception:
        return "EN"

# --- 3. SESSION STATE ---
if 'app_lang' not in st.session_state:
    st.session_state.app_lang = detect_language_by_ip()
if 'summary_length' not in st.session_state:
    st.session_state.summary_length = 2000
if 'generate_triggered' not in st.session_state:
    st.session_state.generate_triggered = False
if 'emojify' not in st.session_state:
    st.session_state.emojify = True
if 'saved_api_key' not in st.session_state:
    st.session_state.saved_api_key = ""
if 'ls_key_loaded' not in st.session_state:
    st.session_state.ls_key_loaded = False
if 'clear_key_triggered' not in st.session_state:
    st.session_state.clear_key_triggered = False

app_lang = st.session_state.app_lang
txt = translations[app_lang]

# --- СТИЛИ ---
st.markdown("""
<style>
/* ════════════ ЯЗЫК radio ════════════ */
div[data-testid="stSidebar"] div[data-testid="stRadio"] > label {
    font-size: 13px !important; font-weight: 600 !important;
    color: #555 !important; margin-bottom: 6px !important;
}
div[data-testid="stSidebar"] div[data-testid="stRadio"] > div {
    display: flex !important; flex-direction: row !important;
    gap: 4px !important; background: #efefef !important;
    border-radius: 20px !important; padding: 3px !important;
    width: fit-content !important;
}
div[data-testid="stSidebar"] div[data-testid="stRadio"] > div > label {
    display: flex !important; align-items: center !important;
    justify-content: center !important; padding: 5px 18px !important;
    border-radius: 16px !important; cursor: pointer !important;
    font-size: 12px !important; font-weight: 700 !important;
    letter-spacing: 0.5px !important; color: #999 !important;
    transition: all 0.2s ease !important; user-select: none !important;
    line-height: 1.4 !important;
}
div[data-testid="stSidebar"] div[data-testid="stRadio"] > div > label:has(input:checked) {
    background: white !important; color: #1a1a1a !important;
    box-shadow: 0 1px 5px rgba(0,0,0,0.13) !important;
}
div[data-testid="stSidebar"] div[data-testid="stRadio"] > div > label > div:first-child { display: none !important; }
div[data-testid="stSidebar"] div[data-testid="stRadio"] > div > label > div:last-child { margin: 0 !important; }

/* ════════════ SLIDER ════════════ */
div[data-testid="stSidebar"] div[data-testid="stSlider"] > label {
    font-size: 13px !important; font-weight: 600 !important; color: #555 !important;
}
div[data-testid="stSidebar"] div[data-testid="stSlider"] div[role="slider"] {
    background-color: #cc0000 !important; border-color: #cc0000 !important;
    box-shadow: 0 1px 6px rgba(204,0,0,0.35) !important;
}
div[data-testid="stSidebar"] div[data-testid="stSlider"] div[data-testid="stTickBarMin"],
div[data-testid="stSidebar"] div[data-testid="stSlider"] div[data-testid="stTickBarMax"] { display: none !important; }
div[data-testid="stSidebar"] div[data-testid="stSlider"] div[data-testid="stThumbValue"] {
    color: #cc0000 !important; font-weight: 700 !important;
    font-size: 13px !important; background: transparent !important; border: none !important;
}
div[data-testid="stSidebar"] div[data-testid="stSlider"] [data-baseweb="thumb"] {
    background-color: #cc0000 !important; border-color: #cc0000 !important;
}

/* ════════════ EMOJIFY CHECKBOX ════════════ */
div[data-testid="stSidebar"] div[data-testid="stCheckbox"] {
    background: #f7f7f7 !important; border-radius: 10px !important;
    padding: 10px 14px !important; border: 1.5px solid #e8e8e8 !important;
    transition: border-color 0.2s ease, background 0.2s ease !important;
}
div[data-testid="stSidebar"] div[data-testid="stCheckbox"]:hover {
    border-color: #cc0000 !important; background: #fff5f5 !important;
}
div[data-testid="stSidebar"] div[data-testid="stCheckbox"] label {
    font-size: 14px !important; font-weight: 600 !important; color: #333 !important;
}

/* ════════════ KEY SAVED BADGE ════════════ */
.key-saved-badge {
    display: flex;
    flex-direction: column;
    gap: 2px;
    background: #f0fff4;
    border: 1.5px solid #86efac;
    border-radius: 8px;
    padding: 8px 12px;
    margin-bottom: 4px;
    box-sizing: border-box;
    width: 100%;
    overflow: hidden;
}
.key-saved-top {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 13px;
    font-weight: 600;
    color: #166534;
}
.key-masked {
    font-family: monospace;
    font-size: 12px;
    color: #888;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 100%;
    display: block;
}

/* ════════════ СКРЫТЬ Enter hint ════════════ */
div[data-testid="InputInstructions"] { display: none !important; }

/* ════════════ SIDEBAR text input ════════════ */
p.sidebar-label {
    font-size: 13px; font-weight: 600; color: #555; margin: 0 0 6px 0;
}
section[data-testid="stSidebar"] div[data-testid="stTextInput"] > label {
    font-size: 13px !important; color: #555 !important;
}
section[data-testid="stSidebar"] div[data-testid="stTextInput"] > div {
    border: 1.5px solid #e0e0e0 !important; border-radius: 9px !important;
    background: white !important; overflow: hidden !important;
    display: flex !important; align-items: center !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
}
section[data-testid="stSidebar"] div[data-testid="stTextInput"] > div:focus-within {
    border-color: #bbb !important; box-shadow: 0 0 0 3px rgba(0,0,0,0.05) !important;
}
section[data-testid="stSidebar"] div[data-testid="stTextInput"] input {
    border: none !important; box-shadow: none !important; outline: none !important;
    background: transparent !important; font-size: 14px !important; caret-color: #888 !important;
}
section[data-testid="stSidebar"] div[data-testid="stTextInput"] button {
    cursor: pointer !important; background: transparent !important;
    border: none !important; padding: 0 10px !important; color: #bbb !important;
}
section[data-testid="stSidebar"] div[data-testid="stTextInput"] button:hover { color: #666 !important; }

/* ════════════ SELECTBOX ════════════ */
section[data-testid="stSidebar"] div[data-testid="stSelectbox"] > div > div {
    border-radius: 9px !important; border: 1.5px solid #e0e0e0 !important;
    font-size: 14px !important; background: white !important; cursor: pointer !important;
}
section[data-testid="stSidebar"] div[data-testid="stSelectbox"] > div > div:hover,
section[data-testid="stSidebar"] div[data-testid="stSelectbox"] > div > div:focus-within {
    border-color: #bbb !important; box-shadow: 0 0 0 3px rgba(0,0,0,0.04) !important;
}

/* ════════════ АНИМАЦИИ ════════════ */
h1 { animation: heroIn 0.7s cubic-bezier(0.22,1,0.36,1) both; }
@keyframes heroIn {
    from { opacity: 0; transform: translateY(-20px) scale(0.97); }
    to   { opacity: 1; transform: translateY(0) scale(1); }
}
@keyframes fadeUp {
    from { opacity: 0; transform: translateY(16px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* ════════════ ПОЛЕ URL ════════════ */
div[data-testid="stMain"] div[data-testid="stTextInput"] > div {
    border: 1.5px solid #e8e8e8 !important; border-radius: 10px !important;
    overflow: hidden !important; background: white !important;
    transition: border-color 0.25s ease, box-shadow 0.25s ease !important;
}
div[data-testid="stMain"] div[data-testid="stTextInput"] > div:focus-within {
    border-color: #e00 !important; box-shadow: 0 0 0 3px rgba(220,0,0,0.1) !important;
}
div[data-testid="stMain"] div[data-testid="stTextInput"] input {
    border: none !important; box-shadow: none !important; outline: none !important;
    background: transparent !important; font-size: 15px !important; caret-color: #e00 !important;
}

/* ════════════ ГЛАВНАЯ КНОПКА ════════════ */
button[data-testid="baseButton-primary"] {
    background: linear-gradient(90deg, #FF1A1A 0%, #CC0000 100%) !important;
    color: white !important; border-radius: 10px !important; height: 3em !important;
    font-weight: 600 !important; border: none !important;
    transition: transform 0.28s cubic-bezier(0.34,1.56,0.64,1), box-shadow 0.28s ease !important;
}
button[data-testid="baseButton-primary"]:hover {
    transform: scale(1.025) translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(220,0,0,0.38) !important;
}
button[data-testid="baseButton-primary"]:active {
    transform: scale(0.975) translateY(1px) !important;
    box-shadow: 0 2px 8px rgba(220,0,0,0.2) !important;
}

/* ════════════ RESULT CARD ════════════ */
.result-card {
    background: white; padding: 26px 30px; border-radius: 14px;
    border-left: 5px solid #e00; box-shadow: 0 4px 20px rgba(0,0,0,0.07);
    color: #31333F; line-height: 1.75;
    animation: springUp 0.7s cubic-bezier(0.22,1,0.36,1) both;
}
@keyframes springUp {
    from { opacity: 0; transform: translateY(28px) scale(0.97); }
    to   { opacity: 1; transform: translateY(0) scale(1); }
}
div[data-testid="stAlert"] { border-radius: 10px !important; }

/* ════════════ FORGET KEY BUTTON ════════════ */
section[data-testid="stSidebar"] button[kind="secondary"] {
    border-radius: 8px !important; font-size: 12px !important;
    color: #888 !important; border-color: #ddd !important;
    transition: all 0.2s ease !important;
}
section[data-testid="stSidebar"] button[kind="secondary"]:hover {
    color: #cc0000 !important; border-color: #cc0000 !important; background: #fff5f5 !important;
}

/* ════════════ FOOTER ════════════ */
.footer { text-align: center; margin-top: 60px; font-size: 0.84em; }
.footer-static { color: #666; }
.footer-link { color: transparent; text-decoration: none; transition: color 0.35s ease; }
.footer-link:hover { color: #444; text-decoration: underline; text-underline-offset: 3px; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
#  localStorage BRIDGE
# ══════════════════════════════════════════════════════
qp = st.query_params
if not st.session_state.ls_key_loaded:
    loaded_key = qp.get("_k", "")
    if loaded_key:
        st.session_state.saved_api_key = loaded_key
        st.query_params.clear()
    st.session_state.ls_key_loaded = True

st.markdown("""
<script>
(function() {
    function tryLoad() {
        const saved = localStorage.getItem('groq_api_key');
        if (saved) {
            const url = new URL(window.location.href);
            if (!url.searchParams.has('_k')) {
                url.searchParams.set('_k', saved);
                window.location.replace(url.toString());
            }
        }
    }
    if (document.readyState === 'complete') { tryLoad(); }
    else { window.addEventListener('load', tryLoad); }
})();
</script>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
#  БОКОВАЯ ПАНЕЛЬ
# ══════════════════════════════════════════════════════
with st.sidebar:
    st.title(txt['settings'])

    lang_choice = st.radio(
        txt['app_lang_label'],
        options=["RU", "EN"],
        index=0 if app_lang == "RU" else 1,
        horizontal=True,
        key="lang_radio"
    )
    if lang_choice != app_lang:
        st.session_state.app_lang = lang_choice
        st.rerun()

    st.markdown("---")
    st.markdown(f"### {txt['get_key']}")
    st.markdown(txt['key_link'])
    st.caption(txt['vpn_note'])

    # API KEY
    if st.session_state.saved_api_key and not st.session_state.clear_key_triggered:
        key = st.session_state.saved_api_key
        masked = key[:6] + "••••••••••••" + key[-4:]
        st.markdown(f"""
        <div class="key-saved-badge">
            <div class="key-saved-top">✅ {txt['key_saved']}</div>
            <span class="key-masked">{masked}</span>
        </div>
        """, unsafe_allow_html=True)
        api_key = key

        if st.button(txt['key_clear'], key="btn_clear_key", use_container_width=True):
            st.session_state.saved_api_key = ""
            st.session_state.clear_key_triggered = True
            st.markdown("<script>localStorage.removeItem('groq_api_key');</script>",
                        unsafe_allow_html=True)
            st.rerun()
    else:
        st.session_state.clear_key_triggered = False
        api_key_input = st.text_input(
            txt['enter_key'],
            type="password",
            label_visibility="visible",
            key="api_key_input",
            placeholder="gsk_..."
        )
        api_key = api_key_input

        if api_key_input and len(api_key_input) > 10:
            st.session_state.saved_api_key = api_key_input
            safe_key = api_key_input.replace("'", "\\'")
            st.markdown(f"""
            <script>
            (function(){{ localStorage.setItem('groq_api_key', '{safe_key}'); }})();
            </script>
            """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown(f'<p class="sidebar-label">{txt["summary_lang"]}</p>', unsafe_allow_html=True)
    lang_options = ["Русский", "English", "Deutsch", "Español"]
    summary_lang = st.selectbox(txt['summary_lang'], lang_options, label_visibility="collapsed")

    st.markdown("---")

    summary_length = st.slider(
        txt['summary_len'],
        min_value=200, max_value=5000,
        value=st.session_state.summary_length,
        step=50, key="slider_len"
    )
    st.session_state.summary_length = summary_length

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(f'<p style="font-size:11px;color:#aaa;margin:-8px 0 0 0">{txt["len_short"]} · 200</p>',
                    unsafe_allow_html=True)
    with col_b:
        st.markdown(f'<p style="font-size:11px;color:#aaa;margin:-8px 0 0 0;text-align:right">5000 · {txt["len_long"]}</p>',
                    unsafe_allow_html=True)

    st.markdown("---")

    emojify = st.checkbox(
        txt['emojify_label'],
        value=st.session_state.emojify,
        help=txt['emojify_help'],
        key="emojify_check"
    )
    st.session_state.emojify = emojify

    st.markdown("---")
    st.info(txt['model_info'])


# ══════════════════════════════════════════════════════
#  ФУНКЦИЯ ПОЛУЧЕНИЯ СУБТИТРОВ
# ══════════════════════════════════════════════════════
def fetch_transcript(v_id: str) -> str:
    errors = []

    # Способ 1 — ru/en напрямую
    try:
        transcript = YouTubeTranscriptApi().fetch(v_id, languages=['ru', 'en', 'en-US'])
        return " ".join([t.text for t in transcript])
    except Exception as e:
        errors.append(f"direct: {e}")

    # Способ 2 — любой доступный язык
    try:
        transcript = YouTubeTranscriptApi().fetch(v_id)
        return " ".join([t.text for t in transcript])
    except Exception as e:
        errors.append(f"any_lang: {e}")

    # Способ 3 — через публичные прокси
    try:
        resp = requests.get(
            "https://api.proxyscrape.com/v2/?request=getproxies&protocol=http"
            "&timeout=5000&country=all&ssl=all&anonymity=elite",
            timeout=5
        )
        proxy_list = [p.strip() for p in resp.text.strip().split("\n") if p.strip()]
    except Exception:
        proxy_list = []

    for proxy in proxy_list[:15]:
        try:
            session = requests.Session()
            session.proxies = {"http": f"http://{proxy}", "https": f"http://{proxy}"}
            session.timeout = 8
            ytt = YouTubeTranscriptApi(http_client=session)
            transcript = ytt.fetch(v_id, languages=['ru', 'en', 'en-US'])
            return " ".join([t.text for t in transcript])
        except Exception as e:
            errors.append(f"proxy {proxy}: {e}")
            continue

    raise Exception("subtitles_unavailable | " + " | ".join(errors[-3:]))


# ══════════════════════════════════════════════════════
#  ОСНОВНОЙ КОНТЕНТ
# ══════════════════════════════════════════════════════
st.title(txt['title'])
st.write(txt['subtitle'])

video_url = st.text_input(
    txt['url_label'],
    placeholder=txt['url_placeholder'],
    label_visibility="visible",
    key="video_url_input"
)

if video_url and re.search(r'youtu', video_url):
    if st.session_state.get("last_url") != video_url:
        st.session_state.last_url = video_url
        st.session_state.generate_triggered = True

btn_clicked = st.button(txt['btn_generate'], type="primary", use_container_width=True)
should_generate = btn_clicked or st.session_state.get("generate_triggered", False)
if st.session_state.get("generate_triggered"):
    st.session_state.generate_triggered = False

if should_generate:
    if not api_key:
        st.warning(txt['err_no_key'])
    elif not video_url:
        st.warning(txt['err_bad_url'])
    else:
        match = re.search(r'(?:v=|\/|youtu\.be\/)([0-9A-Za-z_-]{11})', video_url)
        if not match:
            st.error(txt['err_bad_url'])
            st.stop()

        v_id = match.group(1)

        if summary_length <= 600:
            len_instr = "очень кратко, 3-5 ключевых пунктов"
        elif summary_length <= 1500:
            len_instr = "кратко, основные тезисы"
        elif summary_length <= 2500:
            len_instr = "средней длины, основные тезисы с деталями"
        elif summary_length <= 3500:
            len_instr = "подробно, с разделами и подпунктами"
        else:
            len_instr = "максимально подробно, полный развёрнутый конспект"

        emoji_instr = (
            "Обязательно используй много разнообразных эмодзи в каждом пункте и заголовке."
            if emojify else "Не используй эмодзи вообще."
        )

        with st.status(txt['status_start'], expanded=True) as status:

            # ШАГ 1: субтитры
            st.write(txt['fetching_sub'])
            try:
                full_text = fetch_transcript(v_id)
            except Exception as sub_err:
                status.update(label="❌ Ошибка", state="error")
                err_str = str(sub_err)
                if "subtitles_unavailable" in err_str or "403" in err_str or "Could not retrieve" in err_str:
                    st.error(
                        f"{txt['err_no_sub']}\n\n"
                        "**Причина:** YouTube блокирует запросы с облачного сервера.\n\n"
                        "**Решение:** Запустите локально: `streamlit run app.py`"
                    )
                else:
                    st.error(f"{txt['err_no_sub']}\n\n`{err_str[:200]}`")
                st.stop()

            # ШАГ 2: генерация (только если субтитры получены)
            st.write(txt['generating'])
            try:
                client = Groq(api_key=api_key)
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                f"Сделай конспект на языке: {summary_lang}. "
                                f"Формат: {len_instr}. "
                                f"{emoji_instr} "
                                f"Примерная длина: {summary_length} символов."
                            )
                        },
                        {"role": "user", "content": f"Текст: {full_text[:15000]}"}
                    ]
                )
                res_text = response.choices[0].message.content
            except Exception as groq_err:
                status.update(label="❌ Ошибка", state="error")
                err_str = str(groq_err)
                if "403" in err_str or "401" in err_str or "invalid" in err_str.lower() or "auth" in err_str.lower():
                    st.error(txt['err_bad_key'])
                else:
                    st.error(f"Groq API ошибка: `{err_str[:300]}`")
                st.stop()

            status.update(label=txt['status_done'], state="complete")

        st.markdown(f'<div class="result-card">{res_text}</div>', unsafe_allow_html=True)

# --- ФУТЕР ---
st.markdown('''
<div class="footer">
  <span class="footer-static">Made by </span>
  <a class="footer-link" href="https://github.com/ai-platon" target="_blank">Platon</a>
  <span class="footer-static"> based on Llama</span>
</div>
''', unsafe_allow_html=True)