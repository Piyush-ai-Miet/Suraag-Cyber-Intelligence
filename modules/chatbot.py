"""
modules/chatbot.py — Suराग RAG Chatbot (Multi-Provider Fallback)
Answers investigator questions about uploaded IPDR data.
Structured context is sent — never raw CSV rows.

Fallback Chain:
  1. Gemini (multiple models)
  2. DeepSeek (REST API)
  3. OpenRouter (free tier)
  4. Smart Offline Fallback (keyword-based from analysis data)
"""

import streamlit as st
import requests
import json
import time
import pandas as pd
from config import (
    GEMINI_API_KEY, DEEPSEEK_API_KEY, OPENROUTER_API_KEY,
    APP_NAME, COLOR_ACCENT, COLOR_CARD, COLOR_BG, COLOR_BORDER,
)

# ── SDK Detection ────────────────────────────────────────
try:
    from google import genai as google_genai
    SDK_AVAILABLE = "genai"
except ImportError:
    try:
        import google.generativeai as genai
        SDK_AVAILABLE = "legacy"
    except ImportError:
        SDK_AVAILABLE = None
    google_genai = None

# ── Gemini Model Fallback Order ──────────────────────────
GEMINI_MODELS = [
    "gemini-2.5-flash-lite",   # fastest, lowest quota hit
    "gemini-2.5-flash",        # good balance
    "gemini-2.5-pro",          # best quality
]

# ── OpenRouter Free Models ───────────────────────────────
OPENROUTER_MODELS = [
    "meta-llama/llama-4-maverick:free",
    "google/gemini-2.5-flash-preview-05-20",
    "deepseek/deepseek-chat-v3-0324:free",
    "mistralai/mistral-small-3.1-24b-instruct:free",
]


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
    Never sends raw CSV rows to the model.
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


# ═══════════════════════════════════════════════════════════
# PROVIDER 1: GEMINI (Multiple Model Fallback)
# ═══════════════════════════════════════════════════════════

def _call_gemini(prompt: str, api_key: str) -> tuple[str | None, str | None]:
    """
    Try multiple Gemini models in sequence.
    Returns (answer, model_name) or (None, None) on total failure.
    """
    if not api_key or not SDK_AVAILABLE:
        return None, None

    for model_name in GEMINI_MODELS:
        for attempt in range(2):  # 2 attempts per model
            try:
                if SDK_AVAILABLE == "genai":
                    client = google_genai.Client(api_key=api_key)
                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                    )
                    answer = response.text.strip()
                else:
                    import google.generativeai as genai_legacy
                    genai_legacy.configure(api_key=api_key)
                    model = genai_legacy.GenerativeModel(model_name)
                    result = model.generate_content(prompt)
                    answer = result.text.strip()

                if answer:
                    return answer, f"Gemini ({model_name})"

            except Exception as e:
                err = str(e)
                # Retryable errors — wait and try again
                if ("503" in err or "UNAVAILABLE" in err) and attempt == 0:
                    time.sleep(1.5)
                    continue
                # Non-retryable for this model — move to next
                break

    return None, None


# ═══════════════════════════════════════════════════════════
# PROVIDER 2: DEEPSEEK (REST API)
# ═══════════════════════════════════════════════════════════

def _call_deepseek(prompt: str, api_key: str) -> tuple[str | None, str | None]:
    """
    Call DeepSeek chat completions API.
    Returns (answer, provider_name) or (None, None) on failure.
    """
    if not api_key:
        return None, None

    try:
        resp = requests.post(
            "https://api.deepseek.com/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            },
            json={
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 1024,
                "temperature": 0.7,
            },
            timeout=30,
        )
        if resp.status_code == 200:
            data = resp.json()
            answer = data["choices"][0]["message"]["content"].strip()
            if answer:
                return answer, "DeepSeek"
    except Exception:
        pass

    return None, None


# ═══════════════════════════════════════════════════════════
# PROVIDER 3: OPENROUTER (Free Tier Models)
# ═══════════════════════════════════════════════════════════

def _call_openrouter(prompt: str, api_key: str) -> tuple[str | None, str | None]:
    """
    Call OpenRouter API with free-tier models.
    Returns (answer, provider_name) or (None, None) on failure.
    """
    if not api_key:
        return None, None

    for model_id in OPENROUTER_MODELS:
        try:
            resp = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}",
                    "HTTP-Referer": "https://suraag-ipdr.streamlit.app",
                    "X-Title": "Suराग IPDR Investigation Tool",
                },
                json={
                    "model": model_id,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 1024,
                    "temperature": 0.7,
                },
                timeout=30,
            )
            if resp.status_code == 200:
                data = resp.json()
                choices = data.get("choices", [])
                if choices:
                    answer = choices[0]["message"]["content"].strip()
                    if answer:
                        short_name = model_id.split("/")[-1].split(":")[0]
                        return answer, f"OpenRouter ({short_name})"
        except Exception:
            continue

    return None, None


