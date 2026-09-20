import Mathlib.Data.Real.Sqrt
import InclusionBench.RealSyntax

/-!
# Existential theory of the real numbers over finite binary inputs

`RealSyntax` supplies a uniquely decoded finite arithmetic / Boolean formula.
Coefficients are binary integers (natural bit strings plus unary negation).
Witnesses range over an explicitly finite tuple of Mathlib's actual real
numbers. They are not rational strings, floating-point approximations, or
bounded-bit algebraic certificates.

`ETR` rejects malformed input and asks whether the decoded formula has a real
solution. `ExistsR` consists of binary languages polynomial-time many-one
reducible to this language by the concrete finite-control output transducer
in `RealSyntax.PolynomialTimeComputable`. The equivalence with conventional
ETR / quadratic-system encodings is a literature bridge; no existing deep
containment theorem is silently asserted by the definition.
-/

namespace InclusionBench.RealFeasibility

open RealSyntax

noncomputable def Term.evaluate (values : Nat → ℝ) : Term → ℝ
  | .variable index => values index
  | .natural magnitude => (Transducers.binaryMagnitude magnitude : ℝ)
  | .negation term => -Term.evaluate values term
  | .addition left right => Term.evaluate values left + Term.evaluate values right
  | .multiplication left right => Term.evaluate values left * Term.evaluate values right

def Formula.Holds (values : Nat → ℝ) : Formula → Prop
  | .falsum => False
  | .verum => True
  | .equality left right => Term.evaluate values left = Term.evaluate values right
  | .lessThan left right => Term.evaluate values left < Term.evaluate values right
  | .negation formula => ¬ Formula.Holds values formula
  | .conjunction left right => Formula.Holds values left ∧ Formula.Holds values right
  | .disjunction left right => Formula.Holds values left ∨ Formula.Holds values right

/-- An assignment contains exactly as many real coordinates as the input
quantifies. Invalid variable references are rejected by `Instance.valid`;
the zero extension merely makes the recursive evaluator total. -/
noncomputable def finiteAssignment {variableCount : Nat} (values : Fin variableCount → ℝ) (index : Nat) : ℝ :=
  if h : index < variableCount then values ⟨index, h⟩ else 0

def Satisfiable (inputObject : Instance) : Prop :=
  inputObject.valid = true ∧ ∃ formula : Formula,
    assemble inputObject.program = some formula ∧
    ∃ values : Fin inputObject.variableCount → ℝ, Formula.Holds (finiteAssignment values) formula

def ETR : Language :=
  fun word => ∃ inputObject : Instance,
    deserialize word = some inputObject ∧ Satisfiable inputObject

def ExistsR : ComplexityClass := fun L => PolynomialManyOne L ETR

theorem encoded_etr_iff (inputObject : Instance) :
    ETR (serialize inputObject) ↔ Satisfiable inputObject := by
  constructor
  · rintro ⟨decoded, parses, trueFormula⟩
    rw [deserialize_serialize] at parses
    cases parses
    exact trueFormula
  · intro trueFormula
    exact ⟨inputObject, deserialize_serialize inputObject, trueFormula⟩

theorem malformed_input_rejected (word : Word) (malformed : deserialize word = none) :
    ¬ ETR word := by
  rintro ⟨decoded, parses, _⟩
  rw [malformed] at parses
  cases parses

theorem finiteAssignment_at {variableCount : Nat} (values : Fin variableCount → ℝ)
    (index : Fin variableCount) : finiteAssignment values index.val = values index := by
  simp [finiteAssignment, index.isLt]

/-- The equation x²=2 is accepted using a genuine real square root. Its
witness is not supplied as a rational encoding to the reduction machine. -/
theorem squareTwo_satisfiable : Satisfiable squareTwo := by
  refine ⟨squareTwo_valid, _, squareTwo_assembles, fun _ => Real.sqrt 2, ?_⟩
  change Real.sqrt 2 * Real.sqrt 2 = (2 : ℝ)
  exact Real.mul_self_sqrt (by exact zero_le_two)

theorem squareTwo_in_etr : ETR (serialize squareTwo) :=
  (encoded_etr_iff squareTwo).2 squareTwo_satisfiable

def negativeSquare : Instance :=
  { variableCount := 1
    program := [.variable 0, .variable 0, .multiplyTerms,
      .natural [true], .negateTerm, .equalTerms] }

theorem negativeSquare_not_satisfiable : ¬ Satisfiable negativeSquare := by
  rintro ⟨_, formula, assembled, values, satisfied⟩
  have parsedFormula : formula = .equality (.multiplication (.variable 0) (.variable 0))
      (.negation (.natural [true])) := by
    simpa [negativeSquare, assemble, runProgram, applyInstruction] using assembled.symm
  subst formula
  change Fin 1 → ℝ at values
  have equation : values 0 * values 0 = (-1 : ℝ) := by
    simpa [Formula.Holds, Term.evaluate, finiteAssignment, negativeSquare,
      Transducers.binaryMagnitude] using satisfied
  have nonnegative := mul_self_nonneg (values 0)
  rw [equation] at nonnegative
  exact (not_le_of_gt (neg_one_lt_zero : (-1 : ℝ) < 0)) nonnegative

theorem negativeSquare_not_in_etr : ¬ ETR (serialize negativeSquare) :=
  fun member => negativeSquare_not_satisfiable ((encoded_etr_iff negativeSquare).1 member)

end InclusionBench.RealFeasibility
