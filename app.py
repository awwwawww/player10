import streamlit as st
import requests
import streamlit.components.v1 as components
import json

# =================================================
# 1. إعدادات المنصة وحفظ البيانات
# =================================================
st.set_page_config(page_title="BEAST ULTIMATE V4", layout="wide", page_icon="☢️")

# دالة لحفظ واسترجاع بيانات الدخول من رابط الموقع (لضمان بقائها)
def manage_storage():
    if "active_acc" not in st.session_state:
        # محاولة الاستعادة من بارامترات الرابط
        params = st.query_params
        if "h" in params and "u" in params and "p" in params:
            st.session_state.active_acc = {
                "host": params["h"], "user": params["u"], "pass": params["p"]
            }
        else:
            st.session_state.active_acc = None

manage_storage()

st.markdown("""
<style>
    .stApp { background-color: #050505; color: #e5e5e5; }
    .main-title { color: #00ff41; font-family: 'Impact'; font-size: 40px; text-align: center; text-shadow: 0 0 15px #00ff41; }
    .card { background: #111; border: 1px solid #222; border-radius: 10px; padding: 8px; text-align: center; transition: 0.3s; }
    .card:hover { border-color: #00ff41; transform: scale(1.03); }
    .player-box { border: 2px solid #00ff41; border-radius: 10px; overflow: hidden; background: #000; }
</style>
""", unsafe_allow_html=True)

# =================================================
# 2. محرك المشغلات المتعددة (The Triple Engine)
# =================================================
def render_master_player(url, name, mode):
    if mode == "HLS PRO (الأفضل للجودة)":
        player_code = f"""
        <script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script>
        <video id="video" controls autoplay style="width:100%; height:450px; background:black;"></video>
        <script>
          var video = document.getElementById('video');
          var videoSrc = '{url}';
          if (Hls.isSupported()) {{
            var hls = new Hls();
            hls.loadSource(videoSrc);
            hls.attachMedia(video);
          }} else if (video.canPlayType('application/vnd.apple.mpegurl')) {{
            video.src = videoSrc;
          }}
        </script> """
    elif mode == "VideoJS (دعم الترجمة والجودة)":
        player_code = f"""
        <link href="https://vjs.zencdn.net/7.20.3/video-js.css" rel="stylesheet" />
        <video id="vjs" class="video-js vjs-fluid vjs-big-play-centered" controls data-setup='{{"playbackRates": [0.5, 1, 1.5, 2]}}'>
            <source src="{url}" type="application/x-mpegURL">
        </video>
        <script src="https://vjs.zencdn.net/7.20.3/video.min.js"></script> """
    else: # Direct Force Mode
        player_code = f'<iframe src="{url}" width="100%" height="450px" frameborder="0" allowfullscreen></iframe>'
    
    components.html(player_code, height=480)

# =================================================
# 3. واجهة التحكم الجانبية
# =================================================
with st.sidebar:
    st.markdown("<h1 style='color:#00ff41;'>🌪️ BEAST V4</h1>", unsafe_allow_html=True)
    
    if not st.session_state.active_acc:
        with st.form("login_form"):
            h = st.text_input("Host")
            u = st.text_input("User")
            p = st.text_input("Pass", type="password")
            if st.form_submit_button("تسجيل وحفظ دائم"):
                st.session_state.active_acc = {"host": h.rstrip('/'), "user": u, "pass": p}
                # حفظ في الرابط ليبقى عند التحديث
                st.query_params.update(h=h, u=u, p=p)
                st.rerun()
    else:
        st.success("✅ الحساب مفعل ومحفوظ")
        if st.button("🔴 مسح البيانات والخروج"):
            st.session_state.active_acc = None
            st.query_params.clear()
            st.rerun()

    st.divider()
    player_mode = st.selectbox("🎯 اختر محرك التشغيل:", ["HLS PRO (الأفضل للجودة)", "VideoJS (دعم الترجمة والجودة)", "Force Direct (للقنوات الصعبة)"])

# =================================================
# 4. عرض المحتوى
# =================================================
if st.session_state.active_acc:
    acc = st.session_state.active_acc
    st.markdown(f"<div class='main-title'>BEAST PLAYER PRO</div>", unsafe_allow_html=True)

    # تشغيل الفيديو
    if "play_url" in st.session_state:
        with st.container():
            st.markdown(f"**📺 أنت تشاهد الآن: {st.session_state.play_name}**")
            render_master_player(st.session_state.play_url, st.session_state.play_name, player_mode)
            if st.button("❌ إغلاق المشغل"):
                del st.session_state.play_url
                st.rerun()

    # التبويبات
    t1, t2, t3 = st.tabs(["📺 مباشر", "🍿 أفلام", "🎭 مسلسلات"])
    
    def get_data(action, extra=""):
        try:
            return requests.get(f"{acc['host']}/player_api.php?username={acc['user']}&password={acc['pass']}&action={action}{extra}", timeout=5).json()
        except: return []

    search = st.text_input("🔍 ابحث هنا...").lower()

    def render_grid(action_cat, action_stream, type_p, key_id):
        cats = get_data(action_cat)
        cat_names = {c['category_name']: c['category_id'] for c in cats}
        sel_cat = st.selectbox("الفئة", ["الكل"] + list(cat_names.keys()), key=f"sel_{type_p}")
        
        cid = cat_names[sel_cat] if sel_cat != "الكل" else "0"
        items = get_data(action_stream, f"&category_id={cid}")
        
        if search:
            items = [i for i in items if search in i.get('name', '').lower()]

        cols = st.columns(5)
        for idx, item in enumerate(items[:50]):
            with cols[idx % 5]:
                img = item.get('stream_icon') or item.get('cover') or "https://via.placeholder.com/150"
                st.image(img, use_container_width=True)
                if st.button(item.get('name', 'N/A')[:15], key=f"btn_{type_p}_{item[key_id]}"):
                    ext = ".m3u8" if type_p == "live" else ""
                    st.session_state.play_url = f"{acc['host']}/{type_p}/{acc['user']}/{acc['pass']}/{item[key_id]}{ext}"
                    st.session_state.play_name = item.get('name')
                    st.rerun()

    with t1: render_grid("get_live_categories", "get_live_streams", "live", "stream_id")
    with t2: render_grid("get_vod_categories", "get_vod_streams", "movie", "stream_id")
    with t3: render_grid("get_series_categories", "get_series", "series", "series_id")

else:
    st.info("👋 مرحباً بك! أدخل بيانات السيرفر في القائمة الجانبية. سيتم حفظ البيانات تلقائياً حتى بعد إغلاق الموقع.")
