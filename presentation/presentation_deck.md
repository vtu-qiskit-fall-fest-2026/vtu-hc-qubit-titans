# 🛡️ QShield: Presentation Deck Outline & Speaker Notes
**Hackathon:** Qiskit Fall Fest 2026 — VTU-QFF Hackathon  
**Track:** Track 1: Quantum Cryptography & Security  
**Team ID:** VTU-QFF-HC-0104  
**Team Name:** Qubit Titans  
**Project:** QShield — Quantum Key Distribution (BB84) & Eavesdropping Detection  

---

## 📋 Slide-by-Slide Deck Outline (Official 8-Slide Structure)

### Slide 1 — Title & Overview
- **Title:** QShield: Quantum Key Distribution & Eavesdropping Detection
- **Subtitle:** Harnessing Quantum Superposition & Qiskit Aer to Secure Classical Communications
- **Track:** Track 1: Quantum Cryptography & Security
- **Team ID:** VTU-QFF-HC-0104 | Team: Qubit Titans (Online Tier)
- **Members & Roles:**
  - **Member 1 (Quantum Lead):** Quantum Circuits & Aer Simulation (`bb84.py`, `test_quantum.py`)
  - **Member 2 (Security Lead):** BB84 Logic, Attack Vector & QBER (`security.py`, `tests/`)
  - **Member 3 (Dashboard & Presentation):** Interactive UI, Visuals & Documentation (`app.py`, `README.md`)
- **Key Badge:** Built with ⚛️ Qiskit 1.0+ / 2.0+ & Streamlit
- **Speaker Notes (0:00 - 0:25):**  
  *"Good day judges and fellow quantum enthusiasts. We are team Qubit Titans, presenting QShield — an interactive, Qiskit-powered learning simulator demonstrating Quantum Key Distribution and eavesdropping detection using the BB84 protocol."*

---

### Slide 2 — The Problem: The Post-Quantum Threat
- **Header:** The Vulnerability of Modern Key Exchange
- **Core Dilemma:**
  - Modern digital communication relies heavily on public-key cryptosystems (RSA, Diffie-Hellman, ECC).
  - These systems rely on computational hardness assumptions (integer factorization, discrete logarithms).
  - Shor's Algorithm running on future fault-tolerant quantum computers will render RSA/ECC obsolete.
  - Furthermore, adversaries today practice **"Harvest Now, Decrypt Later"** — intercepting and storing encrypted traffic to decrypt once quantum hardware arrives.
- **The Need:**
  - Symmetric encryption (like AES-256) remains quantum-resistant, BUT sharing the secret symmetric key over classical channels is fundamentally vulnerable.
- **Speaker Notes (0:25 - 0:55):**  
  *"Traditional encryption models assume adversaries possess limited computational power. With the imminent reality of quantum computers, Shor's algorithm will crack standard asymmetric key exchange. We need key distribution secured not by computational complexity, but by the immutable laws of quantum mechanics."*

---

### Slide 3 — Our Solution: BB84 Quantum Key Distribution
- **Header:** Information-Theoretic Security via Quantum Physics
- **The BB84 Mechanism:**
  1. **Preparation:** Alice generates random classical bits $\{0, 1\}$ and randomly chooses between two conjugate bases:
     - Rectilinear / Computational Basis ($+$): $\{|0\rangle, |1\rangle\}$
     - Diagonal / Hadamard Basis ($\times$): $\{|+\rangle, |-\rangle\}$
  2. **Quantum Transmission:** Alice sends single qubits across the quantum channel.
  3. **Measurement:** Bob randomly measures each qubit in either the $+$ or $\times$ basis.
  4. **Basis Sifting:** Alice and Bob publicly announce *only* the bases they used (never the bits). They retain bits where bases matched (~50%).
  5. **QBER & Eavesdropping Detection:** They publicly compare a random subset of sifted bits. If errors exceed a safety threshold, eavesdropping is detected!
- **Core Quantum Principles:**
  - **No-Cloning Theorem:** Eve cannot duplicate unknown quantum states without measurement.
  - **State Collapse / Measurement Disturbance:** Measuring an unknown quantum state irreversibly collapses it.
- **Speaker Notes (0:55 - 1:30):**  
  *"QShield implements the BB84 protocol. The magic lies in the No-Cloning Theorem. An eavesdropper cannot tap a quantum fiber silently. Any eavesdropping attempt collapses the quantum state, unavoidably introducing detectable noise called the Quantum Bit Error Rate (QBER)."*

