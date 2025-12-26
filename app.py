import streamlit as st
import helper
import pickle
import time
import nltk

# Download NLTK stopwords data
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

# -------------------------------------------------------------------------
# 1. Page Configuration
# -------------------------------------------------------------------------
st.set_page_config(
    page_title="Duplicate Question Detector",
    layout="centered",
    initial_sidebar_state="expanded"
)

# -------------------------------------------------------------------------
# 2. SVG Icons (Adjusted Sizes)
# -------------------------------------------------------------------------
ICON_SEARCH = """
<svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#4CAF50" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
"""

ICON_SETTINGS = """
<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#E0E0E0" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>
"""

ICON_BOLT = """
<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#FFC107" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"></polygon></svg>
"""

# Reduced size for result icons (was 50, now 35)
ICON_CHECK_BIG = """
<svg xmlns="http://www.w3.org/2000/svg" width="35" height="35" viewBox="0 0 24 24" fill="none" stroke="#4CAF50" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-bottom: 5px;"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
"""

ICON_ALERT_BIG = """
<svg xmlns="http://www.w3.org/2000/svg" width="35" height="35" viewBox="0 0 24 24" fill="none" stroke="#d32f2f" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-bottom: 5px;"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>
"""

# -------------------------------------------------------------------------
# 3. Custom CSS Styles
# -------------------------------------------------------------------------
st.markdown("""
<style>
    /* Balanced Top Padding (Not too high, not too low) */
    .block-container {
        padding-top: 4rem !important;
        padding-bottom: 2rem !important;
    }

    /* Main Background */
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    
    /* Sidebar Background */
    [data-testid="stSidebar"] {
        background-color: #262730; 
        border-right: 1px solid #333;
    }
    
    /* Input Text Areas */
    .stTextArea textarea {
        background-color: #1E1E1E;
        color: white;
        border: 1px solid #4A4A4A;
        border-radius: 8px;
    }
    .stTextArea textarea:focus {
        border-color: #4CAF50;
        box-shadow: 0 0 5px rgba(76, 175, 80, 0.5);
    }
    
    /* Text Coloring */
    h1, h2, h3, p, label { color: #E0E0E0 !important; }
    
    /* Button */
    .stButton button {
        background: linear-gradient(45deg, #4CAF50, #45a049);
        color: white;
        border: none;
        padding: 12px 24px;
        font-size: 16px;
        font-weight: 600;
        border-radius: 8px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
        width: 100%;
        margin-top: 10px;
    }
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(76, 175, 80, 0.4);
    }
    
    /* Result Cards (COMPACT SIZE) */
    .verdict-box {
        margin-top: 20px;
        margin-left: auto;
        margin-right: auto;
        padding: 15px; /* Reduced padding */
        max-width: 450px; /* Limits width */
        border-radius: 12px;
        text-align: center;
        animation: popIn 0.6s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    
    /* Duplicate Style */
    .is-duplicate {
        background: #181111;
        border: 1px solid #d32f2f;
        box-shadow: 0 0 20px rgba(211, 47, 47, 0.1);
    }
    .is-duplicate h2 { color: #ef5350 !important; margin: 5px 0 5px 0; font-size: 1.2rem; }
    .is-duplicate p { color: #bdbdbd !important; font-size: 13px; margin: 0;}

    /* Unique Style */
    .is-unique {
        background: #0f1610; 
        border: 1px solid #2e7d32;
        box-shadow: 0 0 20px rgba(76, 175, 80, 0.1);
    }
    .is-unique h2 { color: #66bb6a !important; margin: 5px 0 5px 0; font-size: 1.2rem; }
    .is-unique p { color: #bdbdbd !important; font-size: 13px; margin: 0;}
    
    /* Title Alignment */
    .title-container {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 15px;
        margin-bottom: 20px;
    }

    @keyframes popIn {
        0% { opacity: 0; transform: scale(0.9); }
        100% { opacity: 1; transform: scale(1); }
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------------------
# 4. Model & Data Loading
# -------------------------------------------------------------------------
@st.cache_resource
def load_model():
    try:
        return pickle.load(open('model.pkl', 'rb'))
    except:
        return None

model = load_model()

# -------------------------------------------------------------------------
# 5. Sidebar
# -------------------------------------------------------------------------
with st.sidebar:
    st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 20px;">
            {ICON_SETTINGS} <span style="font-size: 20px; font-weight: bold; color: #E0E0E0;">Settings</span>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 10px; margin-top: 20px; margin-bottom: 10px;">
            {ICON_BOLT} <span style="font-size: 16px; font-weight: bold; color: #E0E0E0;">Quick Examples</span>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("Load Duplicate Pair"):
        st.session_state['q1'] = "How can i learn Python?"
        st.session_state['q2'] = "how do we learn Python?"
    
    if st.button("Load Unique Pair"):
        st.session_state['q1'] = "What is Machine Learning?"
        st.session_state['q2'] = "How to cook pasta?"

# -------------------------------------------------------------------------
# 6. Main Layout
# -------------------------------------------------------------------------

# Title
st.markdown(f"""
<div class="title-container">
{ICON_SEARCH}
<h1 style='margin: 0; padding: 0; color: #FAFAFA;'>Duplicate Question Detector</h1>
</div>
""", unsafe_allow_html=True)

st.markdown("<p style='text-align: center; opacity: 0.8; color: #B0B0B0; margin-bottom: 30px;'>Compare two questions to see if they are semantically identical.</p>", unsafe_allow_html=True)

# Inputs
with st.container(border=True):
    col1, col2 = st.columns(2)
    
    if 'q1' not in st.session_state: st.session_state['q1'] = ""
    if 'q2' not in st.session_state: st.session_state['q2'] = ""

    with col1:
        st.subheader("Question 1")
        q1_input = st.text_area(
            "label_hidden_1",
            value=st.session_state['q1'],
            height=150,
            label_visibility="collapsed",
            placeholder="Type your first question here..."
        )

    with col2:
        st.subheader("Question 2")
        q2_input = st.text_area(
            "label_hidden_2",
            value=st.session_state['q2'],
            height=150,
            label_visibility="collapsed",
            placeholder="Type your second question here..."
        )

# Button
col_spacer_l, col_btn, col_spacer_r = st.columns([1, 2, 1])
with col_btn:
    check_btn = st.button("Analyze Questions", use_container_width=True)

# Logic
if check_btn:
    if not q1_input.strip() or not q2_input.strip():
        st.warning("Please enter text in both fields to compare.")
    elif model is None:
        st.error("Model not found. Please ensure 'model.pkl' is in the folder.")
    else:
        with st.spinner("Calculating semantic similarity..."):
            time.sleep(0.6)
            
            try:
                query = helper.query_point_creator(q1_input, q2_input)
                result = model.predict(query)[0]

                if result:
                    # Duplicate Found (Compact)
                    st.markdown(f"""
<div class="verdict-box is-duplicate">
{ICON_ALERT_BIG}
<h2>Duplicate Detected</h2>
<p>These questions have the same intent.</p>
</div>
""", unsafe_allow_html=True)
                else:
                    # Unique (Compact)
                    st.markdown(f"""
<div class="verdict-box is-unique">
{ICON_CHECK_BIG}
<h2>Semantically Unique</h2>
<p>These questions appear to have different meanings.</p>
</div>
""", unsafe_allow_html=True)
                    
            except Exception as e:
                st.error(f"Prediction Error: {e}")

# Footer
st.markdown("""
    <div style="margin-top: 50px; text-align: center; color: #555; font-size: 12px;">
        Model: XGBOOST &bull; Dataset: Quora QP &bull; Privacy: Local Processing (79% Accuracy)
    </div>
""", unsafe_allow_html=True)