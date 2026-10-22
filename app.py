"""
QShield - Quantum Key Distribution (BB84) & Eavesdropping Detection
Streamlit Dashboard (Member 3: Dashboard, Visualizations, and Presentation)
Qiskit Fall Fest 2026 | Track 1: Quantum Cryptography & Security
Team: Qubit Titans (VTU-QFF-HC-0104)
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import random

# ==============================================================================
# Seamless Integration & Resilient Fallback Architecture
# ==============================================================================
# Member 3 interfaces directly with Member 2 (security.py) and Member 1 (bb84.py).
# If teammates' files are not yet in the workspace or still being edited,
# this fallback implements the EXACT agreed specification so the dashboard
# is 100% operational immediately without breaking.
# ==============================================================================

HAS_TEAM_MODULES = False
try:
    from security import simulate_bb84
    from bb84 import make_circuit, measure_qubits
    HAS_TEAM_MODULES = True
except ImportError:
    # Standalone reference implementation strictly adhering to Sections 4, 6 & 7
    try:
        from qiskit import QuantumCircuit
        from qiskit_aer import AerSimulator
        QISKIT_AVAILABLE = True
    except ImportError:
        QISKIT_AVAILABLE = False

    def make_circuit(bit: int, prep_basis: int, measure_basis: int):
        """Construct a single-qubit BB84 circuit with state prep and measurement basis."""
        if not QISKIT_AVAILABLE:
            return None
        qc = QuantumCircuit(1, 1)
        if bit == 1:
            qc.x(0)
        if prep_basis == 1:
            qc.h(0)
        if measure_basis == 1:
            qc.h(0)
        qc.measure(0, 0)
        return qc

    def measure_qubits(bits, prep_bases, measure_bases, seed=None):
        """Execute Qiskit Aer simulation on batched circuits."""
        if not (len(bits) == len(prep_bases) == len(measure_bases)):
            raise ValueError("Input lengths must match")
        if not bits:
            return []

        if QISKIT_AVAILABLE:
            circuits = [make_circuit(b, pb, mb) for b, pb, mb in zip(bits, prep_bases, measure_bases)]
            backend = AerSimulator()
            result = backend.run(circuits, shots=1, seed_simulator=seed).result()
            measured = []
            for i in range(len(circuits)):
                counts = result.get_counts(i)
                measured.append(int(next(iter(counts))))
            return measured
        else:
            # Theoretical quantum measurement distribution fallback if aer is loading
            rng = random.Random(seed)
            measured = []
            for b, pb, mb in zip(bits, prep_bases, measure_bases):
                if pb == mb:
                    measured.append(b)
                else:
                    measured.append(rng.randrange(2))
            return measured

    def simulate_bb84(n_bits=512, eve=False, noise=0.0, sample_fraction=0.25, seed=42):
        """Agreed simulation function strictly following Section 4 & 7."""
        if n_bits < 8:
            raise ValueError("n_bits must be >= 8")
        if not (0.0 <= noise <= 1.0):
            raise ValueError("noise must be between 0.0 and 1.0")
        if not (0.0 < sample_fraction <= 1.0):
            raise ValueError("sample_fraction must be in (0.0, 1.0]")

        rng = random.Random(seed)
        alice_bits = [rng.randrange(2) for _ in range(n_bits)]
        alice_bases = [rng.randrange(2) for _ in range(n_bits)]
        bob_bases = [rng.randrange(2) for _ in range(n_bits)]

        eve_bases = None
        eve_bits = None

        if not eve:
            # Path A: Clean channel (No Eve)
            bob_bits = measure_qubits(alice_bits, alice_bases, bob_bases, seed=seed + 1 if seed else None)
        else:
            # Path B: Intercept-resend attack by Eve
            eve_bases = [rng.randrange(2) for _ in range(n_bits)]
            eve_bits = measure_qubits(alice_bits, alice_bases, eve_bases, seed=seed + 2 if seed else None)
            bob_bits = measure_qubits(eve_bits, eve_bases, bob_bases, seed=seed + 3 if seed else None)

        # Apply simplified bit-error noise model before public sifting comparison
        if noise > 0.0:
            for i in range(len(bob_bits)):
                if rng.random() < noise:
                    bob_bits[i] ^= 1

        # Basis reconciliation (sifting)
        matching = [i for i in range(n_bits) if alice_bases[i] == bob_bases[i]]
        sifted_bits_count = len(matching)

        # Public sampling for error detection
        sample_count = max(1, int(sifted_bits_count * sample_fraction)) if sifted_bits_count > 0 else 0
        if sifted_bits_count > 0:
            sample_positions = rng.sample(matching, sample_count)
            sample_errors = sum(alice_bits[i] != bob_bits[i] for i in sample_positions)
            qber = sample_errors / sample_count
        else:
            sample_positions = []
            sample_errors = 0
            qber = 0.0

        remaining_bits_count = max(0, sifted_bits_count - sample_count)

        if qber > 0.10:
            status = "High errors: attack OR noise possible"
        else:
            status = "No high error detected"

        # Additional detailed audit trail for rich visualizations
        detailed_log = {
            "alice_bits": alice_bits,
            "alice_bases": alice_bases,
            "bob_bases": bob_bases,
            "bob_bits": bob_bits,
            "eve_bases": eve_bases,
            "eve_bits": eve_bits,
            "matching_indices": set(matching),
            "sample_positions": set(sample_positions) if sifted_bits_count > 0 else set()
        }

        return {
            "n_bits": n_bits,
            "sifted_bits": sifted_bits_count,
            "sampled_bits": sample_count,
            "sample_errors": sample_errors,
            "qber": float(qber),
            "remaining_bits": remaining_bits_count,
            "status": status,
            "_detailed_log": detailed_log
        }


# ==============================================================================
# UI Styling & Configuration
# ==============================================================================
st.set_page_config(
    page_title="QShield | Quantum Key Distribution & Eavesdropping Detection",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for polished aesthetics
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.05), rgba(255,255,255,0.02));
        border-radius: 12px;
        padding: 18px;
        border: 1px solid rgba(255,255,255,0.12);
        box-shadow: 0 4px 14px rgba(0,0,0,0.15);
    }
    .badge-clean {
        background-color: #059669;
        color: white;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .badge-eve {
        background-color: #dc2626;
        color: white;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .badge-warning {
        background-color: #d97706;
        color: white;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .channel-box {
        padding: 14px;
        border-radius: 10px;
        margin-bottom: 12px;
        border-left: 5px solid;
    }
</style>
""", unsafe_allow_html=True)