---

### Slide 4 — Qiskit Implementation: The Quantum Circuit
- **Header:** Under the Hood: Real Qiskit Circuit Construction
- **Circuit Operations:**
  - State Preparation:
    - Bit 0 in Basis 0 ($+$): Ground state $|0\rangle$ (Identity)
    - Bit 1 in Basis 0 ($+$): State $|1\rangle$ ($\text{X}$ gate)
    - Bit 0 in Basis 1 ($\times$): State $|+\rangle$ ($\text{H}$ gate)
    - Bit 1 in Basis 1 ($\times$): State $|-\rangle$ ($\text{X}$ followed by $\text{H}$ gate)
  - Measurement:
    - In Basis 0 ($+$): Direct computational readout $\text{measure}(0, 0)$
    - In Basis 1 ($\times$): Apply $\text{H}$ gate prior to readout to rotate from diagonal to computational axis
- **Execution Engine:** Batched execution on `AerSimulator(shots=1)` with explicit simulation seeds.
- **Diagram:**
  ```text
       ┌───┐┌───┐┌───┐┌─┐
  q_0: ┤ X ├┤ H ├┤ H ├┤M├
       └───┘└───┘└───┘└╥┘
  c: 1/════════════════╩═
                       0 
  ```
- **Speaker Notes (1:30 - 2:05):**  
  *"Rather than relying on pseudo-random software approximations, QShield builds genuine Qiskit QuantumCircuits. For each qubit, we apply Pauli-X and Hadamard gates for Alice's encoding, followed by Bob's basis rotation and readout on Qiskit Aer's simulator."*

---

### Slide 5 — System Architecture & Modular Handshake
- **Header:** 3-Tier Layered Engineering Architecture
- **Architecture Diagram:**
  ```text
  ┌────────────────────────────────────────────────────────┐
  │                   app.py (Member 3)                    │
  │     Streamlit Dashboard • Visualizations • Metrics     │
  └───────────────────────────┬────────────────────────────┘
                              │ calls simulate_bb84()
                              ▼
  ┌────────────────────────────────────────────────────────┐
  │                 security.py (Member 2)                 │
  │   Alice/Bob RNG • Eve Attack • Sifting • QBER Audit    │
  └───────────────────────────┬────────────────────────────┘
                              │ calls measure_qubits()
                              ▼
  ┌────────────────────────────────────────────────────────┐
  │                  bb84.py (Member 1)                    │
  │     Qiskit Circuits • AerSimulator • Quantum Readout    │
  └────────────────────────────────────────────────────────┘
  ```
- **Contract Enforcement:**
  - `measure_qubits(bits, prep_bases, measure_bases, seed)` $\rightarrow$ returns raw measured bits from Aer.
  - `simulate_bb84(n_bits, eve, noise, sample_fraction, seed)` $\rightarrow$ returns standardized dictionary containing QBER, sifted bits, sample size, remaining key, and security status.
- **Speaker Notes (2:05 - 2:35):**  
  *"Our codebase is built on a clean team contract. Member 1 provides the core Qiskit measurement engine. Member 2 orchestrates the cryptographic logic and Eve's attack vector. Member 3 delivers the Streamlit dashboard, interactive charts, and documentation."*

---

### Slide 6 — Results: Empirical Verification
- **Header:** Empirical Testing & Theoretical Validation
- **Benchmark Comparison Table:**

| Scenario | Eve Intercept | Channel Noise | Empirical QBER | Theoretical Expectation | Security Verdict |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Clean Channel** | Disabled | 0.0% | **0.0%** | **0.0%** | ✅ Secure (Key Generated) |
| **Eve Active** | 100% Intercept | 0.0% | **~25.1%** | **25.0%** | 🚨 Compromised (Aborted) |
| **Noisy Channel** | Disabled | 8.0% | **~7.8%** | **8.0%** | ⚡ Marginal (Tolerable) |

- **Mathematical Proof of Eve's 25% Footprint:**
  - $P(\text{Eve picks same basis}) = 0.50 \implies \text{Error} = 0\%$
  - $P(\text{Eve picks wrong basis}) = 0.50 \implies \text{Bob measures randomly with } 50\% \text{ error}$
  - $\text{Total Expected QBER} = (0.50 \times 0) + (0.50 \times 0.50) = 0.25 = \mathbf{25\%}$