# ═══════════════════════════════════════════════════════════
# PROVIDER 4: SMART OFFLINE FALLBACK
# ═══════════════════════════════════════════════════════════

def _offline_fallback(question: str, analysis_state: dict) -> str:
    """
    When ALL APIs are down, generate a useful answer from the
    analysis data itself using keyword matching.
    Always returns something — the chatbot never fully dies.
    """
    q = question.lower()
    stats = analysis_state.get("stats", {})
    risk_df = analysis_state.get("risk_scores")
    mitre_df = analysis_state.get("mitre_results")
    df = analysis_state.get("df")
    parts = []

    # ── TOR / Anonymity questions ────────────────────────
    if any(kw in q for kw in ["tor", "anonymity", "anonymous", "hidden", "dark web", "onion"]):
        tor_count = stats.get("tor_sessions", 0)
        if tor_count > 0:
            parts.append(f"**Tor Usage Detected:** {tor_count:,} sessions used Tor (The Onion Router — a tool to hide internet identity).")
            if risk_df is not None and not risk_df.empty and "TOR_Sessions" in risk_df.columns:
                tor_users = risk_df[risk_df["TOR_Sessions"] > 0]
                if not tor_users.empty:
                    names = ", ".join(tor_users["Subscriber_Name"].tolist())
                    parts.append(f"**Suspects using Tor:** {names}")
        else:
            parts.append("**No Tor usage** was detected in the analyzed IPDR data.")

    # ── Risk / Dangerous suspect questions ───────────────
    elif any(kw in q for kw in ["risk", "dangerous", "suspect", "threat", "critical", "high risk", "score"]):
        if risk_df is not None and not risk_df.empty:
            top = risk_df.sort_values("Risk_Score", ascending=False).head(3)
            parts.append("**Top Suspects by Risk Score:**")
            for _, row in top.iterrows():
                parts.append(
                    f"- **{row['Subscriber_Name']}** — Risk Score: **{row['Risk_Score']}/100** "
                    f"[{row['Risk_Level']}] | Sessions: {row['Total_Sessions']:,}"
                )
            highest = top.iloc[0]
            parts.append(f"\n🔴 **Most dangerous suspect:** {highest['Subscriber_Name']} "
                         f"with a risk score of {highest['Risk_Score']}/100.")
        else:
            parts.append("Risk scores have not been computed yet.")

    # ── IP / Connection questions ────────────────────────
    elif any(kw in q for kw in ["ip", "address", "connection", "server", "destination", "connect"]):
        unique_ips = stats.get("unique_ips", 0)
        foreign = stats.get("foreign_sessions", 0)
        parts.append(f"**IP Analysis Summary:**")
        parts.append(f"- Unique Destination IPs: **{unique_ips:,}**")
        parts.append(f"- Foreign IP Sessions: **{foreign:,}**")
        if df is not None and "Destination_IP" in df.columns:
            top_ips = df["Destination_IP"].value_counts().head(5)
            parts.append("\n**Top 5 Most Contacted IPs:**")
            for ip, count in top_ips.items():
                parts.append(f"- `{ip}` — {count:,} sessions")

    # ── Time / Hours / Pattern questions ─────────────────
    elif any(kw in q for kw in ["time", "hour", "night", "off-hour", "pattern", "when", "late", "midnight"]):
        off_hours = stats.get("off_hours_sessions", 0)
        parts.append(f"**Off-Hours Activity (12 AM – 5 AM):** {off_hours:,} sessions")
        if df is not None and "Hour_IST" in df.columns:
            hourly = df.groupby("Hour_IST").size()
            if not hourly.empty:
                peak = int(hourly.idxmax())
                parts.append(f"**Peak Activity Hour:** {peak:02d}:00 IST ({int(hourly.max()):,} sessions)")

    # ── MITRE ATT&CK questions ──────────────────────────
    elif any(kw in q for kw in ["mitre", "attack", "technique", "tactic", "att&ck", "ttp"]):
        if mitre_df is not None and not mitre_df.empty:
            parts.append(f"**MITRE ATT&CK Detections:** {len(mitre_df)} patterns found")
            for _, row in mitre_df.head(5).iterrows():
                parts.append(
                    f"- [{row['Risk Level']}] **{row['Pattern Detected']}** "
                    f"(Technique: {row['Technique ID']}) — {row['Sessions Affected']} sessions"
                )
        else:
            parts.append("No MITRE ATT&CK patterns were detected.")

    # ── Summary / Overview questions ─────────────────────
    elif any(kw in q for kw in ["summary", "overview", "tell me", "explain", "what happened", "brief"]):
        parts.append("**IPDR Analysis Summary:**")
        parts.append(f"- Total Sessions: **{stats.get('total_sessions', 0):,}**")
        parts.append(f"- Suspicious Sessions: **{stats.get('suspicious_sessions', 0):,}**")
        parts.append(f"- Tor Sessions: **{stats.get('tor_sessions', 0):,}**")
        parts.append(f"- Foreign IP Sessions: **{stats.get('foreign_sessions', 0):,}**")
        parts.append(f"- Off-Hours Sessions: **{stats.get('off_hours_sessions', 0):,}**")
        if risk_df is not None and not risk_df.empty:
            critical = risk_df[risk_df["Risk_Level"] == "CRITICAL"]
            if not critical.empty:
                names = ", ".join(critical["Subscriber_Name"].tolist())
                parts.append(f"\n🔴 **Critical-risk suspects:** {names}")

    # ── VPN questions ────────────────────────────────────
    elif any(kw in q for kw in ["vpn", "proxy", "tunnel", "masking"]):
        if df is not None and "Is_VPN_Suspected" in df.columns:
            vpn_count = int(df["Is_VPN_Suspected"].sum())
            parts.append(f"**VPN/Proxy Usage:** {vpn_count:,} sessions flagged as suspected VPN/proxy traffic.")
        else:
            parts.append("VPN detection data is not available in the current dataset.")

    # ── Generic fallback ─────────────────────────────────
    if not parts:
        parts.append("**Here's what I know from the analysis:**")
        parts.append(f"- Total Sessions: **{stats.get('total_sessions', 0):,}**")
        parts.append(f"- Suspicious Sessions: **{stats.get('suspicious_sessions', 0):,}**")
        parts.append(f"- Unique IPs: **{stats.get('unique_ips', 0):,}**")
        if risk_df is not None and not risk_df.empty:
            top = risk_df.sort_values("Risk_Score", ascending=False).iloc[0]
            parts.append(f"- Highest Risk: **{top['Subscriber_Name']}** ({top['Risk_Score']}/100)")
        parts.append("\n💡 *For more detailed AI analysis, please try again in a few minutes when API services recover.*")

    header = (
        "🔌 **Offline Mode** — All AI services are currently unavailable. "
        "Here's what I can tell you from the analyzed data:\n\n"
    )
    return header + "\n".join(parts)


