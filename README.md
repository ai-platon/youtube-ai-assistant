# 🎬 YouTube AI Assistant

> Instantly generate a structured summary of any YouTube video — powered by Llama 3.3 70b via Groq API

![Python](https://img.shields.io/badge/Python-3.9+-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.x-FF4B4B?logo=streamlit&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-Llama--3.3--70b-orange)
![License](https://img.shields.io/badge/license-MIT-green)

---

## ✨ Features

| Feature | Description |
|---|---|
| 📝 **Instant summaries** | Paste any YouTube link and get a structured summary in seconds |
| 🌍 **4 summary languages** | Russian, English, Deutsch, Español |
| 📏 **Adjustable length** | Slider from 200 to 5000 characters — brief or fully detailed |
| 😄 **Emojify mode** | Toggle emoji-rich output for a more expressive summary |
| 🔐 **API key memory** | Key is saved in browser `localStorage` — no need to re-enter |
| 🌐 **Auto language detection** | Detects RU or EN interface by IP on first load |
| 🎨 **Clean animated UI** | Custom components, smooth animations, red accent theme |

---

## 🚀 Quick Start

### 1. Clone the repo

```bash
git clone https://github.com/ai-platon/youtube-ai-assistant.git
cd youtube-ai-assistant
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Get a free Groq API key

Go to [console.groq.com/keys](https://console.groq.com/keys) and create a key.  
> 💡 Use a VPN if the site is unavailable in your region.

### 4. Run the app

```bash
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 📦 Requirements

```txt
streamlit
groq
youtube-transcript-api
requests
```

Install all at once:

```bash
pip install streamlit groq youtube-transcript-api requests
```

---

## 🖥️ Usage

1. Open the app in your browser
2. Enter your **Groq API key** in the sidebar — it will be saved automatically for future visits
3. Paste a **YouTube URL** into the input field
4. Choose the **summary language**, **length**, and toggle **Emojify** if you want
5. Click **🚀 Generate Summary** (or just press Enter)
6. Read your structured summary in the result card

---

## ⚙️ Configuration

All settings are in the sidebar:

| Setting | Options |
|---|---|
| **Interface language** | RU / EN |
| **Summary language** | Russian, English, Deutsch, Español |
| **Summary length** | 200 – 5000 characters |
| **Emojify** | On / Off |
| **API Key** | Auto-saved in browser localStorage |

---

## ⚠️ Known Limitations

### YouTube 403 Error (subtitles blocked)

YouTube blocks subtitle requests from cloud servers (Streamlit Cloud, Railway, etc.).

**Solutions:**
- ✅ **Run locally** — works perfectly with `streamlit run app.py`
- ✅ **Videos with auto-generated captions** tend to work more reliably
- ⚙️ **Advanced:** configure a [Webshare](https://webshare.io) residential proxy in `.streamlit/secrets.toml`

```toml
# .streamlit/secrets.toml
WEBSHARE_PROXY = "http://user:pass@proxy.webshare.io:80"
```

---

## 🏗️ Project Structure

```
youtube-ai-assistant/
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
└── README.md
```

---

## 🔒 Security

- The API key is stored **only in your browser's localStorage** — it never leaves your device to any third-party server
- To remove the saved key, click **🗑️ Forget key** in the sidebar

---

## 🤖 Model

This app uses **Llama 3.3 70b Versatile** via the [Groq](https://groq.com) inference API.  
Groq provides extremely fast inference — summaries are typically generated in **under 3 seconds**.

---

## 📄 License

MIT License — feel free to use, modify and distribute.

---

## 👤 Author

Made by [Platon](https://github.com/ai-platon) · based on Llama + Groq
