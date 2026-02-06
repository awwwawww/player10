import streamlit as st
import requests
import streamlit.components.v1 as components
from datetime import datetime

# =================================================
# 1. إعدادات المنصة والستايل الاحترافي
# =================================================
st.set_page_config(page_title="BEAST ULTIMATE PLAYER", layout="wide", page_icon="🎬")

st.markdown("""
<style>
    .stApp { background-color: #050505; color: #e5e5e5; }
    .main-title { color: #00ff41; font-family: 'Impact'; font-size: 50px; text-align: center; text-shadow: 0 0 20px #00ff41; }
    .card { background: #111; border: 1px solid #222; border-radius: 12px; padding: 10px; transition: 0.3s; text-align: center; }
    .card:hover { border-color: #00ff41; transform: translateY(-5px); box-shadow: 0 5px 15px rgba(0,255,65,0.2); }
    .stButton>button { width: 100%; border-radius: 20px; }
    .fav-btn { color: #ffcc00 !important; }
</style>
""", unsafe_allow_html=True)

# =================================================
# 2. إدارة الحالة (State Management)
# =================================================
if 'active_acc' not in st.session_state: st.session_state.active_acc = None
if 'favorites' not in st.session_state: st.session_state.favorites = []
if 'play_link' not in st.session_state: st.session_state.play_link = None

# =================================================
# 3. محرك جلب البيانات
# =================================================
def xtream_api(acc, action, extra=""):
    try:
        url = f"{acc['host']}/player_api.php?username={acc['user']}&password={acc['pass']}&action={action}{extra}"
        res = requests.get(url, timeout=7)
        return res.json()
    except: return []

# =================================================
# 4. محرك التشغيل العالمي (Universal Video Engine)
# =================================================
def beast_universal_player(url, name):
    # محرك يدمج HLS.js و Video.js لتشغيل كل شيء
    player_html = f"""
    <html>
    <head>
        <link href="https://vjs.zencdn.net/7.20.3/video-js.css" rel="stylesheet" />
        <script src="https://vjs.zencdn.net/7.20.3/video.min.js"></script>
    </head>
    <body style="margin:0; background:black;">
        <div style="color:#00ff41; font-family:sans-serif; font-size:14px; padding:10px; background:#111;">
            🎥 تشغيل الآن: {name}
        </div>
        <video id="beast-video" class="video-js vjs-big-play-centered vjs-16-9" controls preload="auto" width="100%" data-setup='{{"fluid": true}}'>
            <source src="{url}" type="application/x-mpegURL">
            <source src="{url.replace('.m3u8', '.ts')}" type="video/mp2t">
        </video>
        <script>
            var player = videojs('beast-video');
            player.play();
        </script>
    </body>
    </html>
    """
    components.html(player_html, height=550)

# =================================================
# 5. القائمة الجانبية (تسجيل الدخول)
# =================================================
with st.sidebar:
    st.markdown("<h1 style='color:#00ff41; text-align:center;'>🌪️ BEAST V3.5</h1>", unsafe_allow_html=True)
    
    with st.expander("👤 إعدادات السيرفر", expanded=not st.session_state.active_acc):
        host = st.text_input("Host URL", placeholder="http://host.com:8080")
        user = st.text_input("Username")
        pwd = st.text_input("Password", type="password")
        if st.button("🚀 دخول السيرفر"):
            if host and user and pwd:
                st.session_state.active_acc = {"host": host.rstrip('/'), "user": user, "pass": pwd}
                st.rerun()

    if st.session_state.active_acc:
        st.success(f"متصل بـ: {st.session_state.active_acc['host']}")
        if st.button("🛑 تسجيل الخروج"):
            st.session_state.active_acc = None
            st.rerun()
        
        st.markdown("---")
        st.subheader("⭐ المفضلة")
        for fav in st.session_state.favorites:
            if st.sidebar.button(f"📺 {fav['name'][:20]}", key=f"fav_{fav['id']}"):
                st.session_state.play_link = fav['link']
                st.session_state.play_name = fav['name']
                st.rerun()