# ═══════════════════════════════════════════════════════════
# MAIN FALLBACK CHAIN
# ═══════════════════════════════════════════════════════════

def _get_ai_response(
    prompt: str,
    question: str,
    analysis_state: dict,
    gemini_key: str,
    deepseek_key: str,
    openrouter_key: str,
) -> tuple[str, str]:
    """
    Master fallback chain. Tries providers in order:
      Gemini → DeepSeek → OpenRouter → Offline

    Returns (answer, provider_label).
    """
    # 1) Gemini
    answer, provider = _call_gemini(prompt, gemini_key)
    if answer:
        return answer, provider

    # 2) DeepSeek
    answer, provider = _call_deepseek(prompt, deepseek_key)
    if answer:
        return answer, provider

    # 3) OpenRouter
    answer, provider = _call_openrouter(prompt, openrouter_key)
    if answer:
        return answer, provider

    # 4) Offline — always returns something
    answer = _offline_fallback(question, analysis_state)
    return answer, "Offline Fallback"


# ═══════════════════════════════════════════════════════════
# STREAMLIT UI
# ═══════════════════════════════════════════════════════════

def render_chatbot(analysis_state: dict, chat_key: str = "chat_page1"):
    """Render the Suराग chatbot UI in Streamlit."""
    st.markdown("---")

    # Custom glassmorphism header card
    header_html = """
    <div style="
        background: linear-gradient(135deg, rgba(22, 27, 34, 0.7) 0%, rgba(13, 17, 23, 0.8) 100%);
        backdrop-filter: blur(15px);
        -webkit-backdrop-filter: blur(15px);
        border: 1px solid rgba(0, 212, 255, 0.2);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37), 0 0 15px rgba(0, 212, 255, 0.1);
    ">
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 8px;">
            <span style="font-size: 2.2rem; filter: drop-shadow(0 0 8px rgba(0, 212, 255, 0.6));">🤖</span>
            <div>
                <h3 style="
                    color: #00D4FF; 
                    margin: 0; 
                    font-family: 'Inter', sans-serif; 
                    font-weight: 700;
                    font-size: 1.3rem;
                    letter-spacing: 0.5px;
                    text-shadow: 0 0 10px rgba(0, 212, 255, 0.3);
                ">Ask Suराग — Your AI Investigation Assistant</h3>
                <p style="
                    color: #8B949E; 
                    margin: 2px 0 0 0; 
                    font-size: 0.8rem;
                    font-family: 'Inter', sans-serif;
                ">Multi-Provider AI · Gemini · DeepSeek · OpenRouter · Offline Fallback</p>
            </div>
        </div>
        <div style="
            height: 1px; 
            background: linear-gradient(90deg, rgba(0, 212, 255, 0.4), transparent); 
            margin: 12px 0;
        "></div>
        <p style="
            color: #E6EDF3; 
            margin: 0; 
            font-size: 0.875rem; 
            line-height: 1.5;
            font-family: 'Inter', sans-serif;
        ">
            Ask any question about the uploaded data in plain English. For example: 
            <code style="background: rgba(0, 212, 255, 0.1); color: #00D4FF; padding: 2px 6px; border-radius: 4px; font-family: monospace; font-size: 0.85rem; border: 1px solid rgba(0, 212, 255, 0.2);">Which suspect is most dangerous?</code> or 
            <code style="background: rgba(0, 212, 255, 0.1); color: #00D4FF; padding: 2px 6px; border-radius: 4px; font-family: monospace; font-size: 0.85rem; border: 1px solid rgba(0, 212, 255, 0.2);">Was Tor used?</code>
        </p>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)

    # Initialize chat history
    hist_key = f"{chat_key}_history"
    if hist_key not in st.session_state:
        st.session_state[hist_key] = []

    # Check prerequisites
    if not analysis_state or not analysis_state.get("loaded"):
        st.info("📂 Please upload and analyze an IPDR file first to enable the investigation assistant.")
        return

    # Gather all API keys (session state overrides .env)
    active_gemini_key = st.session_state.get("gemini_api_key", GEMINI_API_KEY)
    active_deepseek_key = st.session_state.get("deepseek_api_key", DEEPSEEK_API_KEY)
    active_openrouter_key = st.session_state.get("openrouter_api_key", OPENROUTER_API_KEY)

    # Show provider status
    providers_available = []
    if active_gemini_key:
        providers_available.append("Gemini")
    if active_deepseek_key:
        providers_available.append("DeepSeek")
    if active_openrouter_key:
        providers_available.append("OpenRouter")
    providers_available.append("Offline Fallback")

    # Render chat history style
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
    .chat-provider {
        font-size:10px; color:#8B949E; margin-top:4px;
        font-style:italic;
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
                provider_tag = ""
                if msg.get("provider"):
                    provider_tag = f"<div class='chat-provider'>⚡ {msg['provider']}</div>"
                st.markdown(
                    f"<div class='chat-bot'><span class='chat-avatar'>🤖</span>"
                    f"<div class='bubble'>{msg['content']}{provider_tag}</div></div>",
                    unsafe_allow_html=True,
                )

    # Input form to prevent infinite rerun/submit loop
    with st.form(key=f"{chat_key}_form", clear_on_submit=True):
        col1, col2 = st.columns([5, 1])
        with col1:
            user_input = st.text_input(
                "Your question",
                placeholder="Ask Suराग about this case (e.g. Which IP did Subscriber A connect to most?)...",
                label_visibility="collapsed",
            )
        with col2:
            submit_btn = st.form_submit_button("Send →", use_container_width=True)

    if submit_btn and user_input.strip():
        question = user_input.strip()
        st.session_state[hist_key].append({"role": "user", "content": question})

        context = _build_context(analysis_state)
        full_prompt = SYSTEM_PROMPT.format(context=context) + f"\n\nQuestion: {question}"

        with st.spinner("Suराग is thinking... (trying multiple AI providers)"):
            answer, provider = _get_ai_response(
                prompt=full_prompt,
                question=question,
                analysis_state=analysis_state,
                gemini_key=active_gemini_key,
                deepseek_key=active_deepseek_key,
                openrouter_key=active_openrouter_key,
            )

        st.session_state[hist_key].append({
            "role": "assistant",
            "content": answer,
            "provider": provider,
        })
        st.rerun()

    # Clear chat button
    if st.session_state[hist_key]:
        if st.button("🗑 Clear Chat", key=f"{chat_key}_clear"):
            st.session_state[hist_key] = []
            st.rerun()
