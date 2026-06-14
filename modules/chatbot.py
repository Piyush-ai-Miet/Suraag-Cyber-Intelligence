"""
modules/chatbot.py — Suराग RAG Chatbot (Gemini 1.5 Flash)
Answers investigator questions about the uploaded IPDR data.
Structured context is sent — never raw CSV rows.
"""

import streamlit as st
from config import GEMINI_API_KEY, APP_NAME, COLOR_ACCENT, COLOR_CARD, COLOR_BG, COLOR_BORDER
import pandas as pd

try:
    from google import genai as google_genai
    GEMINI_AVAILABLE = bool(GEMINI_API_KEY)
except ImportError:
    try:
        import google.generativeai as genai
        GEMINI_AVAILABLE = bool(GEMINI_API_KEY)
        if GEMINI_AVAILABLE:
            genai.configure(api_key=GEMINI_API_KEY)
    except ImportError:
        GEMINI_AVAILABLE = False
    google_genai = None


SYSTEM_PROMPT = """You are Suराग, an AI investigation assistant for Indian law enforcement.
You are speaking with a police officer investigating cyber crime using IPDR (Internet Protocol Detail Records).

Your role:
- Answer questions about the IPDR data clearly and simply
- Use plain language — avoid technical jargon
- If you use a technical term, immediately explain it in brackets
- Always refer to suspects by their name, not just their ID
- Format numbers in Indian style (e.g., 1,23,456)
- Keep responses concise but complete
- If you are unsure, say so clearly

IMPORTANT: The context below is structured data extracted from the IPDR file. Use ONLY this context to answer.
Never make up information not present in the context.

{context}
"""


def _build_context(analysis_state: dict) -> str:
    """
    Build a structured text summary of the IPDR analysis.
    Never sends raw CSV rows to Gemini.
    """
    if not analysis_state or not analysis_state.get("loaded"):
        return "No IPDR file has been analyzed yet."

    lines = ["=== IPDR ANALYSIS CONTEXT ===\n"]

    # Summary stats
    stats = analysis_state.get("stats", {})
    lines.append(f"Total Sessions Analyzed: {stats.get('total_sessions', 0):,}")
    lines.append(f"Unique Destination IPs: {stats.get('unique_ips', 0):,}")
    lines.append(f"Suspicious Sessions: {stats.get('suspicious_sessions', 0):,}")
    lines.append(f"Tor Sessions: {stats.get('tor_sessions', 0):,}")
    lines.append(f"Foreign IP Sessions: {stats.get('foreign_sessions', 0):,}")
    lines.append(f"Off-Hours Sessions: {stats.get('off_hours_sessions', 0):,}")
    lines.append("")

    # Risk scores
    risk_df = analysis_state.get("risk_scores")
    if risk_df is not None and not risk_df.empty:
        lines.append("=== SUSPECT RISK SCORES ===")
        for _, row in risk_df.iterrows():
            lines.append(
                f"- {row['Subscriber_Name']} (ID: {row['Subscriber_ID']}): "
                f"Risk Score {row['Risk_Score']}/100 [{row['Risk_Level']}] | "
                f"Sessions: {row['Total_Sessions']:,} | "
                f"Tor Sessions: {row.get('TOR_Sessions', 0)} | "
                f"Foreign Sessions: {row.get('Foreign_Sessions', 0)} | "
                f"Off-Hours: {row.get('Off_Hours_Sessions', 0)}"
            )
        lines.append("")

    # MITRE detections
    mitre_df = analysis_state.get("mitre_results")
    if mitre_df is not None and not mitre_df.empty:
        lines.append("=== MITRE ATT&CK DETECTIONS ===")
        for _, row in mitre_df.iterrows():
            lines.append(
                f"- [{row['Risk Level']}] {row['Pattern Detected']} "
                f"(Technique: {row['Technique ID']}, Tactic: {row['MITRE Tactic']}) "
                f"— {row['Sessions Affected']} sessions affected"
            )
        lines.append("")

    # Hourly breakdown
    df = analysis_state.get("df")
    if df is not None:
        hourly = df.groupby("Hour_IST").size()
        if not hourly.empty:
            peak_hour  = int(hourly.idxmax())
            peak_count = int(hourly.max())
            off_hours  = int(df["Is_Off_Hours"].sum())
            lines.append(f"=== TRAFFIC PATTERNS ===")
            lines.append(f"Peak Activity Hour: {peak_hour:02d}:00 IST ({peak_count} sessions)")
            lines.append(f"Sessions Between 12 AM–5 AM (suspicious window): {off_hours}")
            lines.append("")

    # Correlation (Page 2)
    corr = analysis_state.get("correlation")
    if corr:
        verdict = corr.get("verdict", {})
        lines.append("=== MULTI-SUSPECT CORRELATION ===")
        lines.append(f"Gang Probability Score: {corr.get('gang_score', 0)}%")
        lines.append(f"Verdict: {verdict.get('label', 'Unknown')}")
        shared_ips = corr.get("shared_ips")
        if shared_ips is not None and not shared_ips.empty:
            lines.append(f"Shared IP Addresses Found: {len(shared_ips)}")
            for _, row in shared_ips.head(5).iterrows():
                lines.append(f"  - {row['IP_Address']} used by: {row['Found_In_Suspects']}")

    return "\n".join(lines)


