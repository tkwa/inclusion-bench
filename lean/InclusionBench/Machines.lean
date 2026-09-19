import InclusionBench.Semantics

/-!
# Concrete finite-control machines

These definitions use a read-only binary input tape with endmarkers and a
two-way binary work tape with a blank symbol. Transition tables have finite
domains and finite actions. No oracle, arbitrary initialization function, or
language parameter is hidden in a transition system.

Resource classes below are definitions for this explicit model. Equivalence
with textbook models and membership theorems in the literature remain proof
obligations; the benchmark catalog does not silently use them as theorems.
-/

namespace InclusionBench.Machines

inductive Direction where
  | left | stay | right
  deriving DecidableEq, Repr

inductive InputSymbol where
  | leftEnd | bit (value : Bool) | rightEnd
  deriving DecidableEq, Repr

abbrev WorkSymbol := Option Bool

structure WorkTape where
  left : List WorkSymbol := []
  head : WorkSymbol := none
  right : List WorkSymbol := []
  deriving Repr

def WorkTape.writeMove (t : WorkTape) (symbol : WorkSymbol) : Direction → WorkTape
  | .stay => { t with head := symbol }
  | .left =>
      { left := t.left.drop 1, head := t.left.headD none, right := symbol :: t.right }
  | .right =>
      { left := symbol :: t.left, head := t.right.headD none, right := t.right.drop 1 }

/-- Number of work cells in the represented visited interval; the read-only
input tape is excluded, so logarithmic work space is meaningful. -/
def WorkTape.footprint (t : WorkTape) : Nat := t.left.length + 1 + t.right.length

def readInput (word : Word) (position : Nat) : InputSymbol :=
  if position = 0 then .leftEnd
  else match word[position - 1]? with
    | some b => .bit b
    | none => .rightEnd

def moveInput (word : Word) (position : Nat) : Direction → Nat
  | .left => position - 1
  | .stay => position
  | .right => min (position + 1) (word.length + 1)

structure Action (states : Nat) where
  nextState : Fin (states + 1)
  write : WorkSymbol
  inputMove : Direction
  workMove : Direction

structure Configuration (states : Nat) where
  state : Fin (states + 1) := 0
  inputPosition : Nat := 0
  work : WorkTape := {}

def execute {q : Nat} (word : Word) (config : Configuration q)
    (action : Action q) : Configuration q :=
  { state := action.nextState
    inputPosition := moveInput word config.inputPosition action.inputMove
    work := config.work.writeMove action.write action.workMove }

structure DMachine where
  states : Nat
  transition : Fin (states + 1) → InputSymbol → WorkSymbol → Option (Action states)
  accept : Fin (states + 1) → Bool

def DMachine.step (machine : DMachine) (word : Word)
    (config : Configuration machine.states) : Option (Configuration machine.states) :=
  (machine.transition config.state (readInput word config.inputPosition) config.work.head).map
    (execute word config)

def DMachine.after (machine : DMachine) (word : Word) : Nat → Configuration machine.states
  | 0 => {}
  | time + 1 =>
      let current := machine.after word time
      (machine.step word current).getD current

def DMachine.haltsAt (machine : DMachine) (word : Word) (time : Nat) : Prop :=
  machine.step word (machine.after word time) = none

def DMachine.decidesWithin (machine : DMachine) (bound : Nat → Nat) (L : Language) : Prop :=
  ∀ word, ∃ time ≤ bound word.length,
    machine.haltsAt word time ∧
    (machine.accept (machine.after word time).state = true ↔ L word)

def DMachine.decidesInSpace (machine : DMachine) (bound : Nat → Nat) (L : Language) : Prop :=
  ∀ word, ∃ time,
    machine.haltsAt word time ∧
    (machine.accept (machine.after word time).state = true ↔ L word) ∧
    (∀ visited ≤ time, (machine.after word visited).work.footprint ≤ bound word.length)

def DTIME (bound : Nat → Nat) : ComplexityClass :=
  fun L => ∃ machine : DMachine, machine.decidesWithin bound L

def DSPACE (bound : Nat → Nat) : ComplexityClass :=
  fun L => ∃ machine : DMachine, machine.decidesInSpace bound L

def polynomialBound (bound : Nat → Nat) : Prop :=
  ∃ coefficient degree : Nat, ∀ n, bound n ≤ coefficient * (n + 1) ^ degree

def polynomialTime : ComplexityClass :=
  fun L => ∃ bound, polynomialBound bound ∧ DTIME bound L

def polynomialSpace : ComplexityClass :=
  fun L => ∃ bound, polynomialBound bound ∧ DSPACE bound L

def logarithmicSpace : ComplexityClass :=
  fun L => ∃ coefficient, DSPACE (fun n => coefficient * (Nat.log2 (n + 1) + 1)) L

/-- The same deterministic machine meets both bounds. -/
def simultaneousPolytimePolylogspace : ComplexityClass :=
  fun L => ∃ machine : DMachine, ∃ timeBound coefficient degree,
    polynomialBound timeBound ∧ machine.decidesWithin timeBound L ∧
    machine.decidesInSpace (fun n => coefficient * (Nat.log2 (n + 1) + 1) ^ degree) L

