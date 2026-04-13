"""
ADRION 369 — Trinity Sentinel Dashboard v5.7
===============================================
Streamlit-based monitoring dashboard for the ADRION 369 decision engine.

Panels:
  1. Guardian Radar — 9-axis radar chart of Guardian compliance scores
  2. Audit Chain — Live chain status, length, last hash, verification
  3. Escalation Log — Recent escalations by decision/severity
  4. Decision Distribution — PROCEED/DENY/HOLD breakdown over time
  5. System Health — Redis connectivity, pipeline latency, attack counter

Usage:
    pip install streamlit plotly
    streamlit run dashboard/app.py

Note: This dashboard reads from in-memory state or JSON exports.
      It does NOT require a running Redis or Flask backend.
"""

import json
import math
import time
from pathlib import Path

try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False

try:
    import plotly.graph_objects as go
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False


# ── Guardian Radar Chart ────────────────────────────────────────────────────

GUARDIAN_LABELS = [
    "G1 Unity", "G2 Harmony", "G3 Rhythm", "G4 Causality",
    "G5 Transparency", "G6 Authenticity", "G7 Privacy",
    "G8 Nonmaleficence", "G9 Sustainability",
]

GUARDIAN_THRESHOLDS = {
    "G1 Unity": 0.87, "G2 Harmony": 0.87, "G3 Rhythm": 0.87,
    "G4 Causality": 0.87, "G5 Transparency": 0.87, "G6 Authenticity": 0.87,
    "G7 Privacy": 0.87, "G8 Nonmaleficence": 0.95, "G9 Sustainability": 0.87,
}


def create_guardian_radar(scores: dict) -> "go.Figure":
    """Create a 9-axis radar chart of Guardian compliance scores."""
    labels = list(GUARDIAN_LABELS)
    values = [scores.get(label, 0.0) for label in labels]
    thresholds = [GUARDIAN_THRESHOLDS[label] for label in labels]

    # Close the polygon
    labels_closed = labels + [labels[0]]
    values_closed = values + [values[0]]
    thresholds_closed = thresholds + [thresholds[0]]

    fig = go.Figure()

    # Threshold ring
    fig.add_trace(go.Scatterpolar(
        r=thresholds_closed, theta=labels_closed,
        fill="none", name="Threshold",
        line=dict(color="red", dash="dash", width=2),
    ))

    # Actual scores
    fig.add_trace(go.Scatterpolar(
        r=values_closed, theta=labels_closed,
        fill="toself", name="Current Scores",
        line=dict(color="#00cc88", width=3),
        fillcolor="rgba(0, 204, 136, 0.2)",
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 1.0]),
        ),
        showlegend=True,
        title="Guardian Compliance Radar",
        height=500,
    )
    return fig


# ── Decision Pie Chart ──────────────────────────────────────────────────────

DECISION_COLORS = {
    "PROCEED": "#00cc88",
    "DENY": "#ff4444",
    "HARD_VETO": "#cc0000",
    "HOLD_HUMAN_REVIEW": "#ffaa00",
    "HOLD_SENTINEL_REVIEW": "#ff8800",
    "HEALING_REQUIRED": "#8844ff",
}


def create_decision_pie(decisions: dict) -> "go.Figure":
    """Create a pie chart of decision distribution."""
    labels = list(decisions.keys())
    values = list(decisions.values())
    colors = [DECISION_COLORS.get(d, "#888888") for d in labels]

    fig = go.Figure(data=[go.Pie(
        labels=labels, values=values,
        marker=dict(colors=colors),
        hole=0.4,
    )])
    fig.update_layout(title="Decision Distribution", height=400)
    return fig


# ── Audit Chain Status Card ─────────────────────────────────────────────────

def render_chain_status(chain_summary: dict) -> None:
    """Render audit chain status as Streamlit metrics."""
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Chain Length", chain_summary.get("chain_length", 0))
    with col2:
        valid = chain_summary.get("chain_valid", False)
        st.metric("Chain Valid", "YES" if valid else "TAMPERED!")
    with col3:
        st.metric("Last Hash", chain_summary.get("last_hash", "n/a"))


# ── Escalation Log Table ───────────────────────────────────────────────────

def render_escalation_log(escalations: list) -> None:
    """Render escalation events as a Streamlit table."""
    if not escalations:
        st.info("No escalations recorded.")
        return

    rows = []
    for e in reversed(escalations[-20:]):  # Last 20, newest first
        rows.append({
            "Time": e.get("timestamp", "?"),
            "Decision": e.get("decision", "?"),
            "Score": f"{e.get('trinity_score', 0):.4f}",
            "Severity": e.get("severity", "?"),
            "Reason": e.get("reason", "")[:60],
        })
    st.table(rows)


# ── Load Audit Data from JSON ──────────────────────────────────────────────

def load_audit_json(path: str) -> dict:
    """Load exported audit chain JSON."""
    p = Path(path)
    if not p.exists():
        return {"version": "?", "chain_length": 0, "chain_valid": False, "records": []}
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


# ── Main Dashboard ──────────────────────────────────────────────────────────

