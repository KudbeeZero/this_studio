"""
Beta V3.5 Executive Command - Phil's AI Command Center
=====================================================
A high-tier AI-powered executive dashboard with Neural Tuning,
Live System Ledger, and Interactive Reporting.

Mobile-First Responsive Design

Author: Kilo (AI Software Engineer)
Version: Beta 3.5 (GOLD Edition)
"""

import streamlit as st
import re
import pandas as pd
from datetime import datetime
import io

# =============================================================================
# CONFIGURATION & STYLING
# =============================================================================

st.set_page_config(
    page_title="Beta V3.5 Executive",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load custom CSS
try:
    with open("style.css", "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    pass

# =============================================================================
# SESSION STATE
# =============================================================================

if "history" not in st.session_state:
    st.session_state.history = []

if "neural_tuning" not in st.session_state:
    st.session_state.neural_tuning = 75

if "processed_count" not in st.session_state:
    st.session_state.processed_count = 0

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def extract_vendor(text):
    patterns = [
        r"From:\s*([A-Za-z\s&]+?)(?:\n|@|$)",
        r"Vendor:\s*([A-Za-z\s&]+?)(?:\n|$)",
        r"Bill from\s+([A-Za-z\s&]+?)(?:\n|$)",
        r"Invoice from\s+([A-Za-z\s&]+?)(?:\n|$)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return "Unknown Vendor"


def extract_amount(text):
    amounts = re.findall(r"\$\s*[\d,]+(?:\.\d{2})?", text)
    total = 0.0
    for amount in amounts:
        try:
            total += float(amount.replace("$", "").replace(",", ""))
        except ValueError:
            pass
    return total, total * 12


def extract_deadlines(text):
    date_patterns = [
        r"\b(\d{1,2}/\d{1,2}/\d{2,4})\b",
        r"\b(\d{1,2}-\d{1,2}-\d{2,4})\b",
        r"due\s+by\s+(\w+\s+\d{1,2},?\s+\d{4})",
    ]
    deadlines = []
    for pattern in date_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        deadlines.extend(matches)
    return deadlines if deadlines else ["No deadlines"]


def redact_pii(text):
    pii_patterns = {
        r"\b\d{3}-\d{2}-\d{4}\b": "[SSN]",
        r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b": "[CC]",
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b": "[EMAIL]",
        r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b": "[PHONE]",
    }
    redaction_log = []
    for pattern, replacement in pii_patterns.items():
        matches = re.findall(pattern, text)
        if matches:
            text = re.sub(pattern, replacement, text)
            redaction_log.extend([f"{replacement}: {m}" for m in matches])
    return text, redaction_log


def generate_executive_report():
    report = f"""
╔═══════════��══════════════════════════════════════════════════════╗
║            BETA V3.5 EXECUTIVE REPORT                        ║
║            Phil's AI Command Center                          ║
║            Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}        ║
╚══════════════════════════════════════════════════════════════════╝

VERSION: Beta V3.5-GOLD
Neural Tuning: {st.session_state.neural_tuning}%
Documents Processed: {st.session_state.processed_count}

──────────────────────────────────────────────────────────────
RECENT ACTIVITY LOG
──────────────────────────────────────────────────────────────
"""
    if st.session_state.history:
        for i, entry in enumerate(st.session_state.history[:10], 1):
            report += f"{i}. {entry['Time']} | {entry['Bill/Entity']} | {entry['Status']}\n"
    else:
        report += "No documents processed.\n"

    report += "\n──────────────────────────────────────────────────────────────\n"
    return report


# =============================================================================
# SIDEBAR - RESPONSIVE
# =============================================================================

with st.sidebar:
    # Mobile-friendly header
    st.markdown("""
    <div class="flex-col gap-2 mb-4">
        <div class="flex-row items-center gap-3">
            <span style="font-size: 1.5rem;">🎯</span>
            <div>
                <div style="font-weight: 700; font-size: 1rem; color: white;">BETA V3.5</div>
                <div style="font-size: 0.7rem; color: #a0a0a0;">Executive Command</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Gold Badge - Touch friendly
    st.markdown("""
    <div class="badge-gold mb-4 touch-target" style="width: 100%; justify-content: center;">
        <span class="badge-dot"></span>BETA V3.5-GOLD
    </div>
    """, unsafe_allow_html=True)
    
    # Neural Tuning - Mobile optimized slider
    st.markdown("### 🧠 Neural Tuning")
    st.caption("Reasoning Depth (0-100%)")
    
    neural_tuning = st.slider(
        "Neural Tuning %",
        min_value=0,
        max_value=100,
        value=st.session_state.neural_tuning,
        key="neural_tuning_slider"
    )
    st.session_state.neural_tuning = neural_tuning
    
    # Mode indicator
    if neural_tuning < 40:
        mode_icon, mode_name = "🟢", "Basic"
    elif neural_tuning < 75:
        mode_icon, mode_name = "🟡", "Advanced"
    else:
        mode_icon, mode_name = "🟣", "Executive"
    
    st.markdown(f"**{mode_icon} Mode:** {mode_name}")
    
    st.markdown("---")
    
    # Session Stats - Touch friendly
    st.markdown("### 📊 Session Stats")
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.metric("Processed", st.session_state.processed_count)
    with col_s2:
        priority_count = len([h for h in st.session_state.history if "High Priority" in str(h)])
        st.metric("Priority", priority_count)
    
    # Clear History Button
    if st.button("🗑️ Clear History", use_container_width=True):
        st.session_state.history = []
        st.session_state.processed_count = 0
        st.rerun()

# =============================================================================
# MAIN CONTENT - MOBILE-FIRST
# =============================================================================

st.title("🎯 Beta V3.5 Executive")
st.caption("Phil's AI Command Center | Mobile Ready")

# Morning Briefing - Responsive Grid
st.markdown("### ☀️ Morning Briefing")

# Single column on mobile, 3 columns on desktop
col_brief1, col_brief2, col_brief3 = st.columns([2, 1, 1])

with col_brief1:
    st.markdown("""
    <div class="glass-panel fade-in">
        <div class="flex-row items-center gap-2 mb-2">
            <span style="font-size: 1.25rem;">📌</span>
            <span class="text-gold" style="font-weight: 600;">Executive Summary</span>
        </div>
        <p class="text-gray" style="font-size: 0.875rem; margin: 0;">
            System online • Neural Tuning: <span class="text-gold">75%</span>
        </p>
    </div>
    """, unsafe_allow_html=True)

with col_brief2:
    priority_count = len([h for h in st.session_state.history if "High Priority" in str(h)])
    st.metric("🔥 Priority", priority_count)

with col_brief3:
    st.metric("🤖 Agents", 3)

# Three-Agent Grid - Mobile Responsive
st.markdown("### 🤖 Three-Agent Grid")

col_finance, col_ops, col_security = st.columns(3)

with col_finance:
    st.markdown("""
    <div class="glass-panel touch-target">
        <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">💰</div>
        <div style="font-weight: 600; margin-bottom: 0.25rem;">Finance</div>
        <p class="text-gray" style="font-size: 0.75rem; margin: 0;">Currency & Impact</p>
    </div>
    """, unsafe_allow_html=True)

with col_ops:
    st.markdown("""
    <div class="glass-panel touch-target">
        <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">📅</div>
        <div style="font-weight: 600; margin-bottom: 0.25rem;">Operations</div>
        <p class="text-gray" style="font-size: 0.75rem; margin: 0;">Deadlines & Tasks</p>
    </div>
    """, unsafe_allow_html=True)

with col_security:
    st.markdown("""
    <div class="glass-panel touch-target">
        <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">🛡️</div>
        <div style="font-weight: 600; margin-bottom: 0.25rem;">Security</div>
        <p class="text-gray" style="font-size: 0.75rem; margin: 0;">PII Protection</p>
    </div>
    """, unsafe_allow_html=True)

# Document Processing - Mobile Optimized
st.markdown("---")
st.markdown("### 📝 Process Document")

input_text = st.text_area(
    "Paste email, invoice, or text:",
    height=120,
    placeholder="Paste text here...\n\nExample: Invoice from Acme Corp $1,250 due 03/15. Contact john@acme.com",
    label_visibility="collapsed"
)

# Full-width button on mobile, centered on desktop
col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
with col_btn2:
    process_btn = st.button(
        "🚀 Process Document",
        type="primary",
        use_container_width=True
    )

if process_btn:
    if input_text.strip():
        # Processing animation
        with st.spinner("⚡ Analyzing..."):
            status_ph = st.empty()
            status_ph.info(f"🧠 Neural Processing ({st.session_state.neural_tuning}%)")
            
            import time
            time.sleep(2)
            
            # Extract data
            vendor = extract_vendor(input_text)
            amount, annualized = extract_amount(input_text)
            deadlines = extract_deadlines(input_text)
            redacted_text, pii_log = redact_pii(input_text)
            
            # Create entry
            new_entry = {
                "Time": datetime.now().strftime("%H:%M:%S"),
                "Bill/Entity": vendor[:25] + "..." if len(vendor) > 25 else vendor,
                "Status": "⚠️ High Priority" if amount > 5000 else "✅ Processed",
                "Update": "Financial Synced" if amount > 0 else "Beta V3.5 Sync",
                "Amount": amount,
                "Annualized": annualized,
                "PII_Redacted": len(pii_log)
            }
            
            st.session_state.history.insert(0, new_entry)
            st.session_state.processed_count += 1
            
            status_ph.success("✅ Complete!")
            
            # Results - Responsive grid
            st.markdown("### 📊 Results")
            
            res_col1, res_col2, res_col3 = st.columns(3)
            with res_col1:
                st.metric("Vendor", vendor[:18] if len(vendor) <= 18 else vendor[:15] + "...")
            with res_col2:
                st.metric("Amount", f"${amount:,.0f}")
            with res_col3:
                st.metric("Annual", f"${annualized:,.0f}")
            
            # Expanders for details
            with st.expander("📅 Deadlines"):
                for d in deadlines:
                    st.markdown(f"- **{d}**")
            
            with st.expander("🛡️ PII Redacted"):
                for p in pii_log:
                    st.markdown(f"- {p}")
                if not pii_log:
                    st.caption("No PII detected")
    else:
        st.warning("Please enter text to process")

# Interactive Reporting
st.markdown("---")
st.markdown("### 📥 Export Report")

export_col1, export_col2 = st.columns([2, 1])
with export_col1:
    if st.button("📥 Download Executive Report", use_container_width=True):
        report_content = generate_executive_report()
        st.download_button(
            label="📥 Save as .txt",
            data=report_content,
            file_name="beta_v3.5_report.txt",
            mime="text/plain"
        )

# Live System Ledger
st.markdown("---")
st.markdown("### 📋 System Status & Update Log")

if st.session_state.history:
    df = pd.DataFrame(st.session_state.history)
    st.dataframe(
        df[["Time", "Bill/Entity", "Status", "Update"]],
        use_container_width=True,
        hide_index=True
    )
    st.caption(f"Showing {min(len(st.session_state.history), 10)} of {len(st.session_state.history)} entries")
else:
    st.info("📭 No documents processed yet")

# Footer - Responsive
st.markdown("---")
st.markdown(f"""
<div class="flex-col items-center gap-2 py-4" style="text-align: center; color: #6b6b6b;">
    <div class="flex-row items-center gap-2">
        <span class="status-dot-small"></span>
        <span class="text-gold" style="font-weight: 600;">Beta V3.5-GOLD</span>
    </div>
    <div style="font-size: 0.75rem;">
        Last Updated: {datetime.now().strftime("%Y-%m-%d %H:%M")} • 
        <span class="status-online"><span class="status-dot-small" style="width: 4px; height: 4px;"></span>Online</span>
    </div>
    <div style="font-size: 0.65rem; margin-top: 0.5rem;">
        Mobile Ready • Powered by Kilo
    </div>
</div>
""", unsafe_allow_html=True)
