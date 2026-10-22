"""
QShield - Quantum Key Distribution (BB84) Core Engine (Member 1).
VTU-QFF Hackathon 2026 | Track 1: Quantum Cryptography & Security
Team: Qubit Titans (VTU-QFF-HC-0104)

Responsibilities (Member 1):
- Construct single-qubit BB84 quantum circuits using IBM Qiskit.
- Encode classical bits into quantum states across Rectilinear (+) and Diagonal (×) bases.
- Implement basis rotations and projective measurement in the computational basis.
- Execute batched quantum circuit simulations using Qiskit Aer (AerSimulator).

Educational Physics Overview:
=============================
1. What is a Qubit?
   Unlike a classical bit that is strictly 0 or 1, a quantum bit (qubit) can exist
   in a linear superposition of both states: |psi> = alpha|0> + beta|1>, where
   |alpha|^2 and |beta|^2 are measurement probabilities summing to 1.

2. The Quantum Gates:
   - Pauli-X Gate (qc.x):
     The quantum bit-flip gate. Acts as a NOT operation:
     |0> -> |1>  and  |1> -> |0>.
   - Hadamard Gate (qc.h):
     Creates equal superpositions and transitions between conjugate bases:
     H|0> = |+> = (|0> + |1>) / sqrt(2)
     H|1> = |-> = (|0> - |1>) / sqrt(2)
     Applying H twice returns the state back to its original form (H * H = I).

3. The Four BB84 States:
   +----------------+-----------------+---------------+----------------------+
   | Classical Bit  | Basis Selection | Quantum State | Qiskit Gates Applied |
   +----------------+-----------------+---------------+----------------------+
   | 0              | 0 (Z / + basis) | |0>           | (No gate applied)    |
   | 1              | 0 (Z / + basis) | |1>           | X                    |
   | 0              | 1 (X / × basis) | |+>           | H                    |
   | 1              | 1 (X / × basis) | |->           | X followed by H      |
   +----------------+-----------------+---------------+----------------------+

4. Basis Measurement:
   Physical quantum hardware and Qiskit measure natively in the computational (Z) basis.
   To measure in the diagonal (×) basis, we apply a Hadamard (H) gate right before measurement:
   - H|+> rotates to |0>, yielding classical bit 0 deterministically.
   - H|-> rotates to |1>, yielding classical bit 1 deterministically.

5. Matched vs. Mismatched Bases:
   - When Alice's preparation basis matches Bob's measurement basis, Bob obtains
     Alice's bit with 100% deterministic fidelity in an ideal noiseless channel.
   - When their bases differ, Bob's measurement projects the qubit into an unbiased
     conjugate basis, causing wavefunction collapse with an equal 50/50 probability
     of yielding 0 or 1.
"""

from __future__ import annotations

from typing import List, Optional, Sequence
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

# Module-level default simulator instance for high-performance batched execution.
# Reusing this backend avoids the overhead of repeated C++ simulator initialization.
_DEFAULT_SIMULATOR: Optional[AerSimulator] = None


def get_simulator() -> AerSimulator:
    """Retrieve or initialize the shared Qiskit AerSimulator instance."""
    global _DEFAULT_SIMULATOR
    if _DEFAULT_SIMULATOR is None:
        _DEFAULT_SIMULATOR = AerSimulator()
    return _DEFAULT_SIMULATOR