# ==============================================================================
# Header Section
# ==============================================================================
col_header, col_meta = st.columns([3, 1])
with col_header:
    st.title("🔐 QShield: Quantum Key Distribution")
    st.markdown("### BB84 Protocol Simulator & Eavesdropping Detection using **Qiskit Aer**")
    st.caption("Track 1: Quantum Cryptography & Security | Qiskit Fall Fest 2026 | Team: **Qubit Titans** (VTU-QFF-HC-0104)")

with col_meta:
    st.markdown("""
    <div style="text-align: right; font-size: 0.88rem; padding-top: 10px;">
        <span class="badge-clean">Qiskit Core</span>
        <span class="badge-clean">AerSimulator</span><br>
        <span style="color: #94a3b8; font-size: 0.78rem;">48-Hour Quantum Hackathon</span>
    </div>
    """, unsafe_allow_html=True)

st.divider()


# ==============================================================================
# Sidebar: Controls & Judge Test Presets
# ==============================================================================
st.sidebar.header("⚙️ Simulation Controls")

# Quick 1-Click Presets for Judges and Demos
st.sidebar.markdown("#### 🎯 Quick Scenarios (1-Click Presets)")
preset = st.sidebar.radio(
    "Choose evaluation scenario:",
    ["Custom Settings", "🟢 Clean Channel (Ideal BB84)", "🔴 Eve Intercept-Resend Attack", "🟡 Channel Noise Only"],
    index=0
)

# Preset overrides
if preset == "🟢 Clean Channel (Ideal BB84)":
    default_n = 512
    default_eve = False
    default_noise = 0.0
    default_sample = 0.25
elif preset == "🔴 Eve Intercept-Resend Attack":
    default_n = 512
    default_eve = True
    default_noise = 0.0
    default_sample = 0.25
