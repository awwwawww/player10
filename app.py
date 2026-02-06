import streamlit as st
import requests

# =================================================
# 1. إعدادات المنصة والستايل السينمائي
# =================================================
st.set_page_config(page_title="BEAST WEB PLAYER PRO", layout="wide", page_icon="🎬")

st.markdown("""
<style>
    .stApp { background-color: #080808; color: #e5e5e5; }
    .main-title { color: #00ff41; font-family: 'Impact'; font-size: 45px; text-shadow: 2px 2px #000; }
    .channel-card {
        background: #111; border: 1px solid #222; border-radius: 10px;
        padding: 10px; text-align: center; transition: 0.3s;
    }
    .channel-card:hover { border-color: #00ff41; transform: scale(1.02); }
    .stTextInput>div>div>input { background-color: #111; color: white; border: 1px solid #333; }
</style>
""", unsafe_allow_html=True)

# =================================================
# 2. إدارة البيانات (Session State)
# =================================================
if 'active_acc' not in st.session_state: st.session_state.active_acc = None
if 'content_type' not in st.session_state: st.session_state.content_type = "live"

# =================================================
# 3. دوال التعامل مع سيرفر الاكستريم
# =================================================
def api_request(acc, action, extra=""):
    try:
        url = f"{acc['host']}/player_api.php?username={acc['user']}&password={acc['pass']}&action={action}{extra}"
        return requests.get(url, timeout=7).json()
    except: return []

# =================================================
# 4. واجهة التحكم الجانبية (Sidebar)
# =================================================
with st.sidebar:
    st.markdown("<h1 style='color:#00ff41;'>🌪️ BEAST V2</h1>", unsafe_allow_html=True)
    
    with st.expander("🔑 تسجيل الدخول للسيرفر", expanded=not st.session_state.active_acc):
        host = st.text_input("Host", placeholder="http://host.com:8080")
        user = st.text_input("User")
        pwd = st.text_input("Pass", type="password")
        if st.button("اتصال وتسجيل"):
            if host and user and pwd:
                st.session_state.active_acc = {"host": host.rstrip('/'), "user": user, "pass": pwd}
                st.rerun()

    if st.session_state.active_acc:
        st.markdown("---")
        st.write(f"🌐 المتصل الآن: `{st.session_state.active_acc['host']}`")
        if st.button("🔴 خروج"):
            st.session_state.active_acc = None
            st.rerun()

# =================================================
# 5. الصفحة الرئيسية (المحتوى)
# =================================================
if st.session_state.active_acc:
    acc = st.session_state.active_acc
    
    # قائمة الأقسام الرئيسية
    st.markdown("<h1 class='main-title'>BEAST STREAMING</h1>", unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["📺 قنوات مباشرة", "🍿 أفلام", "🎭 مسلسلات"])

    # --- خانة البحث ---
    search_query = st.text_input("🔍 ابحث عن قناة أو فيلم بالاسم...", key="main_search").lower()

    # --- وظيفة عرض المحتوى لكل قسم ---
    def render_content(content_action, category_action, stream_key, type_path):
        # 1. جلب الفئات
        categories = api_request(acc, category_action)
        cat_names = {c['category_name']: c['category_id'] for c in categories}
        
        col_cat, col_empty = st.columns([1, 2])
        with col_cat:
            sel_cat = st.selectbox("اختر الفئة", ["الكل"] + list(cat_names.keys()), key=f"sel_{content_action}")
        
        cat_id = cat_names[sel_cat] if sel_cat != "الكل" else "0"
        
        # 2. جلب المحتوى
        items = api_request(acc, content_action, f"&category_id={cat_id}")
        
        # 3. فلترة البحث
        if search_query:
            items = [i for i in items if search_query in i.get('name', '').lower()]

        # 4. عرض المحتوى في شبكة (Grid)
        cols = st.columns(5)
        for idx, item in enumerate(items[:50]): # عرض أول 50 لتسريع الأداء
            with cols[idx % 5]:
                name = item.get('name', 'Unknown')
                img = item.get('stream_icon') or item.get('cover')
                if not img: img = "https://via.placeholder.com/150x200?text=No+Image"
                
                st.image(img, use_container_width=True)
                if st.button(name[:20], key=f"btn_{type_path}_{item[stream_key]}"):
                    # بناء رابط التشغيل الموفر للإنترنت
                    stream_url = f"{acc['host']}/{type_path}/{acc['user']}/{acc['pass']}/{item[stream_key]}.m3u8"
                    st.session_state.play_link = stream_url
                    st.session_state.play_name = name
                    st.rerun()

    with tab1: render_content("get_live_streams", "get_live_categories", "stream_id", "live")
    with tab2: render_content("get_vod_streams", "get_vod_categories", "stream_id", "movie")
    with tab3: render_content("get_series", "get_series_categories", "series_id", "series")

    # --- المشغل العائم (Floating Player) ---
    if 'play_link' in st.session_state:
        st.markdown("---")
        st.markdown(f"### 🎬 أنت تشاهد الآن: {st.session_state.play_name}")
        st.video(st.session_state.play_link)
        if st.button("إغلاق المشغل"):
            del st.session_state.play_link
            st.rerun()

else:
    # واجهة الترحيب
    col_welcome, _ = st.columns([2,1])
    with col_welcome:
        st.markdown("""
        # مرحباً بك في BEAST V2 PRO 🎬
        ### مشغل الويب الأسرع والأكثر توفيراً للإنترنت.
        - **بحث سريع** في آلاف القنوات.
        - **بوسترات** أصلية للأفلام والمسلسلات.
        - **توفير البيانات** عبر تقنية الحزم الذكية.
        
        👈 ابدأ بإدخال بيانات سيرفرك من القائمة الجانبية.
        """)