import InclusionBench.Machines

/-!
# Concrete nonuniform Boolean circuits

`Program` is an acyclic sequence of gates. Every reference to an earlier gate
is a `Fin` index, preventing forward references and cycles by construction.
Families are explicitly nonuniform. A circuit's encoding size includes its
wires, including repetitions in unbounded fan-in gates.
-/

namespace InclusionBench.Circuits

inductive Gate (inputs previous : Nat) where
  | input (index : Fin inputs)
  | constant (value : Bool)
  | negation (index : Fin previous)
  | conjunction (indices : List (Fin previous))
  | disjunction (indices : List (Fin previous))
  | modulo (modulus : Nat) (indices : List (Fin previous))
  | majority (indices : List (Fin previous))

def Gate.eval {n k : Nat} (input : Fin n → Bool) (previous : Fin k → Bool) : Gate n k → Bool
  | .input i => input i
  | .constant b => b
  | .negation i => !(previous i)
  | .conjunction indices => indices.all previous
  | .disjunction indices => indices.any previous
  | .modulo modulus indices => decide (indices.countP previous % modulus = 0)
  | .majority indices => decide (indices.length ≤ 2 * indices.countP previous)

def Gate.references {n k : Nat} : Gate n k → List (Fin k)
  | .input _ | .constant _ => []
  | .negation i => [i]
  | .conjunction indices | .disjunction indices | .modulo _ indices | .majority indices => indices

def Gate.depth {n k : Nat} (previous : Fin k → Nat) (gate : Gate n k) : Nat :=
  match gate with
  | .input _ | .constant _ => 0
  | _ => 1 + (gate.references.map previous).foldl max 0

inductive Program (inputs : Nat) : Nat → Type where
  | empty : Program inputs 0
  | append {k : Nat} (previous : Program inputs k) (gate : Gate inputs k) : Program inputs (k + 1)

def Program.eval {n k : Nat} (program : Program n k) (input : Fin n → Bool) : Fin k → Bool :=
  match program with
  | .empty => Fin.elim0
  | .append previous gate => Fin.lastCases (gate.eval input (previous.eval input)) (previous.eval input)

def Program.depths {n k : Nat} (program : Program n k) : Fin k → Nat :=
  match program with
  | .empty => Fin.elim0
  | .append previous gate => Fin.lastCases (gate.depth previous.depths) previous.depths

def Program.encodingSize {n k : Nat} : Program n k → Nat
  | .empty => 0
  | .append previous gate => previous.encodingSize + gate.references.length + 1

inductive Basis where
  | bounded
  | unbounded
  | modulo (modulus : Nat)
  | threshold

def Gate.allowed {n k : Nat} (basis : Basis) : Gate n k → Prop
  | .input _ | .constant _ | .negation _ => True
  | .conjunction indices | .disjunction indices =>
      match basis with
      | .bounded => indices.length ≤ 2
      | _ => True
  | .modulo modulus _ =>
      match basis with
      | .modulo chosen => modulus = chosen ∧ 2 ≤ chosen
      | _ => False
  | .majority _ =>
      match basis with
      | .threshold => True
      | _ => False

def Program.allowed {n k : Nat} (basis : Basis) : Program n k → Prop
  | .empty => True
  | .append previous gate => previous.allowed basis ∧ gate.allowed basis

structure Circuit (inputs : Nat) where
  gates : Nat
  program : Program inputs gates
  output : Fin gates

def Circuit.eval {n : Nat} (circuit : Circuit n) (input : Fin n → Bool) : Bool :=
  circuit.program.eval input circuit.output

def Circuit.depth {n : Nat} (circuit : Circuit n) : Nat :=
  circuit.program.depths circuit.output

abbrev Family := (n : Nat) → Circuit n

def Family.decides (family : Family) (L : Language) : Prop :=
  ∀ word : Word, (family word.length).eval word.get = true ↔ L word

def Family.polynomialSize (family : Family) : Prop :=
  Machines.polynomialBound (fun n => (family n).program.encodingSize)

def Family.allowed (family : Family) (basis : Basis) : Prop :=
  ∀ n, (family n).program.allowed basis

def Family.constantDepth (family : Family) : Prop :=
  ∃ depth, ∀ n, (family n).depth ≤ depth

def Family.logarithmicDepth (family : Family) : Prop :=
  ∃ coefficient, ∀ n, (family n).depth ≤ coefficient * (Nat.log2 (n + 1) + 1)

/-- Polynomial-size nonuniform bounded-fan-in Boolean circuit families. -/
def polynomialCircuits : ComplexityClass :=
  fun L => ∃ family : Family,
    family.polynomialSize ∧ family.allowed .bounded ∧ family.decides L

def nonuniformNC1 : ComplexityClass :=
  fun L => ∃ family : Family,
    family.polynomialSize ∧ family.allowed .bounded ∧ family.logarithmicDepth ∧ family.decides L

def nonuniformAC0 : ComplexityClass :=
  fun L => ∃ family : Family,
    family.polynomialSize ∧ family.allowed .unbounded ∧ family.constantDepth ∧ family.decides L

def nonuniformACC0 : ComplexityClass :=
  fun L => ∃ modulus, 2 ≤ modulus ∧ ∃ family : Family,
    family.polynomialSize ∧ family.allowed (.modulo modulus) ∧ family.constantDepth ∧ family.decides L

def nonuniformTC0 : ComplexityClass :=
  fun L => ∃ family : Family,
    family.polynomialSize ∧ family.allowed .threshold ∧ family.constantDepth ∧ family.decides L

theorem nc1_in_polynomial_circuits : Includes nonuniformNC1 polynomialCircuits := by
  intro L ⟨family, size, basis, _, correct⟩
  exact ⟨family, size, basis, correct⟩

theorem unbounded_gate_allowed_modulo {n k : Nat} (gate : Gate n k)
    (modulus : Nat) (h : gate.allowed .unbounded) : gate.allowed (.modulo modulus) := by
  cases gate <;> simp_all [Gate.allowed]

theorem unbounded_program_allowed_modulo {n k : Nat} (program : Program n k)
    (modulus : Nat) (h : program.allowed .unbounded) : program.allowed (.modulo modulus) := by
  induction program with
  | empty => trivial
  | append previous gate ih =>
      exact ⟨ih h.1, unbounded_gate_allowed_modulo gate modulus h.2⟩

theorem ac0_in_acc0 : Includes nonuniformAC0 nonuniformACC0 := by
  intro L ⟨family, size, basis, depth, correct⟩
  exact ⟨2, Nat.le_refl _, family, size,
    fun n => unbounded_program_allowed_modulo (family n).program 2 (basis n), depth, correct⟩

end InclusionBench.Circuits