def render_chatbot(analysis_state: dict, chat_key: str = "chat_page1"):
    """Render the Suराग chatbot UI in Streamlit."""
    st.markdown("---")
    st.markdown(
        f"<h3 style='color:#00D4FF;margin-bottom:4px'>🤖 Ask Suराग — Your Investigation Assistant</h3>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='color:#8B949E;margin-bottom:16px'>Ask any question about the uploaded data in plain English. "
        "For example: <em>\"Which suspect is most dangerous?\"</em> or <em>\"Was Tor used?\"</em></p>",
        unsafe_allow_html=True,
    )

    # Initialize chat history
    hist_key = f"{chat_key}_history"
    if hist_key not in st.session_state:
        st.session_state[hist_key] = []

    # Check prerequisites
    if not analysis_state or not analysis_state.get("loaded"):
        st.info("📂 Please upload and analyze an IPDR file first to enable the investigation assistant.")
        return

    if not GEMINI_AVAILABLE:
        st.warning(
            "⚠️ Gemini API key not configured. Add your key to the `.env` file as `GEMINI_API_KEY=your_key_here`. "
            "Get a free key at [aistudio.google.com](https://aistudio.google.com)."
        )
        return

    # Render chat history
    chat_css = """
    <style>
    .chat-user {
        display:flex; justify-content:flex-end; margin:8px 0;
    }
    .chat-user .bubble {
        background:#1B4F72; color:#E6EDF3; border-radius:16px 16px 4px 16px;
        padding:10px 16px; max-width:75%; font-size:14px; line-height:1.5;
    }
    .chat-bot {
        display:flex; justify-content:flex-start; margin:8px 0;
    }
    .chat-bot .bubble {
        background:#161B22; color:#E6EDF3; border:1px solid #30363D;
        border-radius:16px 16px 16px 4px; padding:10px 16px;
        max-width:80%; font-size:14px; line-height:1.5;
    }
    .chat-avatar {
        font-size:20px; margin-right:8px; margin-top:4px;
    }
    </style>
    """
    st.markdown(chat_css, unsafe_allow_html=True)

    # Display history
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state[hist_key]:
            if msg["role"] == "user":
                st.markdown(
                    f"<div class='chat-user'><div class='bubble'>👤 {msg['content']}</div></div>",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"<div class='chat-bot'><span class='chat-avatar'>🤖</span>"
                    f"<div class='bubble'>{msg['content']}</div></div>",
                    unsafe_allow_html=True,
                )

    # Input
    col1, col2 = st.columns([5, 1])
    with col1:
        user_input = st.text_input(
            "Your question",
            key=f"{chat_key}_input",
            placeholder="e.g. Which suspect is most dangerous? Was Tor used?",
            label_visibility="collapsed",
        )
    with col2:
        send_btn = st.button("Send →", key=f"{chat_key}_send", use_container_width=True)

    if (send_btn or user_input) and user_input.strip():
        question = user_input.strip()
        st.session_state[hist_key].append({"role": "user", "content": question})

        context = _build_context(analysis_state)
        full_prompt = SYSTEM_PROMPT.format(context=context) + f"\n\nQuestion: {question}"

        with st.spinner("Suराग is thinking..."):
            try:
                try:
                    # Try new google.genai SDK first
                    client = google_genai.Client(api_key=GEMINI_API_KEY)
                    response = client.models.generate_content(
                        model="gemini-1.5-flash",
                        contents=full_prompt,
                    )
                    answer = response.text.strip()
                except Exception:
                    # Fallback to legacy google.generativeai
                    import google.generativeai as genai_legacy
                    genai_legacy.configure(api_key=GEMINI_API_KEY)
                    model = genai_legacy.GenerativeModel("gemini-1.5-flash")
                    result = model.generate_content(full_prompt)
                    answer = result.text.strip()
            except Exception as e:
                answer = (
                    f"I was unable to process your question at this time. "
                    f"Please check your API key in the .env file and try again. "
                    f"(Error: {str(e)[:120]})"
                )

        st.session_state[hist_key].append({"role": "assistant", "content": answer})
        st.rerun()

    # Clear chat
    if st.session_state[hist_key]:
        if st.button("🗑 Clear Chat", key=f"{chat_key}_clear"):
            st.session_state[hist_key] = []
            st.rerun()