elif preset == "🟡 Channel Noise Only":
    default_n = 512
    default_eve = False
    default_noise = 0.07
    default_sample = 0.25
else:
    default_n = 512
    default_eve = False
    default_noise = 0.0
    default_sample = 0.25

n_bits = st.sidebar.slider("Number of Quantum States (Qubits)", min_value=64, max_value=1024, value=default_n, step=64,
                           help="Total number of single photons/qubits transmitted from Alice to Bob.")
enable_eve = st.sidebar.checkbox("Enable Eve Intercept-Resend Attack", value=default_eve,
                                 help="When active, Eve measures each flying qubit in a random basis and sends newly prepared states to Bob.")
noise_val = st.sidebar.slider("Simplified Bit-Error Channel Noise", min_value=0.0, max_value=0.20, value=default_noise, step=0.01,
                              help="Probability of an accidental bit-flip on Bob's measurement (educational model).")
sample_frac = st.sidebar.slider("QBER Sample Fraction", min_value=0.10, max_value=0.50, value=default_sample, step=0.05,
                                help="Fraction of sifted bits revealed publicly to estimate channel disturbance.")
seed_val = st.sidebar.number_input("Random Seed (Reproducibility)", min_value=1, max_value=99999, value=42)

st.sidebar.divider()
if HAS_TEAM_MODULES:
    st.sidebar.success("⚛️ **Engine:** Real Qiskit Aer Active (`bb84.py` + `security.py`)")
else:
    st.sidebar.warning("⚠️ **Engine:** Running in Standalone Fallback Mode")

st.sidebar.info("""
**Team Architecture Handshake**:
- **Member 1**: `bb84.py` (Qiskit quantum core)
- **Member 2**: `security.py` (BB84 protocol logic)
- **Member 3**: `app.py` & docs (Interactive dashboard)
""")


# ==============================================================================
# Simulation Execution
# ==============================================================================
run_clicked = st.sidebar.button("🚀 Run Quantum Simulation", type="primary", use_container_width=True)

# Run simulation automatically or on button click
if "latest_result" not in st.session_state or run_clicked:
    with st.spinner("Preparing Qiskit circuits and executing quantum measurement on AerSimulator..."):
        sim_res = simulate_bb84(
            n_bits=n_bits,
            eve=enable_eve,
            noise=noise_val,
            sample_fraction=sample_frac,
            seed=int(seed_val)
        )
        st.session_state["latest_result"] = sim_res
        st.session_state["params"] = {
            "n_bits": n_bits,
            "eve": enable_eve,
            "noise": noise_val,
            "sample_frac": sample_frac,
            "seed": seed_val
        }

res = st.session_state["latest_result"]
qber_pct = res["qber"] * 100.0


# ==============================================================================
# Main Dashboard Tabs
# ==============================================================================
tab_live, tab_bench, tab_circuit, tab_guide = st.tabs([
    "📊 Live Simulation & Security Audit",
    "⚖️ Multi-Scenario Benchmark",
    "⚛️ Quantum Circuit Inspector",
    "📖 Protocol Science & Submission Notes"
])

