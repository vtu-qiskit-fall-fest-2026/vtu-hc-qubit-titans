"""
QShield - Security & BB84 Protocol Module (Member 2).
VTU-QFF Hackathon 2026 | Team: Qubit Titans (VTU-QFF-HC-0104)

Responsibilities (Member 2):
- BB84 protocol simulation (simulate_bb84)
- Basis sifting and reconciliation (sift_bases)
- Eavesdropper (Eve) Intercept-and-Resend attack simulation
- Channel noise perturbation model
- Quantum Bit Error Rate (QBER) calculation and audit trail (calculate_qber)
- Input validation and security threshold evaluation

Educational Notice & Physical Security Limitations:
- The 10.0% QBER warning threshold is a demonstration setting, not proof of an attacker.
  Disturbances can originate from Eve, environmental thermal noise, or detector dark counts.
  Conversely, a low sample QBER does not guarantee absolute physical security.
- The `remaining_bits` value represents the count of sifted bits that were not publicly
  sacrificed during the QBER sampling phase. It does NOT constitute a final cryptographically
  secure symmetric key; in production QKD, classical Information Reconciliation (error correction)
  and Privacy Amplification (universal hashing) must be applied.
"""

from __future__ import annotations

import random
from typing import Any, Callable, Dict, List, Optional, Set

# Attempt to import Member 1's Qiskit quantum measurement backend.
# If bb84.py has not yet been merged or created, measure_qubits is set to None.
# simulate_bb84() will raise an informative RuntimeError if invoked without an
# available quantum backend or injected test function.
try:
  from bb84 import measure_qubits
except ImportError:
  measure_qubits = None


def sift_bases(alice_bases: List[int], bob_bases: List[int]) -> List[int]:
  """Identify indices where Alice and Bob selected matching measurement bases.

  In the BB84 protocol, Alice and Bob publicly announce their basis choices
  (without revealing the bit values) over an authenticated classical channel.
  Only transmission events where both parties selected the same basis are kept.

  Parameters
  ----------
  alice_bases : list of int
      Basis choices used by Alice (0 = rectilinear '+', 1 = diagonal '×').
  bob_bases : list of int
      Basis choices used by Bob (0 = rectilinear '+', 1 = diagonal '×').

  Returns
  -------
  list of int
      Sorted list of index positions where alice_bases[i] == bob_bases[i].
  """
  if len(alice_bases) != len(bob_bases):
    raise ValueError("Alice and Bob bases lists must have identical lengths")
  return [i for i, (a, b) in enumerate(zip(alice_bases, bob_bases)) if a == b]


def calculate_qber(
    alice_bits: List[int], bob_bits: List[int], sample_indices: List[int]
) -> float:
  """Calculate the Quantum Bit Error Rate (QBER) over a public sample of sifted bits.

  Parameters
  ----------
  alice_bits : list of int
      Bit values prepared by Alice.
  bob_bits : list of int
      Bit values measured by Bob.
  sample_indices : list of int
      Indices of sifted bits publicly compared to estimate channel disturbance.

  Returns
  -------
  float
      QBER fraction between 0.0 and 1.0. Returns 0.0 if sample_indices is empty.
  """
  if not sample_indices:
    return 0.0
  errors = sum(1 for idx in sample_indices if alice_bits[idx] != bob_bits[idx])
  return float(errors / len(sample_indices))


