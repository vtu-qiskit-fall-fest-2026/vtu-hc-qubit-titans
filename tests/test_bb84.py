"""
Test suite for Member 1's Quantum Core module (bb84.py).
VTU-QFF Hackathon 2026 | Track 1: Quantum Cryptography & Security
Team: Qubit Titans (VTU-QFF-HC-0104)

Verifies:
1. Z-basis state preparation (|0> and |1>).
2. X-basis state preparation (|+> and |->).
3. Deterministic measurement on matched bases.
4. Probabilistic 50/50 measurement collapse on mismatched bases.
5. Input validation (lengths, values, empty sequences, types).
6. Output length, type, and order consistency.
7. Simulator seed reproducibility.
8. Circuit construction and textual drawing.
9. Medium-sized batch execution (>= 512 qubits).
10. Full end-to-end integration with Member 2's security.py.
"""

import pytest
from qiskit import QuantumCircuit
from bb84 import make_circuit, measure_qubits, get_simulator
from security import simulate_bb84


# ==============================================================================
# Test 1: Z-Basis State Preparation
# ==============================================================================
def test_z_basis_state_prep():
    """Verify state preparation in the Z (computational / rectilinear) basis."""
    # Bit 0, basis 0: |0> (No gate before measurement)
    qc0 = make_circuit(bit=0, prep_basis=0, measure_basis=0)
    op_names_0 = [inst.operation.name for inst in qc0.data]
    assert "x" not in op_names_0, "Bit 0 should not include an X gate"
    assert "measure" in op_names_0, "Circuit must include measurement"

    # Bit 1, basis 0: |1> (Pauli-X gate applied before measurement)
    qc1 = make_circuit(bit=1, prep_basis=0, measure_basis=0)
    op_names_1 = [inst.operation.name for inst in qc1.data]
    assert "x" in op_names_1, "Bit 1 in Z basis must apply an X gate to flip |0> to |1>"
    assert op_names_1.index("x") < op_names_1.index("measure")


# ==============================================================================
# Test 2: X-Basis State Preparation
# ==============================================================================
def test_x_basis_state_prep():
    """Verify state preparation in the X (diagonal) basis."""
    # Bit 0, basis 1: |+> (Hadamard gate applied to |0>)
    qc0 = make_circuit(bit=0, prep_basis=1, measure_basis=0)
    op_names_0 = [inst.operation.name for inst in qc0.data]
    assert "h" in op_names_0, "Bit 0 in X basis must apply an H gate to produce |+>"
    assert "x" not in op_names_0

    # Bit 1, basis 1: |-> (Pauli-X followed by Hadamard gate)
    qc1 = make_circuit(bit=1, prep_basis=1, measure_basis=0)
    op_names_1 = [inst.operation.name for inst in qc1.data]
    assert "x" in op_names_1 and "h" in op_names_1, "Bit 1 in X basis must apply X followed by H"
    assert op_names_1.index("x") < op_names_1.index("h"), "X must precede H to produce |->"


# ==============================================================================
# Test 3: Correct Measurement on Matched Bases
# ==============================================================================
def test_correct_measurement_matched_bases():
    """When Alice and Bob use matching bases, their bits must match deterministically."""
    bits = [0, 1, 0, 1, 1, 0, 0, 1]
    bases = [0, 0, 1, 1, 0, 1, 0, 1]

    measured = measure_qubits(bits, bases, bases, seed=42)
    assert measured == bits, f"Expected {bits}, but got {measured}"


# ==============================================================================
# Test 4: Mismatched Bases Produce Probabilistic 50/50 Collapse
# ==============================================================================
def test_mismatched_bases_probabilistic():
    """When preparation and measurement bases differ, outcome is random 50/50."""
    n = 1000
    # Alice sends all 0s in Z basis (0), Bob measures in X basis (1)
    bits = [0] * n
    prep_bases = [0] * n
    measure_bases = [1] * n

    measured = measure_qubits(bits, prep_bases, measure_bases, seed=12345)
    zeros = measured.count(0)
    ones = measured.count(1)

    assert zeros + ones == n
    # Expected: ~50% zeros (+- 7% statistical confidence bound for n=1000)
    assert 430 <= zeros <= 570, f"Expected ~500 zeros, got {zeros} zeros and {ones} ones"


# ==============================================================================
# Test 5: Input Validation & Error Handling
# ==============================================================================
def test_input_validation():
    """Verify input validation handles mismatched lengths, invalid values, and types."""
    # Mismatched lengths
    with pytest.raises(ValueError, match="Input sequence lengths must match"):
        measure_qubits([0, 1], [0], [0, 1])

    with pytest.raises(ValueError, match="Input sequence lengths must match"):
        measure_qubits([0, 1], [0, 1], [0])

    # Invalid bit values
    with pytest.raises(ValueError, match="Invalid bit"):
        measure_qubits([2], [0], [0])

    with pytest.raises(ValueError, match="Invalid bit"):
        make_circuit(bit=-1, prep_basis=0, measure_basis=0)

    # Invalid basis values
    with pytest.raises(ValueError, match="Invalid preparation basis"):
        measure_qubits([0], [2], [0])

    with pytest.raises(ValueError, match="Invalid measurement basis"):
        measure_qubits([0], [0], [3])

    # Non-integer / boolean validation (booleans rejected to prevent truthy pitfalls)
    with pytest.raises(ValueError):
        make_circuit(True, 0, 0)

    with pytest.raises(TypeError, match="must be lists or tuples"):
        measure_qubits("invalid", [0], [0])

    with pytest.raises(TypeError, match="Optional 'seed' must be an integer"):
        measure_qubits([0], [0], [0], seed="42")

    # Empty input sequence
    assert measure_qubits([], [], []) == []


