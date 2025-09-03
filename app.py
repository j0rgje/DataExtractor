import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
from datetime import datetime, timedelta
import time
import json
from typing import Dict, List, Optional
import base64
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go

# Page config
st.set_page_config(
    page_title="HSO Data Extractor",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS voor HSO branding en professionele uitstraling
st.markdown("""
<style>
    /* Color system tuned to match the provided design */
    :root {
        --bg-1: #0b2c3d;           /* dark teal */
        --bg-2: #0e2336;           /* navy */
        --card: #133349;           /* panel */
        --border: rgba(255,255,255,0.08);
        --text: #e6f1fa;           /* off-white */
        --text-muted: #99b3c7;
        --primary: #1fb6ff;        /* cyan-blue */
        --primary-strong: #00a3ff;
        --success: #22c55e;
        --warning: #f59e0b;
    }

    /* App background */
    .stApp {
        background: linear-gradient(180deg, var(--bg-1) 0%, var(--bg-2) 100%);
        color: var(--text);
    }
    .block-container { padding-top: 1rem; }

    /* Header */
    .main-header {
        background: linear-gradient(90deg, #0f3a56 0%, #0b2c3d 100%);
        padding: 0.75rem 1.25rem;
        border-radius: 12px;
        margin-bottom: 1.25rem;
        color: var(--text);
        border: 1px solid var(--border);
    }

    .avatar {
        width: 32px; height: 32px; border-radius: 999px;
        background: rgba(255,255,255,0.15);
        display:flex; align-items:center; justify-content:center;
        font-weight: 700; color: var(--text); letter-spacing: .5px;
    }

    /* Status card / panel */
    .status-card {
        background: var(--card);
        padding: 1.25rem;
        border-radius: 10px;
        border: 1px solid var(--border);
        margin-bottom: 1rem;
        color: var(--text);
    }

    /* Step containers */
    .step-container {
        background: rgba(255,255,255,0.02);
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        border: 1px solid var(--border);
        color: var(--text);
    }
    .step-active { border-color: var(--primary); background: rgba(31,182,255,0.06); }
    .step-completed { border-color: var(--success); background: rgba(34,197,94,0.06); }

    /* Metrics */
    .metric-card {
        background: rgba(255,255,255,0.04);
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        border: 1px solid var(--border);
        color: var(--text);
    }

    /* Upload area */
    .upload-area {
        border: 2px dashed rgba(255,255,255,0.15);
        border-radius: 10px;
        padding: 2.5rem;
        text-align: center;
        margin: 1rem 0;
        color: var(--text-muted);
        background: rgba(255,255,255,0.02);
    }

    /* Comparison panels */
    .comparison-container { display: flex; gap: 1.25rem; margin: 1rem 0; }
    .comparison-side {
        flex: 1; background: rgba(255,255,255,0.03);
        padding: 1rem; border-radius: 10px; border: 1px solid var(--border);
        color: var(--text);
    }

    /* Pills for statuses */
    .pill { display: inline-flex; align-items:center; gap: .4rem; padding: .25rem .6rem; border-radius: 999px; font-size: .85rem; border:1px solid var(--border); }
    .pill-success { background: rgba(34,197,94,0.12); color: #a7f3d0; }
    .pill-warn { background: rgba(245,158,11,0.12); color: #fde68a; }

    .dot { width:8px; height:8px; border-radius:999px; display:inline-block; }
    .dot--success { background:#22c55e; }
    .dot--warn { background:#f59e0b; }

    /* Make default Streamlit controls blend on dark */
    .stSelectbox, .stTextInput, .stNumberInput, .stDataFrame, .stDateInput { color: var(--text); }
    .stMarkdown, .stCaption, .stText { color: var(--text); }

    /* Links & accents */
    a { color: var(--primary); }

    /* Buttons */
    .stButton > button {
        border-radius: 999px !important;
        padding: 0.5rem 1rem !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        background: linear-gradient(180deg, #1fb6ff, #00a3ff) !important;
        color: #062234 !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 12px rgba(0,163,255,0.25) !important;
    }
    .stButton > button:hover { filter: brightness(1.05); }
    .stButton > button:disabled { opacity: .6; box-shadow: none !important; }

    /* Inputs */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select {
        background: rgba(255,255,255,0.05);
        border: 1px solid var(--border);
        color: var(--text);
        border-radius: 999px;
    }

    /* Stepper */
    .progress-steps { display:flex; gap:.5rem; align-items:center; background: rgba(255,255,255,0.04); border:1px solid var(--border); border-radius:999px; padding:.4rem; }
    .progress-steps .step { display:flex; align-items:center; gap:.5rem; padding:.45rem .8rem; border-radius:999px; border:1px solid transparent; color: var(--text-muted); }
    .progress-steps .step--active { background: rgba(31,182,255,0.12); border-color: rgba(31,182,255,0.35); color: var(--text); }
    .progress-steps .step--done { background: rgba(34,197,94,0.12); border-color: rgba(34,197,94,0.35); color: var(--text); }
    .step__icon { width:16px; height:16px; display:inline-block; }
</style>
""", unsafe_allow_html=True)

class DataExtractorApp:
    def __init__(self):
        self.init_session_state()
        # Preload logo (if present)
        self._logo_b64 = self._load_logo_b64()
        
    def init_session_state(self):
        """Initialiseer session state variabelen"""
        if 'current_page' not in st.session_state:
            st.session_state['current_page'] = 'overview'
        if 'documents' not in st.session_state:
            st.session_state['documents'] = self.load_sample_documents()
        if 'current_process' not in st.session_state:
            st.session_state['current_process'] = {
                'step': 1,
                'document': None,
                'text_content': None,
                'extracted_data': None,
                'status': 'idle'
            }
            
    def load_sample_documents(self) -> List[Dict]:
        """Laad voorbeelddocumenten voor demo"""
        base_date = datetime.now()
        return [
            {
                'id': f'APO-{200 + i:05d}',
                'name': 'JASA Packaging Solutions B.V.',
                'order_number': f'APO-{200 + i:05d}',
                'date_created': (base_date - timedelta(days=i)).strftime('%Y-%m-%d'),
                'status': 'Completed' if i < 7 else 'Uncompleted',
                'file_size': f"{2.1 + i * 0.3:.1f} MB",
                'document_type': 'Purchase Order'
            }
            for i in range(12)
        ]
    
    def render_header(self):
        """Render hoofdheader met HSO branding"""
        logo_html = """
            <div style="display:flex; align-items:center; gap:.75rem;">
                {logo}
            </div>
        """.format(
            logo=(f'<img src="data:image/png;base64,{self._logo_b64}" alt="HSO Data Extractor" style="height:32px;">'
                  if self._logo_b64 else '<h1 style="margin:0; font-size:1.4rem;">HSO Data Extractor</h1>')
        )

        st.markdown(f"""
        <div class="main-header">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>{logo_html}</div>
                <div style="text-align: right; color: var(--text);">
                    <div style="display:flex; align-items:center; gap:.6rem;">
                        <div class="avatar">JD</div>
                        <div>
                            <div style="font-weight:600;">Jane Doe</div>
                            <div style="font-size:0.8rem; opacity:.8;">Procurement Specialist</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    def _load_logo_b64(self) -> Optional[str]:
        """Zoek naar het logo-bestand en geef base64 terug als gevonden.
        Ondersteunt zowel 'assets/hso_logo_data_extractor 1.png' als root pad.
        """
        try:
            candidates = [
                Path("assets") / "hso_logo_data_extractor 1.png",
                Path("hso_logo_data_extractor 1.png"),
                Path("assets") / "hso_logo_data_extractor.png",
            ]
            for p in candidates:
                if p.exists() and p.is_file():
                    return base64.b64encode(p.read_bytes()).decode("utf-8")
        except Exception:
            pass
        return None
    
    def render_overview_screen(self):
        """Render het overzichtsscherm met documentstatus"""
        st.markdown("# Processed order overview")

        # Metrics en filters
        col1, col2, col3, col4 = st.columns(4)

        completed_count = len([d for d in st.session_state.documents if d['status'] == 'Completed'])
        pending_count = len([d for d in st.session_state.documents if d['status'] == 'Uncompleted'])

        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="color: #10b981; margin: 0;">{completed_count}</h3>
                <p style="margin: 0;">Completed</p>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="color: #f59e0b; margin: 0;">{pending_count}</h3>
                <p style="margin: 0;">Pending</p>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="color: #3b82f6; margin: 0;">{len(st.session_state.documents)}</h3>
                <p style="margin: 0;">Total</p>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            if st.button("Process a new order", type="primary", use_container_width=True):
                st.session_state.current_page = 'process'
                st.rerun()

        st.markdown("---")

        # Zoek en filter functies
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            search_term = st.text_input("Search an order by name or number", placeholder="Zoek op naam of ordernummer...")
        with col2:
            status_filter = st.selectbox("Status", ["All statuses", "Completed", "Uncompleted"])
        with col3:
            year_filter = st.selectbox("Year", ["All years", "2024", "2023"])

        # Filter documenten
        filtered_docs = st.session_state.documents
        if search_term:
            filtered_docs = [d for d in filtered_docs if 
                             search_term.lower() in d['name'].lower() or 
                             search_term.lower() in d['order_number'].lower()]
        if status_filter != "All statuses":
            filtered_docs = [d for d in filtered_docs if d['status'] == status_filter]

        # Documententabel
        st.markdown("### Document Status")

        if filtered_docs:
            df = pd.DataFrame(filtered_docs)

            # Aangepaste weergave van de tabel
            for idx, doc in enumerate(filtered_docs):
                with st.container():
                    col1, col2, col3, col4, col5, col6 = st.columns([3, 2, 2, 1, 1, 1])

                    with col1:
                        st.write(f"**{doc['name']}**")
                    with col2:
                        st.write(doc['order_number'])
                    with col3:
                        st.write(doc['date_created'])
                    with col4:
                        if doc['status'] == 'Completed':
                            st.markdown('<span class="pill pill-success"><span class="dot dot--success"></span> Completed</span>', unsafe_allow_html=True)
                        else:
                            st.markdown('<span class="pill pill-warn"><span class="dot dot--warn"></span> Uncompleted</span>', unsafe_allow_html=True)
                    with col5:
                        st.write(doc['file_size'])
                    with col6:
                        st.button("View", key=f"view_{doc['id']}_{idx}", help="View document")

                st.markdown("---")
        else:
            st.info("Geen documenten gevonden met de huidige filters.")

        # Paginering (simulatie)
        col1, col2, col3 = st.columns([6, 1, 1])
        with col1:
            st.caption(f"1-11 of {len(st.session_state.documents)} items")
        with col2:
            st.button("◀", disabled=True)
        with col3:
            st.button("▶")
    
    def render_process_screen(self):
        """Render het verwerkingsscherm met 4 stappen"""
        st.markdown("# Process a new order")

        # Progress indicator (custom stepper)
        steps = [
            {"key": 1, "label": "Upload"},
            {"key": 2, "label": "Converting the file to text"},
            {"key": 3, "label": "Extracting data from the file"},
            {"key": 4, "label": "Check the order"},
        ]
        current_step = st.session_state.current_process['step']

        def step_svg(kind: str) -> str:
            # simple inline SVGs for states
            if kind == "done":
                return '<svg class="step__icon" viewBox="0 0 24 24" fill="none" stroke="#22c55e" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M20 6L9 17l-5-5"/></svg>'
            elif kind == "active":
                return '<svg class="step__icon" viewBox="0 0 24 24" fill="none" stroke="#1fb6ff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="6"/></svg>'
            else:
                return '<svg class="step__icon" viewBox="0 0 24 24" fill="none" stroke="#99b3c7" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="6"/></svg>'

        step_html_parts = []
        for s in steps:
            if s["key"] < current_step:
                cls, icon = "step step--done", step_svg("done")
            elif s["key"] == current_step:
                cls, icon = "step step--active", step_svg("active")
            else:
                cls, icon = "step", step_svg("pending")
            step_html_parts.append(f'<div class="{cls}">{icon}<span>{s["label"]}</span></div>')

        st.markdown(f'<div class="progress-steps">{"".join(step_html_parts)}</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Stap-specifieke content
        if current_step == 1:
            self.render_upload_step()
        elif current_step == 2:
            self.render_converting_step()
        elif current_step == 3:
            self.render_extracting_step()
        elif current_step == 4:
            self.render_check_step()
        
        # Navigation
        col1, col2 = st.columns([1, 6])
        with col1:
            if st.button("Cancel"):
                st.session_state.current_page = 'overview'
                st.session_state.current_process = {
                    'step': 1,
                    'document': None,
                    'text_content': None,
                    'extracted_data': None,
                    'status': 'idle'
                }
                st.rerun()
    
    def render_upload_step(self):
        """Render upload stap"""
        st.markdown("""
        <div class="step-container step-active">
            <h3>Upload the purchase order</h3>
            <p>PDF is the only accepted file format<br>
            The maximum file size is 2MB</p>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "Drag and drop a PDF file",
            type=['pdf'],
            help="Sleep een PDF bestand hierheen of klik om te bladeren"
        )
        
        if uploaded_file is not None:
            st.success(f"Bestand geüpload: {uploaded_file.name}")
            
            col1, col2 = st.columns([1, 6])
            with col2:
                if st.button("Start Converting", type="primary"):
                    st.session_state.current_process['document'] = uploaded_file
                    st.session_state.current_process['step'] = 2
                    st.rerun()
    
    def render_converting_step(self):
        """Render converteer stap"""
        st.markdown("""
        <div class="step-container step-active">
            <h3>Converting the file to text</h3>
            <p>Het document wordt geconverteerd naar tekstformaat voor verdere verwerking...</p>
        </div>
        """, unsafe_allow_html=True)

        # Simuleer conversie proces
        if st.session_state.current_process['status'] != 'converting':
            st.session_state.current_process['status'] = 'converting'

        progress_bar = st.progress(0)
        status_text = st.empty()

        # Simuleer progressie
        for i in range(100):
            progress_bar.progress(i + 1)
            status_text.text(f'Converteer document... {i + 1}%')
            time.sleep(0.01)

        st.success("Document succesvol geconverteerd naar tekst!")

        # Sample tekst content voor demo
        st.session_state.current_process['text_content'] = """
        PURCHASE ORDER
        
        Order Number: APO-00199
        Date: 2024-01-15
        Supplier: JASA Packaging Solutions B.V.
        
        Items:
        - Product A: 100 units @ €25.00 = €2,500.00
        - Product B: 50 units @ €15.00 = €750.00
        
        Subtotal: €3,250.00
        VAT (21%): €682.50
        Total: €3,932.50
        
        Delivery Address:
        HSO Nederland B.V.
        Postbus 12345
        1234 AB Amsterdam
        """

        time.sleep(1)
        st.session_state.current_process['step'] = 3
        st.rerun()
    
    def render_extracting_step(self):
        """Render data extractie stap"""
        st.markdown("""
        <div class="step-container step-active">
            <h3>Extracting data from the file</h3>
            <p>Relevante gegevens worden geëxtraheerd uit het document...</p>
        </div>
        """, unsafe_allow_html=True)

        # Simuleer extractie proces
        progress_bar = st.progress(0)
        status_text = st.empty()

        extraction_steps = [
            "Detecteer document type...",
            "Identificeer header informatie...",
            "Extraheer ordergegevens...",
            "Verwerk line items...",
            "Berekend totalen...",
            "Valideer extracted data..."
        ]

        for i, step in enumerate(extraction_steps):
            progress = int((i + 1) / len(extraction_steps) * 100)
            progress_bar.progress(progress)
            status_text.text(step)
            time.sleep(0.5)

        st.success("Data succesvol geëxtraheerd!")

        # Sample extracted data voor demo
        st.session_state.current_process['extracted_data'] = {
            "order_number": "APO-00199",
            "date": "2024-01-15",
            "supplier": "JASA Packaging Solutions B.V.",
            "items": [
                {"product": "Product A", "quantity": 100, "unit_price": 25.00, "total": 2500.00},
                {"product": "Product B", "quantity": 50, "unit_price": 15.00, "total": 750.00}
            ],
            "subtotal": 3250.00,
            "vat_rate": 0.21,
            "vat_amount": 682.50,
            "total": 3932.50,
            "delivery_address": {
                "company": "HSO Nederland B.V.",
                "address": "Postbus 12345, 1234 AB Amsterdam"
            }
        }

        time.sleep(1)
        st.session_state.current_process['step'] = 4
        st.rerun()
    
    def render_check_step(self):
        """Render human check stap"""
        st.markdown("""
        <div class="step-container step-active">
            <h3>Check the order</h3>
            <p>Controleer de geëxtraheerde gegevens en corrigeer indien nodig</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Vergelijking tussen origineel en extracted data
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Original Document")
            st.markdown("""
            <div class="comparison-side">
                <h4>Originele tekst:</h4>
                <pre style="background: rgba(255,255,255,0.04); color: var(--text); padding: 1rem; border-radius: 6px; font-size: 0.85em; border:1px solid var(--border);">
PURCHASE ORDER

Order Number: APO-00199
Date: 2024-01-15
Supplier: JASA Packaging Solutions B.V.

Items:
- Product A: 100 units @ €25.00 = €2,500.00
- Product B: 50 units @ €15.00 = €750.00

Subtotal: €3,250.00
VAT (21%): €682.50
Total: €3,932.50

Delivery Address:
HSO Nederland B.V.
Postbus 12345
1234 AB Amsterdam
                </pre>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("### Extracted Data")
            
            extracted = st.session_state.current_process['extracted_data']
            
            # Bewerkbare velden voor correctie
            st.text_input("Order Number", value=extracted['order_number'], key="edit_order_number")
            st.date_input("Date", value=datetime.strptime(extracted['date'], '%Y-%m-%d'), key="edit_date")
            st.text_input("Supplier", value=extracted['supplier'], key="edit_supplier")
            
            st.markdown("**Line Items:**")
            items_df = pd.DataFrame(extracted['items'])
            edited_items = st.data_editor(items_df, use_container_width=True)
            
            col2a, col2b = st.columns(2)
            with col2a:
                st.number_input("Subtotal", value=extracted['subtotal'], key="edit_subtotal")
                st.number_input("VAT Amount", value=extracted['vat_amount'], key="edit_vat")
            with col2b:
                st.number_input("VAT Rate", value=extracted['vat_rate'], key="edit_vat_rate")
                st.number_input("Total", value=extracted['total'], key="edit_total")
        
        st.markdown("---")
        
        # Acties
        col1, col2, col3 = st.columns([1, 1, 4])
        
        with col1:
            if st.button("Approve", type="primary", use_container_width=True):
                # Simuleer opslaan naar Azure Blob Storage
                with st.spinner("Opslaan naar database..."):
                    time.sleep(2)
                
                st.success("Order succesvol verwerkt en opgeslagen!")
                
                # Voeg toe aan documents lijst
                new_doc = {
                    'id': extracted['order_number'],
                    'name': extracted['supplier'],
                    'order_number': extracted['order_number'],
                    'date_created': extracted['date'],
                    'status': 'Completed',
                    'file_size': "2.1 MB",
                    'document_type': 'Purchase Order'
                }
                st.session_state.documents.insert(0, new_doc)
                
                # Reset process
                st.session_state.current_process = {
                    'step': 1,
                    'document': None,
                    'text_content': None,
                    'extracted_data': None,
                    'status': 'idle'
                }
                
                time.sleep(2)
                st.session_state.current_page = 'overview'
                st.rerun()
        
        with col2:
            if st.button("Reject", use_container_width=True):
                st.error("Order gerejected. Terug naar upload.")
                st.session_state.current_process['step'] = 1
                st.rerun()
    
    def run(self):
        """Hoofdrunner voor de app"""
        self.render_header()
        
        # Navigation
        if st.session_state.current_page == 'overview':
            self.render_overview_screen()
        elif st.session_state.current_page == 'process':
            self.render_process_screen()

if __name__ == "__main__":
    app = DataExtractorApp()
    app.run()
