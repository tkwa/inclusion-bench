import InclusionBench.Machines

/-!
# Concrete oracle machines and the polynomial hierarchy

Machines have finite control, read-only input, a work tape, and a separate
query tape. Only a `query` instruction consults the supplied oracle language.
The query is the written binary word on the finite visited query-tape interval
(blank cells are omitted). This encoding is explicit and computable.

Oracle answers are mathematical membership in the chosen language; these
definitions do not claim to execute an undecidable oracle on a computer.
-/

namespace InclusionBench.Oracles

open Machines

structure OracleConfiguration (states : Nat) where
  machine : Configuration states := {}
  queryTape : WorkTape := {}

def OracleConfiguration.queryWord {q : Nat} (config : OracleConfiguration q) : Word :=
  (config.queryTape.left.reverse ++ config.queryTape.head :: config.queryTape.right).filterMap id

inductive OracleAction (states : Nat) where
  | compute (machineAction : Action states) (queryWrite : WorkSymbol) (queryMove : Direction)
  | query (yesState noState : Fin (states + 1))

noncomputable def executeOracle {q : Nat} (oracle : Language) (word : Word)
    (config : OracleConfiguration q) : OracleAction q → OracleConfiguration q
  | .compute action symbol direction =>
      { machine := execute word config.machine action
        queryTape := config.queryTape.writeMove symbol direction }
  | .query yes no =>
      { config with machine :=
        { config.machine with state := @ite _ (oracle config.queryWord) (Classical.propDecidable _) yes no } }

structure DOracleMachine where
  states : Nat
  transition : Fin (states + 1) → InputSymbol → WorkSymbol → WorkSymbol → Option (OracleAction states)
  accept : Fin (states + 1) → Bool

def DOracleMachine.instruction (machine : DOracleMachine) (word : Word)
    (config : OracleConfiguration machine.states) : Option (OracleAction machine.states) :=
  machine.transition config.machine.state (readInput word config.machine.inputPosition)
    config.machine.work.head config.queryTape.head

noncomputable def DOracleMachine.step (machine : DOracleMachine) (oracle : Language) (word : Word)
    (config : OracleConfiguration machine.states) : OracleConfiguration machine.states :=
  match machine.instruction word config with
  | none => config
  | some action => executeOracle oracle word config action

noncomputable def DOracleMachine.after (machine : DOracleMachine) (oracle : Language) (word : Word) :
    Nat → OracleConfiguration machine.states
  | 0 => {}
  | time + 1 => machine.step oracle word (machine.after oracle word time)

noncomputable def DOracleMachine.queryCount (machine : DOracleMachine) (oracle : Language) (word : Word) :
    Nat → Nat
  | 0 => 0
  | time + 1 => machine.queryCount oracle word time +
      match machine.instruction word (machine.after oracle word time) with
      | some (.query _ _) => 1
      | _ => 0

def DOracleMachine.decidesWithin (machine : DOracleMachine) (oracle : Language)
    (bound : Nat → Nat) (L : Language) : Prop :=
  ∀ word, ∃ time ≤ bound word.length,
    machine.instruction word (machine.after oracle word time) = none ∧
    (machine.accept (machine.after oracle word time).machine.state = true ↔ L word)

def DOracleMachine.decidesWithQueries (machine : DOracleMachine) (oracle : Language)
    (timeBound queryBound : Nat → Nat) (L : Language) : Prop :=
  ∀ word, ∃ time ≤ timeBound word.length,
    machine.instruction word (machine.after oracle word time) = none ∧
    (machine.accept (machine.after oracle word time).machine.state = true ↔ L word) ∧
    machine.queryCount oracle word time ≤ queryBound word.length

structure NOracleMachine where
  states : Nat
  transition : Fin (states + 1) → InputSymbol → WorkSymbol → WorkSymbol → List (OracleAction states)
  accept : Fin (states + 1) → Bool

noncomputable def NOracleMachine.successors (machine : NOracleMachine) (oracle : Language) (word : Word)
    (config : OracleConfiguration machine.states) : List (OracleConfiguration machine.states) :=
  (machine.transition config.machine.state (readInput word config.machine.inputPosition)
    config.machine.work.head config.queryTape.head).map (executeOracle oracle word config)

def NOracleMachine.reachable (machine : NOracleMachine) (oracle : Language) (word : Word) :
    Nat → OracleConfiguration machine.states → Prop
  | 0, config => config = {}
  | time + 1, config => ∃ previous,
      machine.reachable oracle word time previous ∧ config ∈ machine.successors oracle word previous

def NOracleMachine.decidesWithin (machine : NOracleMachine) (oracle : Language)
    (bound : Nat → Nat) (L : Language) : Prop :=
  ∀ word,
    (∀ config, machine.reachable oracle word (bound word.length) config →
      machine.successors oracle word config = []) ∧
    (L word ↔ ∃ time ≤ bound word.length, ∃ config,
      machine.reachable oracle word time config ∧ machine.successors oracle word config = [] ∧
      machine.accept config.machine.state = true)

def deterministicPolynomialWith (oracle : Language) : ComplexityClass :=
  fun L => ∃ machine : DOracleMachine, ∃ bound,
    polynomialBound bound ∧ machine.decidesWithin oracle bound L

def nondeterministicPolynomialWith (oracle : Language) : ComplexityClass :=
  fun L => ∃ machine : NOracleMachine, ∃ bound,
    polynomialBound bound ∧ machine.decidesWithin oracle bound L

/-- The oracle is a single language in the specified class, fixed for every
input length. It is not arbitrary length advice. -/
def POracle (oracleClass : ComplexityClass) : ComplexityClass :=
  fun L => ∃ oracle, oracleClass oracle ∧ deterministicPolynomialWith oracle L

def NPOracle (oracleClass : ComplexityClass) : ComplexityClass :=
  fun L => ∃ oracle, oracleClass oracle ∧ nondeterministicPolynomialWith oracle L

def Sigma2P : ComplexityClass := NPOracle nondeterministicPolynomialTime
def Pi2P : ComplexityClass := coClass Sigma2P
def Delta2P : ComplexityClass := POracle nondeterministicPolynomialTime

def Theta2P : ComplexityClass :=
  fun L => ∃ oracle, nondeterministicPolynomialTime oracle ∧
    ∃ machine : DOracleMachine, ∃ bound coefficient,
      polynomialBound bound ∧ machine.decidesWithQueries oracle bound
        (fun n => coefficient * (Nat.log2 (n + 1) + 1)) L

def sigmaLevel : Nat → ComplexityClass
  | 0 => polynomialTime
  | 1 => nondeterministicPolynomialTime
  | level + 2 => NPOracle (sigmaLevel (level + 1))

def PH : ComplexityClass := fun L => ∃ level, sigmaLevel level L

theorem theta2_in_delta2 : Includes Theta2P Delta2P := by
  intro L ⟨oracle, oracleNP, machine, bound, coefficient, polynomial, correct⟩
  refine ⟨oracle, oracleNP, machine, bound, polynomial, ?_⟩
  intro word
  obtain ⟨time, bounded, halted, decides, _⟩ := correct word
  exact ⟨time, bounded, halted, decides⟩

theorem sigma2_in_ph : Includes Sigma2P PH := fun _ h => ⟨2, h⟩

theorem np_in_ph : Includes nondeterministicPolynomialTime PH := fun _ h => ⟨1, h⟩

end InclusionBench.Oracles
