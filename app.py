import streamlit as st
import os
import time

st.set_page_config(
    page_title='ERIA - Education Regulation Impact Analyzer',
    page_icon='📘',
    layout='wide',
)

from analyzer import analyze_regulation
from pdf_reader import extract_text_from_pdf


time.sleep(0.3)

# ── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.main-title{font-size:2rem;font-weight:700;color:#1a1a2e;}
.sub-title{font-size:1rem;color:#555;margin-top:-10px;}
.section-hdr{font-size:1.1rem;font-weight:600;color:#2c3e50;
    border-left:4px solid #4a90d9;padding-left:10px;margin:1.2rem 0 0.6rem;}
.summary-box{background:#f0f4ff;border-radius:10px;
    padding:1.2rem 1.5rem;font-size:0.95rem;line-height:1.75;color:#222;}
.tag-pill{display:inline-block;background:#dbeafe;color:#1e40af;
    border-radius:20px;padding:3px 12px;font-size:0.78rem;font-weight:600;margin:3px 3px 0 0;}
.cat-pill{display:inline-block;background:#ede9fe;color:#5b21b6;
    border-radius:20px;padding:4px 14px;font-size:0.85rem;font-weight:700;margin-bottom:10px;}
.impact-card{border-radius:10px;padding:1rem 1.2rem;font-size:0.9rem;line-height:1.65;}
.short-card{background:#eff6ff;border-left:4px solid #3b82f6;}
.mid-card{background:#fffbeb;border-left:4px solid #f59e0b;}
.long-card{background:#f0fdf4;border-left:4px solid #22c55e;}
.stake-card{background:#fafafa;border:1px solid #e5e7eb;
    border-radius:10px;padding:0.9rem 1.1rem;margin-bottom:0.6rem;}
.pos-item{color:#166534;font-size:0.9rem;margin:4px 0;}
.risk-item{color:#991b1b;font-size:0.9rem;margin:4px 0;}
.footer{text-align:center;color:#aaa;font-size:0.8rem;
    margin-top:3rem;padding-top:1rem;border-top:1px solid #eee;}
</style>
""", unsafe_allow_html=True)


SAMPLE_TEXT = """UGC Circular No. F.1-1/2023 dated March 2024
Subject: Implementation of Academic Bank of Credits (ABC) under NEP 2020

The UGC notifies all HEIs that from 2024-25, the Academic Bank of Credits (ABC)
scheme is mandatory for all centrally funded institutions.

Key provisions:
1. Students store credits from multiple institutions in ABC DigiLocker account.
2. Multiple entry/exit: Certificate (1yr), Diploma (2yr), Degree (3-4yr).
3. Credits valid for 7 years from date of earning.
4. Institutions must register on abc.gov.in within 60 days.
5. Faculty development programmes by UGC in Q1 2024-25.
6. Non-compliant institutions risk adverse NAAC/NBA accreditation impact."""


if 'text_area_widget_key' not in st.session_state:
    st.session_state['text_area_widget_key'] = ''
if 'pdf_text' not in st.session_state:
    st.session_state['pdf_text'] = ''
if 'last_filename' not in st.session_state:
    st.session_state['last_filename'] = ''


with st.sidebar:
    st.markdown('## 📘 ERIA')
    st.markdown('**Education Regulation Impact Analyzer**')
    st.markdown('---')
    input_mode = st.radio('Input method', ['Upload PDF', 'Paste Text'])
    st.markdown('---')
    st.markdown('**Supported sources**')
    st.markdown('- UGC Circulars\n- AICTE Notifications\n- NAAC Guidelines\n- NIRF Frameworks\n- Ministry of Education')
    st.markdown('---')
    st.caption('GUVI x HCL Capstone · Groq + Llama 3')

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown('<p class="main-title">📘 Education Regulation Impact Analyzer</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Simplifying education policies for every institution · GUVI x HCL</p>', unsafe_allow_html=True)
st.markdown('---')

# ── Input ────────────────────────────────────────────────────────────────────
regulation_text = ''

if input_mode == 'Upload PDF':
    uploaded_file = st.file_uploader(
        'Upload regulation PDF (UGC / AICTE / NAAC / Ministry of Education)',
        type=['pdf']
    )
    if uploaded_file is not None:
        if uploaded_file.name != st.session_state['last_filename']:
            with st.spinner('Extracting text from PDF...'):
                extracted = extract_text_from_pdf(uploaded_file)
            st.session_state['pdf_text'] = extracted
            st.session_state['last_filename'] = uploaded_file.name

        if st.session_state['pdf_text']:
            st.success(f'✅ Extracted {len(st.session_state["pdf_text"])} characters from "{uploaded_file.name}"')
            with st.expander('Preview extracted text', expanded=False):
                st.text_area('', st.session_state['pdf_text'][:3000], height=180, disabled=True)
            regulation_text = st.session_state['pdf_text']
        else:
            st.error('❌ Could not extract text. Make sure it is a text-based PDF (not a scanned image).')
            st.info('💡 Tip: Try selecting text in the PDF with your cursor. If you cannot, it is a scanned PDF.')

else:
    col1, col2 = st.columns([4, 1])
    with col2:
        # Fix: set session state key directly — this works even when text_area has a key=
        if st.button('Load sample'):
            st.session_state['text_area_widget_key'] = SAMPLE_TEXT
            st.rerun()

    # Fix: when text_area has key=, Streamlit controls value via session_state[key]
    # So we must NOT pass value= here. Instead pre-set session_state[key] above.
    regulation_text = st.text_area(
        'Paste regulation text here',
        height=220,
        placeholder='Paste any UGC / AICTE / NAAC circular text...',
        key='text_area_widget_key'
    )

# ── Analyze button ────────────────────────────────────────────────────────────
st.markdown('')
analyze_clicked = st.button(
    '🔍 Analyze Regulation',
    type='primary',
    use_container_width=True,
    disabled=not bool(regulation_text and regulation_text.strip())
)

if not regulation_text:
    st.info('Upload a PDF or paste regulation text above to begin.')

# ── Results ───────────────────────────────────────────────────────────────────
if analyze_clicked and regulation_text.strip():
    with st.spinner('Analyzing with AI... please wait 10-20 seconds'):
        result = analyze_regulation(regulation_text)

    if 'error' in result:
        st.error(f"Analysis failed: {result['error']}")
        st.stop()

    st.success('✅ Analysis complete!')
    st.markdown('---')

    st.markdown('<p class="section-hdr">Classification</p>', unsafe_allow_html=True)
    st.markdown(f'<span class="cat-pill">📂 {result.get("category", "Unknown")}</span>', unsafe_allow_html=True)
    tags = ''.join(f'<span class="tag-pill">{t}</span>' for t in result.get('topic_tags', []))
    st.markdown(tags, unsafe_allow_html=True)
    st.markdown('---')

    st.markdown('<p class="section-hdr">Plain-Language Summary</p>', unsafe_allow_html=True)
    st.markdown(f'<div class="summary-box">{result.get("summary", "")}</div>', unsafe_allow_html=True)
    st.markdown('---')

    st.markdown('<p class="section-hdr">Stakeholder Impact</p>', unsafe_allow_html=True)
    icons = {
        'Students': '🎓', 'Faculty': '👩‍🏫',
        'Colleges / Universities': '🏛️',
        'Academic Administrators': '🗂️',
        'Accreditation / Compliance Teams': '✅'
    }
    cols = st.columns(2)
    for i, s in enumerate(result.get('stakeholders', [])):
        with cols[i % 2]:
            st.markdown(
                f'<div class="stake-card"><strong>{icons.get(s.get("name",""),"📌")} {s["name"]}</strong><br>'
                f'<span style="color:#444;font-size:0.88rem;">{s["impact"]}</span></div>',
                unsafe_allow_html=True
            )
    st.markdown('---')

    st.markdown('<p class="section-hdr">Impact Timeline</p>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="impact-card short-card"><strong>🔵 Short-term (0-1 yr)</strong><br><br>{result.get("short_term","")}</div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="impact-card mid-card"><strong>🟡 Medium-term (1-5 yr)</strong><br><br>{result.get("medium_term","")}</div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="impact-card long-card"><strong>🟢 Long-term (5+ yr)</strong><br><br>{result.get("long_term","")}</div>', unsafe_allow_html=True)
    st.markdown('---')

    st.markdown('<p class="section-hdr">Positives & Risks</p>', unsafe_allow_html=True)
    pc1, pc2 = st.columns(2)
    with pc1:
        st.markdown('**✅ Positives**')
        for p in result.get('positives', []):
            st.markdown(f'<p class="pos-item">✔ {p}</p>', unsafe_allow_html=True)
    with pc2:
        st.markdown('**⚠️ Risks**')
        for r in result.get('risks', []):
            st.markdown(f'<p class="risk-item">✘ {r}</p>', unsafe_allow_html=True)
    st.markdown('---')

    report = (
        f"ERIA Report\n{'='*50}\n"
        f"Category: {result.get('category','')}\n"
        f"Tags: {', '.join(result.get('topic_tags',[]))}\n\n"
        f"SUMMARY\n{'-'*40}\n{result.get('summary','')}\n\n"
        f"STAKEHOLDERS\n{'-'*40}\n"
        + '\n'.join(f"{s['name']}:\n  {s['impact']}" for s in result.get('stakeholders',[]))
        + f"\n\nIMPACT TIMELINE\n{'-'*40}\n"
        f"Short-term : {result.get('short_term','')}\n"
        f"Medium-term: {result.get('medium_term','')}\n"
        f"Long-term  : {result.get('long_term','')}\n\n"
        + "POSITIVES\n" + '\n'.join(f'• {p}' for p in result.get('positives',[]))
        + '\n\nRISKS\n' + '\n'.join(f'• {r}' for r in result.get('risks',[]))
    )
    st.download_button('⬇️ Download Report', data=report,
                       file_name='ERIA_report.txt', mime='text/plain',
                       use_container_width=True)

st.markdown('<p class="footer">ERIA · GUVI x HCL Capstone · Powered by Groq + Llama 3</p>', unsafe_allow_html=True)