def exponentialTime : ComplexityClass :=
  fun L => ∃ coefficient degree, DTIME (fun n => 2 ^ (coefficient * (n + 1) ^ degree)) L

def linearExponentialTime : ComplexityClass :=
  fun L => ∃ coefficient, DTIME (fun n => 2 ^ (coefficient * (n + 1))) L

def exponentialSpace : ComplexityClass :=
  fun L => ∃ coefficient degree, DSPACE (fun n => 2 ^ (coefficient * (n + 1) ^ degree)) L

structure NMachine where
  states : Nat
  transition : Fin (states + 1) → InputSymbol → WorkSymbol → List (Action states)
  accept : Fin (states + 1) → Bool

def NMachine.successors (machine : NMachine) (word : Word)
    (config : Configuration machine.states) : List (Configuration machine.states) :=
  (machine.transition config.state (readInput word config.inputPosition) config.work.head).map
    (execute word config)

def NMachine.reachable (machine : NMachine) (word : Word) :
    Nat → Configuration machine.states → Prop
  | 0, config => config = {}
  | time + 1, config => ∃ previous,
      machine.reachable word time previous ∧ config ∈ machine.successors word previous

def NMachine.decidesWithin (machine : NMachine) (bound : Nat → Nat) (L : Language) : Prop :=
  ∀ word,
    (∀ config, machine.reachable word (bound word.length) config →
      machine.successors word config = []) ∧
    (L word ↔ ∃ time ≤ bound word.length, ∃ config,
      machine.reachable word time config ∧ machine.successors word config = [] ∧
      machine.accept config.state = true)

def NTIME (bound : Nat → Nat) : ComplexityClass :=
  fun L => ∃ machine : NMachine, machine.decidesWithin bound L

/-- Every branch halts, and every configuration on every branch meets the
work-space bound. The per-input time bound is finite but otherwise unrestricted. -/
def NMachine.decidesInSpace (machine : NMachine) (bound : Nat → Nat) (L : Language) : Prop :=
  ∀ word, ∃ time,
    (∀ config, machine.reachable word time config → machine.successors word config = []) ∧
    (∀ visited ≤ time, ∀ config, machine.reachable word visited config →
      config.work.footprint ≤ bound word.length) ∧
    (L word ↔ ∃ visited ≤ time, ∃ config,
      machine.reachable word visited config ∧ machine.successors word config = [] ∧
      machine.accept config.state = true)

def NSPACE (bound : Nat → Nat) : ComplexityClass :=
  fun L => ∃ machine : NMachine, machine.decidesInSpace bound L

def nondeterministicLogarithmicSpace : ComplexityClass :=
  fun L => ∃ coefficient, NSPACE (fun n => coefficient * (Nat.log2 (n + 1) + 1)) L

def nondeterministicPolynomialTime : ComplexityClass :=
  fun L => ∃ bound, polynomialBound bound ∧ NTIME bound L

def nondeterministicExponentialTime : ComplexityClass :=
  fun L => ∃ coefficient degree, NTIME (fun n => 2 ^ (coefficient * (n + 1) ^ degree)) L

def nondeterministicLinearExponentialTime : ComplexityClass :=
  fun L => ∃ coefficient, NTIME (fun n => 2 ^ (coefficient * (n + 1))) L

theorem dtime_monotone {small large : Nat → Nat}
    (bound : ∀ n, small n ≤ large n) : Includes (DTIME small) (DTIME large) := by
  intro L ⟨machine, hm⟩
  refine ⟨machine, ?_⟩
  intro word
  obtain ⟨time, ht, halted, correct⟩ := hm word
  exact ⟨time, Nat.le_trans ht (bound _), halted, correct⟩

theorem dspace_monotone {small large : Nat → Nat}
    (bound : ∀ n, small n ≤ large n) : Includes (DSPACE small) (DSPACE large) := by
  intro L ⟨machine, hm⟩
  refine ⟨machine, ?_⟩
  intro word
  obtain ⟨time, halted, correct, space⟩ := hm word
  exact ⟨time, halted, correct, fun visited hv => Nat.le_trans (space visited hv) (bound _)⟩

theorem simultaneous_in_polynomial_time :
    Includes simultaneousPolytimePolylogspace polynomialTime := by
  intro L ⟨machine, timeBound, _, _, polynomial, time, _⟩
  exact ⟨timeBound, polynomial, machine, time⟩

theorem linear_exponential_in_exponential :
    Includes linearExponentialTime exponentialTime := by
  intro L ⟨coefficient, hm⟩
  refine ⟨coefficient, 1, ?_⟩
  simpa only [Nat.pow_one] using hm

theorem nlinear_exponential_in_nexponential :
    Includes nondeterministicLinearExponentialTime nondeterministicExponentialTime := by
  intro L ⟨coefficient, hm⟩
  refine ⟨coefficient, 1, ?_⟩
  simpa only [Nat.pow_one] using hm

end InclusionBench.Machines