def main():
    """Main Streamlit dashboard entry point."""
    if not HAS_STREAMLIT:
        print("Streamlit not installed. Run: pip install streamlit plotly")
        return
    if not HAS_PLOTLY:
        st.error("Plotly not installed. Run: pip install plotly")
        return

    st.set_page_config(
        page_title="ADRION 369 — Trinity Sentinel",
        page_icon="<shield>",
        layout="wide",
    )

    st.title("ADRION 369 — Trinity Sentinel Dashboard")
    st.caption("Real-time monitoring of the 162-dimensional decision engine")

    # ── Sidebar: Data Source ────────────────────────────────────────────
    st.sidebar.header("Data Source")
    mode = st.sidebar.radio("Mode", ["Demo Data", "Load JSON"])

    if mode == "Load JSON":
        uploaded = st.sidebar.file_uploader("Upload audit_log.json", type=["json"])
        if uploaded:
            data = json.load(uploaded)
        else:
            st.sidebar.info("Upload an exported audit chain JSON file.")
            data = None
    else:
        # Demo data for visualization testing
        data = _generate_demo_data()

    if data is None:
        st.warning("No data loaded. Use Demo Data or upload a JSON file.")
        return

    # ── Row 1: Guardian Radar + Chain Status ────────────────────────────
    col_left, col_right = st.columns([2, 1])

    with col_left:
        # Aggregate guardian scores from last record
        records = data.get("records", [])
        if records:
            last_record = records[-1]
            g_scores = last_record.get("guardian_scores", {})
            # Map to display labels
            display_scores = {}
            for k, v in g_scores.items():
                display_label = k.replace("_", " ")
                display_scores[display_label] = v
            fig = create_guardian_radar(display_scores)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No records to display Guardian radar.")

    with col_right:
        st.subheader("Audit Chain Status")
        render_chain_status({
            "chain_length": data.get("chain_length", 0),
            "chain_valid": data.get("chain_valid", False),
            "last_hash": records[-1]["record_hash"][:16] + "..." if records else "n/a",
        })

        # Decision breakdown
        decisions = {}
        for r in records:
            d = r.get("decision", "?")
            decisions[d] = decisions.get(d, 0) + 1

        st.subheader("Decision Statistics")
        for dec, count in sorted(decisions.items()):
            st.write(f"**{dec}**: {count}")

    # ── Row 2: Decision Distribution + Escalation Log ───────────────────
    col2_left, col2_right = st.columns(2)

    with col2_left:
        if decisions:
            fig = create_decision_pie(decisions)
            st.plotly_chart(fig, use_container_width=True)

    with col2_right:
        st.subheader("Recent Escalations")
        escalations = [r for r in records if r.get("decision") != "PROCEED"]
        render_escalation_log(escalations[-10:])

    # ── Row 3: System Health ────────────────────────────────────────────
    st.subheader("System Health")
    health_cols = st.columns(4)
    with health_cols[0]:
        st.metric("Total Records", len(records))
    with health_cols[1]:
        violations = sum(len(r.get("guardian_violations", [])) for r in records)
        st.metric("Total Violations", violations)
    with health_cols[2]:
        deny_count = sum(1 for r in records if r.get("decision") in ("DENY", "HARD_VETO"))
        st.metric("Blocked Actions", deny_count)
    with health_cols[3]:
        proceed_count = decisions.get("PROCEED", 0)
        total = len(records) or 1
        st.metric("Approval Rate", f"{100 * proceed_count / total:.1f}%")


def _generate_demo_data() -> dict:
    """Generate demo data for testing the dashboard."""
    import hashlib
    import random
    random.seed(42)

    records = []
    prev_hash = "0" * 64
    decisions_pool = ["PROCEED"] * 7 + ["DENY"] + ["HOLD_HUMAN_REVIEW"] + ["HOLD_SENTINEL_REVIEW"]

    for seq in range(50):
        decision = random.choice(decisions_pool)
        t_score = random.uniform(0.3, 0.95)
        g_scores = {
            "G1_Unity": random.uniform(0.80, 0.98),
            "G2_Harmony": random.uniform(0.82, 0.97),
            "G3_Rhythm": random.uniform(0.84, 0.96),
            "G4_Causality": random.uniform(0.85, 0.97),
            "G5_Transparency": random.uniform(0.83, 0.98),
            "G6_Authenticity": random.uniform(0.81, 0.96),
            "G7_Privacy": random.uniform(0.85, 0.99),
            "G8_Nonmaleficence": random.uniform(0.90, 0.99),
            "G9_Sustainability": random.uniform(0.84, 0.97),
        }
        violations = []
        if decision == "DENY":
            violations = ["G8_Nonmaleficence"]
            g_scores["G8_Nonmaleficence"] = random.uniform(0.60, 0.89)

        payload = f"{prev_hash}|{seq}|{t_score}|{decision}"
        record_hash = hashlib.sha256(payload.encode()).hexdigest()

        records.append({
            "seq": seq,
            "timestamp": f"2026-04-13T{10 + seq // 60:02d}:{seq % 60:02d}:00Z",
            "prev_hash": prev_hash,
            "record_hash": record_hash,
            "version": "5.7.0",
            "input_hash": hashlib.sha256(f"input-{seq}".encode()).hexdigest(),
            "trinity_score": round(t_score, 4),
            "decision": decision,
            "guardian_violations": violations,
            "guardian_scores": {k: round(v, 4) for k, v in g_scores.items()},
            "pad_state": [round(random.uniform(-0.3, 0.3), 3) for _ in range(3)],
            "severity": random.choice(["LOW", "MEDIUM", "HIGH"]),
        })
        prev_hash = record_hash

    return {
        "version": "5.7.0",
        "chain_length": len(records),
        "chain_valid": True,
        "records": records,
    }


if __name__ == "__main__":
    main()