# ==============================================================================
# Test 6: Output Consistency & Order Preservation
# ==============================================================================
def test_output_consistency():
    """Confirm output length, type, and transmission sequence preservation."""
    bits = [1, 0, 1, 1, 0, 0, 1, 0]
    prep = [0, 1, 0, 1, 0, 1, 0, 1]
    meas = [0, 1, 0, 1, 0, 1, 0, 1]

    results = measure_qubits(bits, prep, meas, seed=99)
    assert len(results) == len(bits)
    assert all(isinstance(r, int) and r in (0, 1) for r in results)
    assert results == bits


# ==============================================================================
# Test 7: Seed Reproducibility
# ==============================================================================
def test_seed_reproducibility():
    """Identical simulator seeds must yield identical measurement outcomes."""
    bits = [0] * 100
    prep_bases = [0] * 100
    measure_bases = [1] * 100  # Conjugate basis causes random collapse

    run1 = measure_qubits(bits, prep_bases, measure_bases, seed=7777)
    run2 = measure_qubits(bits, prep_bases, measure_bases, seed=7777)
    assert run1 == run2, "Seed reproducibility failed: simulator outputs differ for same seed"


# ==============================================================================
# Test 8: Quantum Circuit Object & Visual Diagram
# ==============================================================================
def test_circuit_diagram():
    """Verify that make_circuit creates a QuantumCircuit that renders properly."""
    qc = make_circuit(bit=1, prep_basis=1, measure_basis=1)
    assert isinstance(qc, QuantumCircuit)
    assert qc.num_qubits == 1
    assert qc.num_clbits == 1

    text_diag = str(qc.draw(output="text"))
    assert "X" in text_diag or "x" in text_diag
    assert "H" in text_diag or "h" in text_diag
    assert "M" in text_diag or "measure" in text_diag


# ==============================================================================
# Test 9: Medium-Sized Batched Simulation (>= 512 Qubits)
# ==============================================================================
def test_medium_sized_batches():
    """Verify that 512 single-qubit circuits execute efficiently and accurately in batch."""
    n = 512
    bits = [i % 2 for i in range(n)]
    bases = [(i // 2) % 2 for i in range(n)]

    measured = measure_qubits(bits, bases, bases, seed=42)
    assert len(measured) == n
    assert measured == bits


# ==============================================================================
# Test 10: Security Module Integration with Real Qiskit Backend
# ==============================================================================
def test_security_module_integration():
    """Verify full contract compatibility when security.py calls bb84.measure_qubits."""
    res = simulate_bb84(n_bits=256, eve=False, noise=0.0, sample_fraction=0.25, seed=42)

    required_keys = ["n_bits", "sifted_bits", "sampled_bits", "sample_errors", "qber", "remaining_bits", "status"]
    for key in required_keys:
        assert key in res, f"Missing required key {key} in simulation result"

    assert res["n_bits"] == 256
    assert res["qber"] == 0.0
    assert res["remaining_bits"] + res["sampled_bits"] == res["sifted_bits"]
    assert res["status"] == "No high error detected"


# ==============================================================================
# Extended Scenarios: Clean, Eve Attack, and Noisy Channels
# ==============================================================================
def test_scenario_clean_communication():
    """Scenario A: Clean noiseless communication must have QBER = 0.0%."""
    res = simulate_bb84(n_bits=512, eve=False, noise=0.0, seed=42)
    assert res["qber"] == 0.0
    assert res["sample_errors"] == 0
    # Sifting ratio should be approximately 50%
    assert 200 <= res["sifted_bits"] <= 312


def test_scenario_eve_intercept_resend():
    """Scenario B: Eve intercept-resend attack must produce elevated QBER converging to ~25%."""
    # 1. Verify individual runs show significant elevation (> 15%) and trigger warning status
    res = simulate_bb84(n_bits=512, eve=True, noise=0.0, seed=42)
    assert res["qber"] > 0.15
    assert "High errors" in res["status"]

    # 2. Test statistical convergence across sufficiently large sample runs
    qbers = []
    for s in range(1001, 1006):
        r = simulate_bb84(n_bits=1000, eve=True, noise=0.0, sample_fraction=0.5, seed=s)
        qbers.append(r["qber"])

    avg_qber = sum(qbers) / len(qbers)
    assert 0.20 <= avg_qber <= 0.30, f"Expected average QBER ~25%, got {avg_qber * 100:.2f}%"


def test_scenario_noise_without_eve():
    """Scenario C: 5% channel noise without Eve tends toward 5% QBER."""
    res = simulate_bb84(n_bits=1000, eve=False, noise=0.05, sample_fraction=0.5, seed=555)
    assert 0.02 <= res["qber"] <= 0.09, f"Expected QBER near 5%, got {res['qber'] * 100:.2f}%"


def test_scenario_eve_and_noise_combined():
    """Scenario D: Combined Eve and noise produces higher QBER than noise alone."""
    res_noise = simulate_bb84(n_bits=512, eve=False, noise=0.05, seed=42)
    res_both = simulate_bb84(n_bits=512, eve=True, noise=0.05, seed=42)
    assert res_both["qber"] > res_noise["qber"]
