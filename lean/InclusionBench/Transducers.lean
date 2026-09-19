import InclusionBench.Counting

/-!
# Polynomial-time integer transducers

The output tape is write-only and append-only. A transition may append one
bit; the transition table cannot inspect any output bit or the output length.
The implementation stores output in reverse order, adding each emitted bit
at the front, then reverses the list when reading the completed result.
Output is excluded from work-space accounting.

FP is defined by total polynomial-time computation in this concrete model,
not by decidability of an output graph. WPP and LWPP use these computed,
nonzero integer normalizers. Equivalence with textbook models and their
general closure theorems remains unproved.
-/

namespace InclusionBench.Transducers

open Machines
open Counting (GapP SPP polynomialValue)

structure OutputAction (states : Nat) where
  control : Action states
  emit : Option Bool

structure OutputConfiguration (states : Nat) where
  control : Configuration states := {}
  reversedOutput : Word := []

structure Transducer where
  states : Nat
  transition : Fin (states + 1) → InputSymbol → WorkSymbol → Option (OutputAction states)

def applyOutputAction {q : Nat} (word : Word) (config : OutputConfiguration q)
    (action : OutputAction q) : OutputConfiguration q :=
  { control := execute word config.control action.control
    reversedOutput := match action.emit with
      | none => config.reversedOutput
      | some bit => bit :: config.reversedOutput }

def Transducer.step (machine : Transducer) (word : Word)
    (config : OutputConfiguration machine.states) : Option (OutputConfiguration machine.states) :=
  (machine.transition config.control.state
    (readInput word config.control.inputPosition) config.control.work.head).map
    (applyOutputAction word config)

def Transducer.after (machine : Transducer) (word : Word) :
    Nat → OutputConfiguration machine.states
  | 0 => {}
  | time + 1 =>
      let current := machine.after word time
      (machine.step word current).getD current

def Transducer.haltsAt (machine : Transducer) (word : Word) (time : Nat) : Prop :=
  machine.step word (machine.after word time) = none

def Transducer.output (machine : Transducer) (word : Word) (time : Nat) : Word :=
  (machine.after word time).reversedOutput.reverse

/-- Only the ordinary work tape is charged to work space. -/
def OutputConfiguration.workSpace {q : Nat} (config : OutputConfiguration q) : Nat :=
  config.control.work.footprint

/-- The first magnitude bit is the most significant bit. -/
def binaryMagnitude (bits : Word) : Nat :=
  bits.foldl (fun value bit => 2 * value + if bit then 1 else 0) 0

/-- A true sign bit denotes a negative integer. Empty output and either
representation of signed zero denote zero. Leading magnitude zeros are allowed. -/
def decodeInteger : Word → Int
  | [] => 0
  | sign :: magnitude =>
      if sign then -(binaryMagnitude magnitude : Int) else (binaryMagnitude magnitude : Int)

def Transducer.value (machine : Transducer) (word : Word) (time : Nat) : Int :=
  decodeInteger (machine.output word time)

/-- One concrete machine computes the integer function on all inputs and
halts by an explicitly given polynomial horizon. -/
def FP (f : Word → Int) : Prop :=
  ∃ machine : Transducer, ∃ runtime : List Nat,
    ∀ word,
      machine.haltsAt word (polynomialValue runtime word.length) ∧
      machine.value word (polynomialValue runtime word.length) = f word

def WPP : ComplexityClass :=
  fun L => ∃ gap normalizer : Word → Int,
    GapP gap ∧ FP normalizer ∧
    ∀ word, normalizer word ≠ 0 ∧
      (L word → gap word = normalizer word) ∧ (¬ L word → gap word = 0)

/-- The normalizer receives only a unary encoding of input length. -/
def unary (n : Nat) : Word := List.replicate n false

def LWPP : ComplexityClass :=
  fun L => ∃ gap normalizer : Word → Int,
    GapP gap ∧ FP normalizer ∧
    (∀ n, normalizer (unary n) ≠ 0) ∧
    ∀ word,
      (L word → gap word = normalizer (unary word.length)) ∧
      (¬ L word → gap word = 0)

theorem decode_positive_one : decodeInteger [false, true] = 1 := by rfl

theorem decode_negative_one : decodeInteger [true, true] = -1 := by rfl

theorem emit_appends_bit {q : Nat} (word : Word) (config : OutputConfiguration q)
    (action : Action q) (bit : Bool) :
    (applyOutputAction word config { control := action, emit := some bit }).reversedOutput.reverse =
      config.reversedOutput.reverse ++ [bit] := by
  simp [applyOutputAction]

theorem output_action_length_le {q : Nat} (word : Word) (config : OutputConfiguration q)
    (action : OutputAction q) :
    (applyOutputAction word config action).reversedOutput.length ≤
      config.reversedOutput.length + 1 := by
  cases emitted : action.emit <;> simp [applyOutputAction, emitted]

/-- Each transition emits at most one bit, so the polynomial time bound
also bounds output length. -/
theorem output_length_le_time (machine : Transducer) (word : Word) (time : Nat) :
    (machine.output word time).length ≤ time := by
  suffices h : (machine.after word time).reversedOutput.length ≤ time by
    simpa [Transducer.output] using h
  induction time with
  | zero => simp [Transducer.after]
  | succ time ih =>
      let current := machine.after word time
      change ((machine.step word current).getD current).reversedOutput.length ≤ time + 1
      cases next : machine.transition current.control.state
          (readInput word current.control.inputPosition) current.control.work.head with
      | none =>
          simp only [Transducer.step, next, Option.map_none, Option.getD_none]
          exact Nat.le_trans ih (Nat.le_succ time)
      | some action =>
          simp only [Transducer.step, next, Option.map_some, Option.getD_some]
          exact Nat.le_trans (output_action_length_le word current action)
            (Nat.add_le_add_right ih 1)

def zeroTransducer : Transducer :=
  { states := 0, transition := fun _ _ _ => none }

theorem fp_zero : FP (fun _ => 0) := by
  refine ⟨zeroTransducer, [], ?_⟩
  intro word
  exact ⟨rfl, rfl⟩

/-- Emit the positive sign bit, then the magnitude bit one, then halt. -/
def oneTransducer : Transducer :=
  { states := 2
    transition := fun state _ _ =>
      if state.val = 0 then
        some
          { control :=
              { nextState := 1, write := none, inputMove := .stay, workMove := .stay }
            emit := some false }
      else if state.val = 1 then
        some
          { control :=
              { nextState := 2, write := none, inputMove := .stay, workMove := .stay }
            emit := some true }
      else none }

theorem fp_one : FP (fun _ => 1) := by
  refine ⟨oneTransducer, [2], ?_⟩
  intro word
  exact ⟨rfl, rfl⟩

theorem spp_in_wpp : Includes SPP WPP := by
  intro L ⟨gap, hg, correct⟩
  refine ⟨gap, fun _ => 1, hg, fp_one, ?_⟩
  intro word
  exact ⟨by change (1 : Int) ≠ 0; decide, (correct word).1, (correct word).2⟩

theorem spp_in_lwpp : Includes SPP LWPP := by
  intro L ⟨gap, hg, correct⟩
  exact ⟨gap, fun _ => 1, hg, fp_one,
    fun _ => by change (1 : Int) ≠ 0; decide, correct⟩

end InclusionBench.Transducers
