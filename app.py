import streamlit as st
import requests
import streamlit.components.v1 as components

# =================================================
# 1. إعدادات المنصة وحفظ البيانات (Permanent Store)
# =================================================
st.set_page_config(page_title="BEAST V5 EXTERNAL", layout="wide", page_icon="🚀")

# استعادة البيانات من الرابط تلقائياً
params = st.query_params
if "h" in params and "u" in params and "p" in params:
    if "active_acc" not in st.session_state:
        st.session_state.active_acc = {"host": params["h"], "user": params["u"], "pass": params["p"]}

st.markdown("""
<style>
    .stApp { background-color: #050505; color: white; }
    .main-title { color: #00ff41; text-align: center; font-family: 'Impact'; font-size: 40px; }
    .card { background: #111; border: 1px solid #333; padding: 10px; border-radius: 10px; text-align: center; }
    .external-btn {
        background-color: #ff8800 !important; color: white !important;
        font-weight: bold !important; border-radius: 10px !important;
        padding: 10px !important; text-decoration: none !important; display: block; text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# =================================================
# 2. وظيفة إنشاء روابط التشغيل الخارجي
# =================================================
def get_external_links(url):
    # روابط مخصصة لفتح التطبيقات مباشرة
    vlc_link = f"vlc://{url}"
    mx_link = f"intent:{url}#Intent;package=com.mxtech.videoplayer.ad;end"
    nplayer_link = f"nplayer-{url}"
    return vlc_link, mx_link

# =================================================
# 3. القائمة الجانبية (الدخول)
# =================================================
with st.sidebar:
    st.markdown("<h1 style='color:#00ff41;'>🌪️ BEAST V5</h1>", unsafe_allow_html=True)
    if not st.session_state.get("active_acc"):
        with st.form("login"):
            h = st.text_input("السيرفر (Host)")
            u = st.text_input("اليوزر (User)")
            p = st.text_input("الباسورد (Pass)", type="password")
            if st.form_submit_button("دخول وحفظ دائم"):
                st.session_state.active_acc = {"host": h.rstrip('/'), "user": u, "pass": p}
                st.query_params.update(h=h, u=u, p=p)
                st.rerun()
    else:
        st.success("✅ متصل الآن")
        if st.button("🔴 تسجيل خروج"):
            st.session_state.active_acc = None
            st.query_params.clear()
            st.rerun()

# =================================================
# 4. عرض المحتوى والتشغيل
# =================================================
if st.session_state.get("active_acc"):
    acc = st.session_state.active_acc
    st.markdown("<div class='main-title'>BEAST EXTERNAL PLAYER</div>", unsafe_allow_html=True)

    # --- منطقة المشغل النشط ---
    if "play_url" in st.session_state:
        url = st.session_state.play_url
        vlc, mx = get_external_links(url)
        
        st.warning(f"🎯 قناة: {st.session_state.play_name}")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f'<a href="{vlc}" class="external-btn">🧡 فتح في VLC</a>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<a href="{mx}" class="external-btn" style="background:#0055ff !important;">💙 فتح في MX Player</a>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<a href="{url}" download class="external-btn" style="background:#444 !important;">📥 تحميل الملف</a>', unsafe_allow_html=True)
        
        st.info("💡 إذا كنت على الكمبيوتر، اضغط 'فتح في VLC'. إذا كنت على الهاتف، اختر VLC أو MX Player.")
        if st.button("إغلاق الخيارات"):
            del st.session_state.play_url
            st.rerun()
        st.divider()

    # --- البحث والقنوات ---
    t1, t2, t3 = st.tabs(["📺 مباشر", "🍿 أفلام", "🎭 مسلسلات"])
    search = st.text_input("🔍 بحث عن قناة...").lower()

    def render_content(cat_act, stream_act, type_p, key_id):
        try:
            items = requests.get(f"{acc['host']}/player_api.php?username={acc['user']}&password={acc['pass']}&action={stream_act}", timeout=5).json()
            if search:
                items = [i for i in items if search in i.get('name', '').lower()]
            
            cols = st.columns(5)
            for idx, item in enumerate(items[:100]):
                with cols[idx % 5]:
                    img = item.get('stream_icon') or item.get('cover') or "https://via.placeholder.com/150"
                    st.image(img, use_container_width=True)
                    if st.button(item.get('name', 'N/A')[:15], key=f"{type_p}_{item[key_id]}"):
                        ext = ".m3u8" if type_p == "live" else ""
                        st.session_state.play_url = f"{acc['host']}/{type_p}/{acc['user']}/{acc['pass']}/{item[key_id]}{ext}"
                        st.session_state.play_name = item.get('name')
                        st.rerun()
        except: st.error("فشل في جلب البيانات من السيرفر.")

    with t1: render_content(None, "get_live_streams", "live", "stream_id")
    with t2: render_content(None, "get_vod_streams", "movie", "stream_id")
    with t3: render_content(None, "get_series", "series", "series_id")
else:
    st.info("الرجاء تسجيل الدخول.")
