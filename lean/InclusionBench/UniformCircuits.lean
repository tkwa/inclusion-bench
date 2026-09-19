import InclusionBench.Circuits
import InclusionBench.Transducers

/-!
# Logspace-uniform NC

The generator is a concrete finite-control output transducer. It emits the
full gate list, not an unconstrained family label. Natural fields use unary
coding with a terminator; a gate contains a tag, a payload length, and its
payload. Circuit headers contain the input count, gate count, and output
index. Unary indices increase a polynomial-size encoding only polynomially.
-/

namespace InclusionBench.UniformCircuits

open Machines Circuits Transducers

def encodeNaturals : List Nat → Word
  | [] => []
  | number :: remaining => List.replicate number false ++ true :: encodeNaturals remaining

/-- The decoder may discard a malformed unterminated suffix. The encoder
never emits such a suffix, and its round trip is proved below. -/
def decodeNaturals : Word → List Nat
  | [] => []
  | true :: remaining => 0 :: decodeNaturals remaining
  | false :: remaining =>
      match decodeNaturals remaining with
      | [] => []
      | number :: rest => (number + 1) :: rest

theorem decode_unary_prefix (number : Nat) (suffix : Word) :
    decodeNaturals (List.replicate number false ++ true :: suffix) = number :: decodeNaturals suffix := by
  induction number with
  | zero => rfl
  | succ n ih => simp [List.replicate_succ, decodeNaturals, ih]

theorem decode_encode_naturals (numbers : List Nat) :
    decodeNaturals (encodeNaturals numbers) = numbers := by
  induction numbers with
  | nil => rfl
  | cons n remaining ih => simpa [encodeNaturals, decode_unary_prefix] using congrArg (n :: ·) ih

theorem encode_naturals_injective {left right : List Nat}
    (same : encodeNaturals left = encodeNaturals right) : left = right := by
  have decoded := congrArg decodeNaturals same
  simpa only [decode_encode_naturals] using decoded

/-- Tags distinguish every gate constructor. The second field is always the
number of payload fields, so successive gate records have unique boundaries. -/
def gateFields {n k : Nat} : Gate n k → List Nat
  | .input i => [0, 1, i.val]
  | .constant value => [1, 1, if value then 1 else 0]
  | .negation i => [2, 1, i.val]
  | .conjunction indices => 3 :: indices.length :: indices.map Fin.val
  | .disjunction indices => 4 :: indices.length :: indices.map Fin.val
  | .modulo modulus indices => 5 :: (indices.length + 1) :: modulus :: indices.map Fin.val
  | .majority indices => 6 :: indices.length :: indices.map Fin.val

def programFields {n k : Nat} : Program n k → List Nat
  | .empty => []
  | .append previous gate => programFields previous ++ gateFields gate

def serializeCircuit {n : Nat} (circuit : Circuit n) : Word :=
  encodeNaturals (n :: circuit.gates :: circuit.output.val :: programFields circuit.program)

/-- On every input of length n, the same concrete transducer outputs circuit
n. Space charges only the work tape, never the write-only output tape. -/
def logspaceUniform (family : Family) : Prop :=
  ∃ generator : Transducer, ∃ runtime : List Nat, ∃ coefficient : Nat,
    ∀ input : Word,
      generator.haltsAt input (Counting.polynomialValue runtime input.length) ∧
      generator.output input (Counting.polynomialValue runtime input.length) =
        serializeCircuit (family input.length) ∧
      (∀ time ≤ Counting.polynomialValue runtime input.length,
        (generator.after input time).workSpace ≤ coefficient * (Nat.log2 (input.length + 1) + 1))

def polylogarithmicDepth (family : Family) : Prop :=
  ∃ coefficient degree, ∀ n,
    (family n).depth ≤ coefficient * (Nat.log2 (n + 1) + 1) ^ degree

def NC : ComplexityClass :=
  fun L => ∃ family : Family,
    family.polynomialSize ∧ family.allowed .bounded ∧
    polylogarithmicDepth family ∧ logspaceUniform family ∧ family.decides L

theorem nc_in_polynomial_circuits : Includes NC polynomialCircuits := by
  intro L ⟨family, size, basis, _, _, correct⟩
  exact ⟨family, size, basis, correct⟩

end InclusionBench.UniformCircuits