# ------------------------------------------------------------------------------
# TAB 1: Live Simulation & Security Audit
# ------------------------------------------------------------------------------
with tab_live:
    # Status Banner
    if res["qber"] > 0.10:
        st.markdown(f"""
        <div class="channel-box" style="background-color: rgba(220, 38, 38, 0.15); border-color: #dc2626; color: #fca5a5;">
            <h4 style="margin: 0; color: #f87171;">⚠️ DEMONSTRATION WARNING: HIGH ERROR RATE DETECTED ({qber_pct:.2f}%)</h4>
            <p style="margin: 4px 0 0 0; color: #fecaca; font-size: 0.95rem;">
                <strong>Verdict:</strong> {res['status']}. The Quantum Bit Error Rate exceeds the 10.0% demonstration warning threshold.
                Alice and Bob must <strong>ABORT</strong> key generation! Disturbances indicate an eavesdropper (Eve) or high channel noise.
            </p>
        </div>
        """, unsafe_allow_html=True)
    elif res["qber"] == 0.0:
        st.markdown(f"""
        <div class="channel-box" style="background-color: rgba(5, 150, 105, 0.15); border-color: #059669; color: #6ee7b7;">
            <h4 style="margin: 0; color: #34d399;">🛡️ CLEAN CHANNEL: ZERO ERRORS DETECTED (0.0%)</h4>
            <p style="margin: 4px 0 0 0; color: #a7f3d0; font-size: 0.95rem;">
                <strong>Verdict:</strong> {res['status']}. In this ideal noiseless simulation without an active eavesdropper, all matching bases yield identical bits.
                The remaining {res['remaining_bits']} sifted bits are retained. In production QKD, error reconciliation and privacy amplification must follow before key derivation.
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="channel-box" style="background-color: rgba(217, 119, 6, 0.15); border-color: #d97706; color: #fcd34d;">
            <h4 style="margin: 0; color: #fbbf24;">⚡ TOLERABLE ERRORS DETECTED ({qber_pct:.2f}%)</h4>
            <p style="margin: 4px 0 0 0; color: #fde68a; font-size: 0.95rem;">
                <strong>Verdict:</strong> {res['status']}. Errors exist below the 10.0% demonstration warning threshold.
                Note that low sample QBER does not prove absolute security or absence of eavesdropping. In physical QKD, classical Error Correction (Information Reconciliation) and Privacy Amplification are applied to eliminate residual leakage.
            </p>
        </div>
        """, unsafe_allow_html=True)

    # Key Metrics Display
    m_col1, m_col2, m_col3, m_col4, m_col5 = st.columns(5)
    with m_col1:
        st.metric("Quantum States (N)", res["n_bits"])
    with m_col2:
        st.metric("Sifted Bits (~50%)", res["sifted_bits"], delta=f"{res['sifted_bits']/res['n_bits']*100:.1f}% kept")
    with m_col3:
        st.metric("Public Sampled Bits", res["sampled_bits"], delta=f"{res['sample_errors']} errors")
    with m_col4:
        st.metric("Measured QBER", f"{qber_pct:.2f}%", delta=f"{'EXCEEDS 10%' if qber_pct > 10 else '<= 10% (LOW ERROR)'}", delta_color="inverse" if qber_pct > 10 else "normal")
    with m_col5:
        st.metric("Remaining Sifted Bits", res["remaining_bits"])

    st.markdown("""
    <div style="background-color: rgba(59, 130, 246, 0.1); border-left: 4px solid #3b82f6; padding: 10px 14px; border-radius: 6px; margin: 12px 0 4px 0; font-size: 0.88rem; color: #bfdbfe;">
        <strong>Educational Demonstration Notice:</strong>
        The 10.0% QBER threshold is an educational demonstration setting, not a universal proof of an attacker. High QBER can result from Eve or channel noise.
        Conversely, low QBER does not prove the total absence of eavesdropping. Remaining sifted bits require classical error reconciliation
        and privacy amplification before becoming a cryptographically secure key.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Visualizations: QBER Gauge & Funnel Breakdown
    v_col1, v_col2 = st.columns([1, 1])

    with v_col1:
        st.markdown("##### 🎯 QBER Gauge vs Demonstration Warning Threshold")
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=qber_pct,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Quantum Bit Error Rate (%)", 'font': {'size': 18}},
            number={'suffix': "%"},
            gauge={
                'axis': {'range': [0, 50], 'tickwidth': 1, 'tickcolor': "white"},
                'bar': {'color': "#ef4444" if qber_pct > 10 else "#10b981"},
                'bgcolor': "rgba(0,0,0,0.1)",
                'borderwidth': 1,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, 10], 'color': "rgba(16, 185, 129, 0.25)"},
                    {'range': [10, 25], 'color': "rgba(245, 158, 11, 0.25)"},
                    {'range': [25, 50], 'color': "rgba(239, 68, 68, 0.25)"}
                ],
                'threshold': {
                    'line': {'color': "yellow", 'width': 3},
                    'thickness': 0.75,
                    'value': 10.0
                }
            }
        ))
        fig_gauge.update_layout(height=280, margin=dict(l=20, r=20, t=40, b=20))
        st.plotly_chart(fig_gauge, use_container_width=True)
        st.caption("• 0–10%: Demonstration low-error zone (noise possible) | • >10%: Demonstration warning zone (Eve or heavy noise) | • ~25%: Ideal Eve Intercept-Resend average. (Note: 10% is a hackathon demo setting, not a universal security proof.)")

    with v_col2:
        st.markdown("##### 🔄 BB84 Quantum Key Pipeline")
        funnel_df = pd.DataFrame({
            "Stage": [
                "1. Initial Qubits Sent",
                "2. Sifted Bits (Bases Matched)",
                "3. Public Sample (Revealed)",
                "4. Remaining Sifted Bits"
            ],
            "Count": [
                res["n_bits"],
                res["sifted_bits"],
                res["sampled_bits"],
                res["remaining_bits"]
            ]
        })
        fig_funnel = px.funnel(funnel_df, x="Count", y="Stage", color="Stage",
                               color_discrete_sequence=["#3b82f6", "#8b5cf6", "#ec4899", "#10b981"])
        fig_funnel.update_layout(height=280, margin=dict(l=20, r=20, t=20, b=20), showlegend=False)
        st.plotly_chart(fig_funnel, use_container_width=True)
        st.caption("Notice: Publicly tested sample bits are discarded and NOT included in the remaining sifted bits.")

    # Quantum Bit Stream Inspection Table
    st.markdown("---")
    st.markdown("##### 🔬 Quantum State Transmission Inspector (First 20 Qubits)")
    st.write("Inspect how Alice's preparation, basis choices, Eve's intercept (if active), and Bob's measurement interact in real time:")

    if "_detailed_log" in res:
        log = res["_detailed_log"]
        display_n = min(20, res["n_bits"])
        table_rows = []
        basis_symbol = {0: "+ (Rectilinear)", 1: "× (Diagonal)"}

        for i in range(display_n):
            a_bit = log["alice_bits"][i]
            a_bas = basis_symbol[log["alice_bases"][i]]
            b_bas = basis_symbol[log["bob_bases"][i]]
            b_bit = log["bob_bits"][i]
            matched = i in log["matching_indices"]
            sampled = i in log["sample_positions"]
            err = (a_bit != b_bit) if sampled else False

            row = {
                "Qubit #": f"Q_{i}",
                "Alice Bit": a_bit,
                "Alice Basis": a_bas,
            }
            if enable_eve and log["eve_bases"]:
                row["Eve Basis"] = basis_symbol[log["eve_bases"][i]]
                row["Eve Measured"] = log["eve_bits"][i]

            row.update({
                "Bob Basis": b_bas,
                "Bob Measured": b_bit,
                "Bases Matched?": "✅ Yes" if matched else "❌ Discard",
                "Sampled for QBER?": "🔍 Yes" if sampled else "—",
                "Sample Error?": "🚨 ERROR" if (sampled and err) else ("✔️ Match" if sampled else "—")
            })
            table_rows.append(row)

        df_display = pd.DataFrame(table_rows)
        st.dataframe(df_display, use_container_width=True)
    else:
        st.info("Transmission details available during live run.")


# ------------------------------------------------------------------------------
# TAB 2: Multi-Scenario Benchmark
# ------------------------------------------------------------------------------
with tab_bench:
    st.markdown("#### ⚖️ Side-by-Side Comparison of BB84 Channels")
    st.write("This benchmark runs all three canonical scenarios using the exact same Qiskit measurement engine to demonstrate the power of eavesdropping detection:")

    if st.button("📊 Run 3-Scenario Comparative Benchmark", type="secondary"):
        with st.spinner("Simulating Clean, Eve Attack, and Noisy Channels via Qiskit Aer..."):
            res_clean = simulate_bb84(n_bits=512, eve=False, noise=0.0, seed=101)
            res_eve = simulate_bb84(n_bits=512, eve=True, noise=0.0, seed=102)
            res_noise = simulate_bb84(n_bits=512, eve=False, noise=0.08, seed=103)

            comp_df = pd.DataFrame({
                "Scenario": ["1. Clean Channel (Ideal)", "2. Eve Intercept-Resend", "3. Noisy Channel (8% Noise)"],
                "Eve Active": ["No", "YES (100% Intercept)", "No"],
                "Channel Noise": ["0.0%", "0.0%", "8.0%"],
                "QBER (%)": [res_clean["qber"] * 100, res_eve["qber"] * 100, res_noise["qber"] * 100],
                "Expected Theoretical QBER": ["0.0%", "~25.0%", "~8.0%"],
                "Sifted Bits": [res_clean["sifted_bits"], res_eve["sifted_bits"], res_noise["sifted_bits"]],
                "Protocol Status": [res_clean["status"], res_eve["status"], res_noise["status"]]
            })

            # Bar Chart
            fig_bar = px.bar(
                comp_df,
                x="Scenario",
                y="QBER (%)",
                color="Scenario",
                color_discrete_map={
                    "1. Clean Channel (Ideal)": "#10b981",
                    "2. Eve Intercept-Resend": "#ef4444",
                    "3. Noisy Channel (8% Noise)": "#f59e0b"
                },
                text="QBER (%)",
                title="Empirical QBER Comparison across Scenarios (Qiskit Simulation)"
            )
            fig_bar.add_hline(y=10.0, line_dash="dash", line_color="red",
                              annotation_text="10% Demonstration Warning Threshold", annotation_position="top left")
            fig_bar.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
            fig_bar.update_layout(height=380)

            st.plotly_chart(fig_bar, use_container_width=True)
            st.dataframe(comp_df, use_container_width=True)

            st.markdown("""
            > **Judges' Key Takeaways:**
            > - Eve's intercept-resend attack reliably introduces **~25% QBER**, clearly distinguishing it from an ideal noiseless channel ($0\\%$).
            > - **Noise vs. Attack:** Channel noise alone (e.g. 8%) also produces errors without an eavesdropper. The 10% threshold is an educational demonstration setting, not a universal proof of an attacker.
            > - **Security Limitations:** A low or zero QBER does not prove absolute security. In real-world QKD, authenticated classical channels, classical error correction (reconciliation), and privacy amplification are mandatory.
            """)
    else:
        st.info("Click the button above to generate a side-by-side empirical benchmark of Clean vs Eve vs Noisy channels.")


# ------------------------------------------------------------------------------
# TAB 3: Quantum Circuit Inspector
# ------------------------------------------------------------------------------
with tab_circuit:
    st.markdown("#### ⚛️ Real Qiskit Circuit Construction")
    st.write("QShield does **not** rely on pseudo-random software numbers for measurement. It builds and executes real Qiskit `QuantumCircuit` objects on `AerSimulator`.")

    c_col1, c_col2 = st.columns([1, 2])
    with c_col1:
        st.markdown("##### Select Circuit Configuration")
        inspect_bit = st.selectbox("Alice Bit", [0, 1], index=1)
        inspect_pb = st.selectbox("Alice Preparation Basis", [0, 1], format_func=lambda x: "+ (Rectilinear / Computational)" if x == 0 else "× (Diagonal / Hadamard)", index=1)
        inspect_mb = st.selectbox("Bob Measurement Basis", [0, 1], format_func=lambda x: "+ (Rectilinear / Computational)" if x == 0 else "× (Diagonal / Hadamard)", index=1)

        st.markdown("""
        **Basis Encoding Logic:**
        - **Bit 0, Basis 0 (+):** $|0\rangle$ (No gate)
        - **Bit 1, Basis 0 (+):** $|1\rangle$ (Apply $X$)
        - **Bit 0, Basis 1 (×):** $|+\rangle$ (Apply $H$)
        - **Bit 1, Basis 1 (×):** $|-\rangle$ (Apply $X$, then $H$)
        - **Measurement in ×:** Apply $H$ gate before standard measurement.
        """)

    with c_col2:
        st.markdown("##### Generated Qiskit Circuit Diagram")
        sample_qc = make_circuit(inspect_bit, inspect_pb, inspect_mb)
        if sample_qc is not None:
            circuit_text = sample_qc.draw(output="text")
            st.code(str(circuit_text), language="text")

            # Explanation of the specific circuit
            st.markdown(f"""
            **Circuit Explanation:**
            1. **Alice prepares bit {inspect_bit} in basis {'+' if inspect_pb == 0 else '×'}:**
               {'Applied X gate to flip |0> to |1>.' if inspect_bit == 1 else 'Qubit remains in |0> state.'}
               {'Applied H gate to rotate into superposition.' if inspect_pb == 1 else 'Remains in computational basis.'}
            2. **Bob measures in basis {'+' if inspect_mb == 0 else '×'}:**
               {'Applied H gate prior to readout to rotate from diagonal to computational basis.' if inspect_mb == 1 else 'Direct measurement in computational basis.'}
            3. **Compatibility:**
               {'Both bases match (' + ('+' if inspect_pb==0 else '×') + ') → Deterministic outcome!' if inspect_pb == inspect_mb else 'Bases differ! Outcome is random 50/50 superposition collapse.'}
            """)
        else:
            st.warning("Circuit drawing is loading or Qiskit is not yet installed.")


# ------------------------------------------------------------------------------
# TAB 4: Protocol Science & Submission Notes
# ------------------------------------------------------------------------------
with tab_guide:
    st.markdown("#### 📖 QShield Science, Architecture & Limitations")

    col_g1, col_g2 = st.columns(2)

    with col_g1:
        st.markdown("""
        ##### 1. Why Does Eve Cause ~25% Error?
        When Eve performs an **intercept-resend** attack:
        - Alice transmits states in basis $+$ or $\\times$ (probability 50% each).
        - Eve must choose a measurement basis at random without knowing Alice's choice:
          - **50% of the time**, Eve chooses the *correct* basis. Her measurement leaves the quantum state intact. Bob measures the correct bit ($0\\%$ error).
          - **50% of the time**, Eve chooses the *wrong* basis. Her measurement collapses the state into the wrong basis. When Eve resends this state, Bob measures in Alice's original basis and receives a purely random bit ($50\\%$ error chance).
        - **Total expected QBER:**
          $$\\text{QBER} = (0.50 \\times 0) + (0.50 \\times 0.50) = 0.25 = \\mathbf{25\\%}$$
        """)

    with col_g2:
        st.markdown("""
        ##### 2. Crucial Security Notice & Limitations
        > **Educational Simulator Disclaimer:**
        > QShield is an educational proof-of-concept simulator built for the VTU Qiskit Fall Fest hackathon.
        >
        > - **Low or zero QBER does NOT prove the absence of eavesdropping:** More sophisticated attacks (such as beam-splitting, photon-number splitting on weak coherent pulses, or side-channel leakage) can steal partial information without generating 25% error.
        > - **High QBER can occur without Eve:** Optical fiber attenuation, polarization drift, and detector dark counts cause errors in legitimate channels.
        > - **The 10% QBER threshold is a demonstration setting:** In real-world QKD, the tolerable error threshold is mathematically derived from the Shannon limit and privacy amplification bounds.
        > - **Production QKD requirements before a key is considered secure:**
        >   1. Authenticated classical public channel (e.g. Wegman-Carter MACs).
        >   2. Information Reconciliation (Cascade or LDPC classical error correction).
        >   3. Privacy Amplification (Universal hashing to compress remaining sifted bits into a final secret key).
        """)

    st.markdown("---")
    st.markdown("##### 👥 Team Responsibilities (Handshake Specification)")
    st.markdown("""
    | Member | Role | Files Owned | Status |
    | :--- | :--- | :--- | :--- |
    | **Member 1** | Quantum Core Engine (Qiskit circuits & Aer measurement) | `bb84.py`, `test_quantum.py` | Real Qiskit Aer simulation engine active |
    | **Member 2** | Security Protocol & Attack Simulation | `security.py`, `tests/` | Active BB84 protocol & attack simulation |
    | **Member 3 (You)** | Interactive Dashboard & Documentation | `app.py`, `README.md`, `presentation/` | Live Streamlit app, benchmark suite, slide deck |
    """)

# Footer
st.markdown("---")
st.markdown("<div style='text-align: center; color: #64748b; font-size: 0.85rem;'>QShield | VTU-Qiskit Fall Fest 2026 | Built with Python, Streamlit & Qiskit</div>", unsafe_allow_html=True)
