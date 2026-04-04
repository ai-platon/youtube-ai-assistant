import streamlit as st
from groq import Groq
from youtube_transcript_api import YouTubeTranscriptApi  # Измененный импорт
import re

st.set_page_config(page_title="YouTube AI Assistant", page_icon="🎬", layout="wide")

# Дизайн (красная кнопка)
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .stButton>button { 
        background-color: #FF0000; color: white; border-radius: 8px; 
        width: 100%; height: 3.5rem; font-size: 1.2rem; font-weight: bold; border: none;
    }
    .stButton>button:hover { background-color: #cc0000; color: white; }
    </style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.title("⚙️ Настройки")
    api_key = st.text_input("Groq API Key:", type="password")

st.title("🎬 AI YouTube Assistant")
video_url = st.text_input("Ссылка на видео:", placeholder="https://www.youtube.com/watch?v=...")

if st.button("🚀 Создать конспект"):
    if not api_key or not video_url:
        st.error("Введите API ключ и ссылку!")
    else:
        try:
            # Парсинг ссылки
            match = re.search(r'(?:v=|\/|youtu\.be\/)([0-9A-Za-z_-]{11})', video_url)
            if not match:
                st.error("Неверная ссылка!")
                st.stop()
            v_id = match.group(1)

            with st.status("📥 Обработка видео...", expanded=True) as status:
                st.write("Получаю текст субтитров...")
                
                # Прямой вызов метода через импортированный класс
                try:
                    # Пробуем получить сначала на русском, потом на английском
                    transcript_list = YouTubeTranscriptApi.get_transcript(v_id, languages=['ru', 'en'])
                    full_text = " ".join([t['text'] for t in transcript_list])
                except Exception as api_err:
                    st.error(f"Ошибка получения текста: {api_err}")
                    st.stop()

                st.write("🧠 ИИ анализирует контент...")
                client = Groq(api_key=api_key)
                res = client.chat.completions.create(
                    model="llama-3.3-70b-versatile", #
                    messages=[
                        {"role": "system", "content": "Ты эксперт по конспектам. Напиши кратко и понятно на русском языке с эмодзи."},
                        {"role": "user", "content": f"Сделай конспект текста: {full_text[:10000]}"}
                    ]
                )
                status.update(label="✅ Конспект готов!", state="complete", expanded=False)

            st.markdown("### 📝 Главные тезисы")
            st.markdown(res.choices[0].message.content)
            
        except Exception as e:
            st.error(f"Произошла ошибка: {e}")