def make_circuit(bit: int, prep_basis: int, measure_basis: int) -> QuantumCircuit:
    """
    Construct a single-qubit BB84 quantum circuit with state preparation and measurement.

    Parameters
    ----------
    bit : int
        Classical bit Alice wishes to transmit (must be 0 or 1).
    prep_basis : int
        Alice's preparation basis choice (0 = Rectilinear '+', 1 = Diagonal '×').
    measure_basis : int
        Bob's measurement basis choice (0 = Rectilinear '+', 1 = Diagonal '×').

    Returns
    -------
    QuantumCircuit
        A Qiskit QuantumCircuit with 1 qubit and 1 classical bit containing the
        appropriate preparation gates, basis rotation, and measurement operation.

    Raises
    ------
    ValueError
        If bit, prep_basis, or measure_basis are not 0 or 1.
    TypeError
        If inputs are not integers (rejecting booleans and non-integer types).
    """
    # Strict binary type and value validation
    if type(bit) is not int or bit not in (0, 1):
        raise ValueError(f"Invalid bit value: {bit!r}. Expected integer 0 or 1.")
    if type(prep_basis) is not int or prep_basis not in (0, 1):
        raise ValueError(f"Invalid preparation basis: {prep_basis!r}. Expected integer 0 (+) or 1 (×).")
    if type(measure_basis) is not int or measure_basis not in (0, 1):
        raise ValueError(f"Invalid measurement basis: {measure_basis!r}. Expected integer 0 (+) or 1 (×).")

    # Allocate 1 quantum bit and 1 classical bit for readout
    qc = QuantumCircuit(1, 1)

    # --------------------------------------------------------------------------
    # Step 1: Alice's State Preparation
    # --------------------------------------------------------------------------
    # For bit 1: Apply Pauli-X to flip |0> to |1>
    if bit == 1:
        qc.x(0)

    # For Diagonal (×) basis: Apply Hadamard to rotate into superposition
    # |0> -> |+>, and |1> -> |->
    if prep_basis == 1:
        qc.h(0)

    # --------------------------------------------------------------------------
    # Step 2: Bob's Measurement-Basis Transformation
    # --------------------------------------------------------------------------
    # Standard measurement occurs in the computational Z basis (|0>, |1>).
    # To measure in the diagonal X basis, apply H prior to readout:
    # |+> -> |0> (bit 0), and |-> -> |1> (bit 1).
    if measure_basis == 1:
        qc.h(0)

    # --------------------------------------------------------------------------
    # Step 3: Projective Measurement
    # --------------------------------------------------------------------------
    # Measure quantum bit 0 and record the classical outcome into classical bit 0
    qc.measure(0, 0)

    return qc


def measure_qubits(
    bits: Sequence[int],
    prep_bases: Sequence[int],
    measure_bases: Sequence[int],
    seed: Optional[int] = None
) -> List[int]:
    """
    Execute batched Qiskit Aer quantum simulations for a series of transmitted qubits.

    Parameters
    ----------
    bits : sequence of int
        List or tuple of classical bits prepared by the sender (0 or 1).
    prep_bases : sequence of int
        List or tuple of preparation basis selections (0 for '+', 1 for '×').
    measure_bases : sequence of int
        List or tuple of receiver measurement basis selections (0 for '+', 1 for '×').
    seed : int, optional
        RNG seed passed to AerSimulator for deterministic, reproducible measurement.

    Returns
    -------
    list of int
        List of single-shot classical measurement outcomes (0 or 1), preserving
        exact transmission order.

    Raises
    ------
    TypeError
        If inputs are not sequences or seed is not an integer.
    ValueError
        If sequence lengths do not match or any element is not a binary 0 or 1.
    """
    # 1. Type validation for sequences
    if not (isinstance(bits, (list, tuple)) and
            isinstance(prep_bases, (list, tuple)) and
            isinstance(measure_bases, (list, tuple))):
        raise TypeError("Input sequences 'bits', 'prep_bases', and 'measure_bases' must be lists or tuples.")

    # 2. Length equality check
    n = len(bits)
    if not (n == len(prep_bases) == len(measure_bases)):
        raise ValueError(
            f"Input sequence lengths must match: got bits={len(bits)}, "
            f"prep_bases={len(prep_bases)}, measure_bases={len(measure_bases)}."
        )

    # 3. Seed type validation
    if seed is not None and not isinstance(seed, int):
        raise TypeError(f"Optional 'seed' must be an integer, got {type(seed)}.")

    # 4. Handle empty sequence edge case
    if n == 0:
        return []

    # 5. Construct QuantumCircuits with per-element validation
    circuits: List[QuantumCircuit] = []
    for i, (b, pb, mb) in enumerate(zip(bits, prep_bases, measure_bases)):
        if type(b) is not int or b not in (0, 1):
            raise ValueError(f"Invalid bit at index {i}: {b!r}. Expected 0 or 1.")
        if type(pb) is not int or pb not in (0, 1):
            raise ValueError(f"Invalid preparation basis at index {i}: {pb!r}. Expected 0 or 1.")
        if type(mb) is not int or mb not in (0, 1):
            raise ValueError(f"Invalid measurement basis at index {i}: {mb!r}. Expected 0 or 1.")
        circuits.append(make_circuit(b, pb, mb))

    # 6. Execute batched single-shot simulation on AerSimulator
    simulator = get_simulator()
    run_kwargs = {"shots": 1}
    if seed is not None:
        run_kwargs["seed_simulator"] = seed

    job = simulator.run(circuits, **run_kwargs)
    result = job.result()

    # 7. Extract classical outcomes in original transmission sequence
    measured_bits: List[int] = []
    for i in range(n):
        counts = result.get_counts(i)
        measured_bit_str = next(iter(counts))
        measured_bits.append(int(measured_bit_str))

    return measured_bits
