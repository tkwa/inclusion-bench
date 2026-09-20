import InclusionBench.Machines

/-!
# Alternating logarithmic time with random input access

This is an explicit random-access alternating Turing machine. A finite number
of ordinary work tapes have local read/write heads. A separate binary index
tape has a local head and a fixed left endpoint; the input symbol at its
binary address is available in one transition. Input addresses are zero based,
and an out-of-range address returns `none`. There is no input-dependent advice,
arbitrary initialization, arithmetic instruction, or oracle.

The address decoder is the semantics of the random-access input port. It is
not a general unit-cost operation available on ordinary work tapes. Each
transition changes one cell and moves each head by at most one position.
Every branch must halt within c(log₂(n+1)+1) transitions. Existential and
universal branching have their usual finite-tree semantics.

`UniformNC1` denotes this ALOGTIME model. The cited identification is with
DLOGTIME-uniform NC¹ under the standard *extended connection language* U_E,
not the weaker direct-connection-only uniformity U_D. That model-equivalence
theorem remains a literature bridge, not a Lean axiom.
-/

namespace InclusionBench.AlternatingLogtime

open Machines

/-- A semi-infinite binary tape. Missing cells contain zero. The leftmost
cell is the least significant address bit; moving the head does not shift
any existing bit's position or significance. -/
structure IndexTape where
  cells : List Bool := []
  position : Nat := 0
  deriving Repr

def binaryValue : List Bool → Nat
  | [] => 0
  | bit :: rest => (if bit then 1 else 0) + 2 * binaryValue rest

def writeAt : List Bool → Nat → Bool → List Bool
  | [], 0, bit => [bit]
  | [], position + 1, bit => false :: writeAt [] position bit
  | _ :: rest, 0, bit => bit :: rest
  | first :: rest, position + 1, bit => first :: writeAt rest position bit

def IndexTape.head (tape : IndexTape) : Bool := tape.cells[tape.position]?.getD false

def IndexTape.address (tape : IndexTape) : Nat := binaryValue tape.cells

def IndexTape.writeMove (tape : IndexTape) (bit : Bool) (direction : Direction) : IndexTape :=
  { cells := writeAt tape.cells tape.position bit
    position := match direction with
      | .left => tape.position - 1
      | .stay => tape.position
      | .right => tape.position + 1 }

structure Configuration (states tapes : Nat) where
  state : Fin (states + 1) := 0
  work : Fin tapes → WorkTape := fun _ => {}
  index : IndexTape := {}

structure Action (states tapes : Nat) where
  nextState : Fin (states + 1)
  workWrite : Fin tapes → WorkSymbol
  workMove : Fin tapes → Direction
  indexWrite : Bool
  indexMove : Direction

def execute {states tapes : Nat} (config : Configuration states tapes)
    (action : Action states tapes) : Configuration states tapes :=
  { state := action.nextState
    work := fun tape => (config.work tape).writeMove (action.workWrite tape) (action.workMove tape)
    index := config.index.writeMove action.indexWrite action.indexMove }

/-- All arguments to the transition table range over finite types. Its
choice of a transition therefore cannot contain an arbitrary language. -/
structure Machine where
  states : Nat
  tapes : Nat
  transition : Fin (states + 1) → Option Bool → (Fin tapes → WorkSymbol) → Bool →
    List (Action states tapes)
  universal : Fin (states + 1) → Bool
  accept : Fin (states + 1) → Bool

def Machine.successors (machine : Machine) (word : Word)
    (config : Configuration machine.states machine.tapes) :
    List (Configuration machine.states machine.tapes) :=
  (machine.transition config.state word[config.index.address]?
    (fun tape => (config.work tape).head) config.index.head).map (execute config)

def Machine.reachable (machine : Machine) (word : Word) :
    Nat → Configuration machine.states machine.tapes → Prop
  | 0, config => config = {}
  | time + 1, config => ∃ previous,
      machine.reachable word time previous ∧ config ∈ machine.successors word previous

/-- Terminal states use their explicit answer. In particular, a universal
state with no transitions does not accept by vacuous conjunction. -/
def Machine.evaluateFrom (machine : Machine) (word : Word) :
    Nat → Configuration machine.states machine.tapes → Bool
  | 0, config =>
      match machine.successors word config with
      | [] => machine.accept config.state
      | _ :: _ => false
  | fuel + 1, config =>
      match machine.successors word config with
      | [] => machine.accept config.state
      | first :: rest =>
          if machine.universal config.state then
            (first :: rest).all (machine.evaluateFrom word fuel)
          else (first :: rest).any (machine.evaluateFrom word fuel)

def Machine.decidesWithin (machine : Machine) (bound : Nat → Nat) (L : Language) : Prop :=
  ∀ word,
    (∀ config, machine.reachable word (bound word.length) config →
      machine.successors word config = []) ∧
    (machine.evaluateFrom word (bound word.length) {} = true ↔ L word)

def ALOGTIME : ComplexityClass :=
  fun L => ∃ machine : Machine, ∃ coefficient : Nat,
    machine.decidesWithin (fun n => coefficient * (Nat.log2 (n + 1) + 1)) L

def UniformNC1 : ComplexityClass := ALOGTIME

theorem writeAt_reads_written (cells : List Bool) (position : Nat) (bit : Bool) :
    (writeAt cells position bit)[position]? = some bit := by
  induction position generalizing cells with
  | zero => cases cells <;> rfl
  | succ position ih =>
      cases cells with
      | nil => simpa only [writeAt, List.getElem?_cons_succ] using ih []
      | cons first rest => simpa only [writeAt, List.getElem?_cons_succ] using ih rest

theorem index_head_stay (tape : IndexTape) (bit : Bool) :
    (tape.writeMove bit .stay).head = bit := by
  simp [IndexTape.head, IndexTape.writeMove, writeAt_reads_written]

theorem fixed_binary_address : binaryValue [true, false, true] = 5 := rfl

theorem terminal_evaluation (machine : Machine) (word : Word)
    (config : Configuration machine.states machine.tapes)
    (terminal : machine.successors word config = []) (fuel : Nat) :
    machine.evaluateFrom word fuel config = machine.accept config.state := by
  cases fuel <;> simp [Machine.evaluateFrom, terminal]

/-- Two successor branches respectively accept and reject. Switching the
root between existential and universal changes its result, as required. -/
def branchingExample (universalRoot : Bool) : Machine :=
  { states := 2
    tapes := 0
    transition := fun state _ _ _ =>
      if state.val = 0 then
        [{ nextState := 1, workWrite := Fin.elim0, workMove := Fin.elim0,
           indexWrite := false, indexMove := .stay },
         { nextState := 2, workWrite := Fin.elim0, workMove := Fin.elim0,
           indexWrite := false, indexMove := .stay }]
      else []
    universal := fun _ => universalRoot
    accept := fun state => state.val == 1 }

theorem existential_example_accepts :
    (branchingExample false).evaluateFrom [] 1 {} = true := rfl

theorem universal_example_rejects :
    (branchingExample true).evaluateFrom [] 1 {} = false := rfl

end InclusionBench.AlternatingLogtime