- **Speaker Notes (2:35 - 3:15):**  
  *"Here are our empirical results. In a clean channel, QBER is exactly 0.0%. When Eve launches an intercept-resend attack, the measured error jumps to approximately 25%, precisely matching our theoretical derivation. This clear gap allows Alice and Bob to distinguish eavesdropping from background noise."*

---

### Slide 7 — Live Demo & Critical Limitations
- **Header:** Live Dashboard & Honest Scientific Limitations
- **Features Demonstrated in App:**
  - Real-time QBER Gauge with 10% safety warning line.
  - Interactive Qubit Inspector showing step-by-step state collapse.
  - 1-Click scenario comparison across Clean, Attack, and Noise.
- **Essential Engineering Limitations:**
  - **Learning Simulator:** QShield is a conceptual educational demonstration, not a production optical cryptosystem.
  - **Noise vs. Attack:** A low QBER does not alone prove safety; channel eavesdroppers could perform partial beam-splitting.
  - **Production QKD Requirements:** Real-world QKD requires an authenticated classical channel (e.g. Wegman-Carter MACs), Cascade / LDPC Information Reconciliation, and Universal Hashing for Privacy Amplification.
- **Demo Link:** Available on YouTube *(link provided in submission portal)*.
- **Speaker Notes (3:15 - 3:45):**  
  *"Our Streamlit dashboard allows judges to test any combination of quantum states, attack modes, and noise levels. We also explicitly emphasize the honest limitations: in physical implementations, error correction and privacy amplification are mandatory to eliminate residual information leakage."*

---

### Slide 8 — Conclusion & Team Information
- **Header:** Summary & Team Qubit Titans
- **Core Takeaways:**
  1. Implemented real BB84 circuits and multi-basis measurement on Qiskit Aer.
  2. Demonstrated eavesdropping detection via QBER thresholding (~25% attack marker).
  3. Delivered an interactive, transparent Streamlit dashboard for exploration and defense.
- **Repository:** `vtu-qiskit-fall-fest-2026/vtu-hc-qubit-titans` (Assigned Private Repo)
- **Team Members:**
  - **Member 1 (Quantum Core):** Qiskit circuit modeling & execution
  - **Member 2 (Security):** BB84 attack models & QBER statistical tests
  - **Member 3 (Dashboard & Presentation):** Streamlit UI, visual analytics & documentation
- **Thank You & Questions!**
- **Speaker Notes (3:45 - 4:00):**  
  *"Thank you for your time. QShield demonstrates how the fundamental principles of quantum mechanics can be harnessed to secure our post-quantum future. We invite you to explore our repository and dashboard."*

---

## 🎬 3-Minute Demo Video Recording Script

### Setup Before Recording:
1. Terminal open with `python -m streamlit run app.py`.
2. Browser open at `http://localhost:8501`.
3. Screen recorder set to 1080p.

### Video Script Timeline:
- **0:00 - 0:30 (Introduction):**  
  Show Slide 1 / Dashboard Header. State team name (Qubit Titans, VTU-QFF-HC-0104) and problem statement (post-quantum key distribution threat).
- **0:30 - 1:00 (Clean Channel Run):**  
  Click "🟢 Clean Channel" preset. Hit "Run Quantum Simulation". Show QBER = 0.0%, status banner green ("CLEAN CHANNEL"), and explain basis matching (~50% sifted).
- **1:00 - 1:45 (Eve Intercept-Resend Attack):**  
  Click "🔴 Eve Intercept-Resend Attack" preset. Hit "Run Quantum Simulation". Point out how QBER jumps to ~25%, status banner turns red ("SECURITY WARNING"), and explain how state collapse alerts Alice and Bob.
- **1:45 - 2:15 (Circuit & Inspector):**  
  Switch to "⚛️ Quantum Circuit Inspector" tab. Show the actual Qiskit circuit with X, H, and measurement gates. Show the Quantum State Inspector table.
- **2:15 - 2:45 (Benchmark & Limitations):**  
  Switch to "⚖️ Multi-Scenario Benchmark" tab. Run the 3-scenario comparison. Highlight the honest limitations: difference between educational simulator and production QKD (need for authenticated channel, error correction, privacy amplification).
- **2:45 - 3:00 (Outro):**  
  Show GitHub repository link and thank the judges!