def simulate_bb84(
    n_bits: int = 512,
    eve: bool = False,
    noise: float = 0.0,
    sample_fraction: float = 0.25,
    seed: Optional[int] = 42,
    measure_func: Optional[Callable[..., List[int]]] = None,
) -> Dict[str, Any]:
  """Simulate the Bennett-Brassard 1984 (BB84) Quantum Key Distribution protocol.

  Coordinates Alice's state preparation, optional Eve intercept-and-resend
  interception, Bob's measurement, basis sifting, public error sampling,
  and QBER evaluation.

  Parameters
  ----------
  n_bits : int, default=512
      Number of initial quantum states (qubits) Alice transmits. Must be >= 8.
  eve : bool, default=False
      If True, simulates Eve executing an Intercept-and-Resend attack:
      1. Eve intercepts flying qubits and measures them in random bases.
      2. Eve prepares new qubits in her measurement bases and resends them to
      Bob.
      Requires two actual calls to the quantum measurement engine.
  noise : float, default=0.0
      Probability of independent output bit-flip noise on Bob's measured bits
      (0.0 <= noise <= 1.0), modeling detector dark counts or fiber
      depolarization.
  sample_fraction : float, default=0.25
      Fraction of sifted bits randomly sampled and publicly sacrificed to
      estimate
      the Quantum Bit Error Rate (0.0 < sample_fraction <= 1.0).
  seed : int or None, default=42
      RNG seed for deterministic reproducibility across simulation stages.
  measure_func : callable, optional
      Custom quantum measurement function for dependency injection or testing.
      Signature: measure_func(bits, prep_bases, measure_bases, seed=None) ->
      list[int].
      Defaults to Member 1's `bb84.measure_qubits`.

  Returns
  -------
  dict
      Contract-compliant simulation dictionary:
      - "n_bits": int, total initial qubits transmitted.
      - "sifted_bits": int, count of qubits where Alice and Bob bases matched.
      - "sampled_bits": int, count of sifted bits revealed publicly for QBER
      audit.
      - "sample_errors": int, number of bit mismatches observed in the public
      sample.
      - "qber": float, sample error rate (sample_errors / sampled_bits).
      - "remaining_bits": int, count of unsampled sifted bits remaining
      (sifted - sampled).
      - "status": str, "No high error detected" or "High errors: attack OR noise
      possible".
      - "_detailed_log": dict, optional educational inspection metadata.

  Raises
  ------
  ValueError
      If n_bits < 8, noise is not in [0.0, 1.0], or sample_fraction is not in
      (0.0, 1.0].
  RuntimeError
      If Member 1's quantum backend is missing and no `measure_func` is
      injected.
  """
  # 1. Parameter Validation
  if not isinstance(n_bits, int) or isinstance(n_bits, bool) or n_bits < 8:
    raise ValueError("n_bits must be an integer >= 8")
  if not isinstance(noise, (int, float)) or not (0.0 <= noise <= 1.0):
    raise ValueError("noise must be between 0.0 and 1.0")
  if not isinstance(sample_fraction, (int, float)) or not (
      0.0 < sample_fraction <= 1.0
  ):
    raise ValueError("sample_fraction must be in (0.0, 1.0]")

  # 2. Resolve Quantum Measurement Backend
  active_measure = measure_func if measure_func is not None else measure_qubits
  if active_measure is None:
    raise RuntimeError(
        "Quantum measurement backend unavailable: Member 1's 'bb84.py' "
        "(providing 'measure_qubits') could not be imported. Please ensure "
        "'bb84.py' is present in the workspace or inject a 'measure_func' for"
        " testing."
    )

  # 3. Random Generation for Alice and Bob
  rng = random.Random(seed)
  alice_bits = [rng.randrange(2) for _ in range(n_bits)]
  alice_bases = [rng.randrange(2) for _ in range(n_bits)]
  bob_bases = [rng.randrange(2) for _ in range(n_bits)]

  eve_bases = None
  eve_bits = None

  # 4. Quantum Transmission & Eve Attack Handling
  if not eve:
    # Path A: Clean quantum transmission directly from Alice to Bob
    # Single call to quantum measurement backend
    bob_raw = active_measure(
        alice_bits,
        alice_bases,
        bob_bases,
        seed=seed + 1 if seed is not None else None,
    )
    bob_bits = list(bob_raw)
  else:
    # Path B: Eve Intercept-and-Resend Attack
    # Requires two actual, independent calls to measure_qubits:
    # Step 1: Eve intercepts flying qubits and measures them in random bases
    eve_bases = [rng.randrange(2) for _ in range(n_bits)]
    eve_raw = active_measure(
        alice_bits,
        alice_bases,
        eve_bases,
        seed=seed + 2 if seed is not None else None,
    )
    eve_bits = list(eve_raw)

    # Step 2: Eve prepares new qubits in her bases and resends them to Bob
    bob_raw = active_measure(
        eve_bits,
        eve_bases,
        bob_bases,
        seed=seed + 3 if seed is not None else None,
    )
    bob_bits = list(bob_raw)

  # 5. Independent Output-Bit-Flip Noise Model (before classical basis announcement)
  if noise > 0.0:
    for i in range(len(bob_bits)):
      if rng.random() < noise:
        bob_bits[i] ^= 1

  # 6. Public Basis Sifting
  matching_indices = sift_bases(alice_bases, bob_bases)
  sifted_bits_count = len(matching_indices)

  # 7. Public Sampling for Error Detection (QBER)
  sample_count = (
      max(1, int(sifted_bits_count * sample_fraction))
      if sifted_bits_count > 0
      else 0
  )
  if sifted_bits_count > 0:
    sample_positions = rng.sample(matching_indices, sample_count)
    sample_errors = sum(
        1 for idx in sample_positions if alice_bits[idx] != bob_bits[idx]
    )
    qber = float(sample_errors / sample_count)
  else:
    sample_positions = []
    sample_errors = 0
    qber = 0.0

  # 8. Key Material Conservation
  # Sampled bits are publicly revealed and MUST be removed from remaining key material
  remaining_bits_count = max(0, sifted_bits_count - sample_count)

  # 9. Educational Security Threshold Evaluation
  # Warning threshold at 10.0% QBER (demonstration threshold for hackathon)
  if qber > 0.10:
    status = "High errors: attack OR noise possible"
  else:
    status = "No high error detected"

  # 10. Educational Audit Trail for Dashboard
  detailed_log = {
      "alice_bits": alice_bits,
      "alice_bases": alice_bases,
      "bob_bases": bob_bases,
      "bob_bits": bob_bits,
      "eve_bases": eve_bases,
      "eve_bits": eve_bits,
      "matching_indices": set(matching_indices),
      "sample_positions": (
          set(sample_positions) if sifted_bits_count > 0 else set()
      ),
      "educational_notice": (
          "Educational simulation data. The remaining bits count is not a"
          " cryptographically secure key without classical error correction"
          " and privacy amplification."
      ),
  }

  return {
      "n_bits": n_bits,
      "sifted_bits": sifted_bits_count,
      "sampled_bits": sample_count,
      "sample_errors": sample_errors,
      "qber": float(qber),
      "remaining_bits": remaining_bits_count,
      "status": status,
      "_detailed_log": detailed_log,
  }