# =================================================
# 6. الواجهة الرئيسية والعرض
# =================================================
if st.session_state.active_acc:
    acc = st.session_state.active_acc
    st.markdown("<h1 class='main-title'>BEAST ULTIMATE PLAYER</h1>", unsafe_allow_html=True)

    # --- منطقة المشغل (تظهر عند اختيار قناة) ---
    if st.session_state.play_link:
        st.markdown(f"#### 🎬 المشغل النشط: {st.session_state.play_name}")
        beast_universal_player(st.session_state.play_link, st.session_state.play_name)
        
        c1, c2, c3 = st.columns(3)
        with c1: 
            if st.button("🔄 تحويل لـ TS"): 
                st.session_state.play_link = st.session_state.play_link.replace('.m3u8', '.ts')
                st.rerun()
        with c2:
            if st.button("🔄 تحويل لـ M3U8"): 
                st.session_state.play_link = st.session_state.play_link.replace('.ts', '.m3u8')
                st.rerun()
        with c3:
            if st.button("❌ إغلاق البث"): 
                st.session_state.play_link = None
                st.rerun()
        st.divider()

    # --- تقسيم المحتوى ---
    tab_live, tab_vod, tab_series = st.tabs(["📺 قنوات مباشرة", "🍿 أفلام", "🎭 مسلسلات"])

    search_q = st.text_input("🔍 بحث سيع في السيرفر...", "").lower()

    def show_grid(content_type, category_action, stream_action, type_path, stream_key):
        cats = xtream_api(acc, category_action)
        cat_map = {c['category_name']: c['category_id'] for c in cats}
        
        col_sel, _ = st.columns([1, 2])
        with col_sel:
            sel_cat = st.selectbox("الفئة", ["الكل"] + list(cat_map.keys()), key=f"cat_{content_type}")
        
        cat_id = cat_map[sel_cat] if sel_cat != "الكل" else "0"
        items = xtream_api(acc, stream_action, f"&category_id={cat_id}")
        
        if search_q:
            items = [i for i in items if search_q in i.get('name', '').lower()]

        # عرض الشبكة
        cols = st.columns(6)
        for idx, item in enumerate(items[:60]): # عرض 60 محتوى للسرعة
            with cols[idx % 6]:
                name = item.get('name', 'N/A')
                img = item.get('stream_icon') or item.get('cover') or "https://via.placeholder.com/150x200?text=No+Logo"
                
                st.markdown(f'<div class="card">', unsafe_allow_html=True)
                st.image(img, use_container_width=True)
                
                # أزرار التشغيل والمفضلة
                b_col1, b_col2 = st.columns([4, 1])
                with b_col1:
                    if st.button(f"▶️ {name[:12]}", key=f"play_{type_path}_{item[stream_key]}"):
                        ext = ".m3u8" if content_type == "live" else ""
                        st.session_state.play_link = f"{acc['host']}/{type_path}/{acc['user']}/{acc['pass']}/{item[stream_key]}{ext}"
                        st.session_state.play_name = name
                        st.rerun()
                with b_col2:
                    if st.button("⭐", key=f"fav_add_{item[stream_key]}"):
                        fav_item = {"id": item[stream_key], "name": name, "link": f"{acc['host']}/{type_path}/{acc['user']}/{acc['pass']}/{item[stream_key]}{ext}"}
                        if fav_item not in st.session_state.favorites:
                            st.session_state.favorites.append(fav_item)
                            st.toast("تمت الإضافة للمفضلة!")
                st.markdown('</div>', unsafe_allow_html=True)

    with tab_live: show_grid("live", "get_live_categories", "get_live_streams", "live", "stream_id")
    with tab_vod: show_grid("vod", "get_vod_categories", "get_vod_streams", "movie", "stream_id")
    with tab_series: show_grid("series", "get_series_categories", "get_series", "series", "series_id")

else:
    st.markdown("""
    <div style='text-align: center; padding: 100px;'>
        <h2 style='color: #00ff41;'>🌪️ BEAST ULTIMATE V3.5 🎬</h2>
        <p>مرحباً بك في أقوى مشغل ويب للاكستريم. الرجاء إدخال بياناتك في القائمة الجانبية للبدء.</p>
        <img src="https://img.icons8.com/nolan/512/tv.png" width="200">
    </div>
    """, unsafe_allow_html=True)
