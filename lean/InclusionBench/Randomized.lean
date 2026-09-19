import InclusionBench.Counting

/-!
# Finite fair-coin machines

Each nonterminal transition chooses between exactly two finite actions using
one fair bit. Halting configurations remain fixed when unused random bits
are padded. A budget of t steps therefore has exactly 2^t equiprobable random
strings; probabilities are not fractions of variable-branch nondeterministic
paths. A terminal answer may be true, false, or a declared failure.
-/

namespace InclusionBench.Randomized

open Machines

structure FairMachine where
  states : Nat
  transition : Fin (states + 1) → InputSymbol → WorkSymbol →
    Option (Action states × Action states)
  answer : Fin (states + 1) → Option Bool

def FairMachine.halted (machine : FairMachine) (word : Word)
    (config : Configuration machine.states) : Prop :=
  machine.transition config.state (readInput word config.inputPosition) config.work.head = none

def FairMachine.step (machine : FairMachine) (word : Word)
    (config : Configuration machine.states) (coin : Bool) : Configuration machine.states :=
  match machine.transition config.state (readInput word config.inputPosition) config.work.head with
  | none => config
  | some actions => execute word config (if coin then actions.2 else actions.1)

def FairMachine.runFrom (machine : FairMachine) (word : Word)
    (config : Configuration machine.states) : List Bool → Configuration machine.states
  | [] => config
  | coin :: remaining => machine.runFrom word (machine.step word config coin) remaining

def FairMachine.run (machine : FairMachine) (word coins : Word) : Configuration machine.states :=
  machine.runFrom word {} coins

def FairMachine.result (machine : FairMachine) (word coins : Word) : Option Bool :=
  machine.answer (machine.run word coins).state

def coinStrings : Nat → List Word
  | 0 => [[]]
  | n + 1 => (coinStrings n).map (false :: ·) ++ (coinStrings n).map (true :: ·)

theorem coinStrings_length (n : Nat) : (coinStrings n).length = 2 ^ n := by
  induction n with
  | zero => rfl
  | succ n ih => simp [coinStrings, ih, Nat.pow_succ, Nat.mul_two]

theorem halted_padding (machine : FairMachine) (word : Word)
    (config : Configuration machine.states) (halted : machine.halted word config)
    (coins : Word) : machine.runFrom word config coins = config := by
  simp only [FairMachine.halted] at halted
  induction coins with
  | nil => rfl
  | cons coin coins ih =>
      simpa only [FairMachine.runFrom, FairMachine.step, halted] using ih

def FairMachine.acceptCount (machine : FairMachine) (word : Word) (budget : Nat) : Nat :=
  (coinStrings budget).countP (fun coins => decide (machine.result word coins = some true))

def FairMachine.rejectCount (machine : FairMachine) (word : Word) (budget : Nat) : Nat :=
  (coinStrings budget).countP (fun coins => decide (machine.result word coins = some false))

/-- Every random string halts within the budget and returns a Boolean answer. -/
def FairMachine.binaryWithin (machine : FairMachine) (bound : Nat → Nat) : Prop :=
  ∀ word coins, coins ∈ coinStrings (bound word.length) →
    machine.halted word (machine.run word coins) ∧ machine.result word coins ≠ none

def FairMachine.bppWithin (machine : FairMachine) (bound : Nat → Nat) (L : Language) : Prop :=
  machine.binaryWithin bound ∧ ∀ word,
    (L word → 2 * 2 ^ (bound word.length) ≤ 3 * machine.acceptCount word (bound word.length)) ∧
    (¬ L word → 3 * machine.acceptCount word (bound word.length) ≤ 2 ^ (bound word.length))

def FairMachine.rpWithin (machine : FairMachine) (bound : Nat → Nat) (L : Language) : Prop :=
  machine.binaryWithin bound ∧ ∀ word,
    (L word → 2 ^ (bound word.length) ≤ 2 * machine.acceptCount word (bound word.length)) ∧
    (¬ L word → machine.acceptCount word (bound word.length) = 0)

/-- Bounded Las Vegas computation: no wrong answer, failure probability at
most one half, and a polynomial bound on every trial. Restarting trials gives
the usual expected-time view of ZPP; that equivalence is not yet proved here. -/
def FairMachine.lasVegasWithin (machine : FairMachine) (bound : Nat → Nat) (L : Language) : Prop :=
  ∀ word,
    (∀ coins ∈ coinStrings (bound word.length),
      machine.halted word (machine.run word coins) ∧
      (machine.result word coins = some true → L word) ∧
      (machine.result word coins = some false → ¬ L word)) ∧
    (2 ^ (bound word.length) ≤
      2 * (machine.acceptCount word (bound word.length) + machine.rejectCount word (bound word.length)))

def boundedErrorPolynomialTime : ComplexityClass :=
  fun L => ∃ machine : FairMachine, ∃ bound,
    polynomialBound bound ∧ machine.bppWithin bound L

def oneSidedPolynomialTime : ComplexityClass :=
  fun L => ∃ machine : FairMachine, ∃ bound,
    polynomialBound bound ∧ machine.rpWithin bound L

def coOneSidedPolynomialTime : ComplexityClass := coClass oneSidedPolynomialTime

def zeroErrorPolynomialTime : ComplexityClass :=
  fun L => ∃ machine : FairMachine, ∃ bound,
    polynomialBound bound ∧ machine.lasVegasWithin bound L

/-- Acceptance is at least 2^-q on members and at most half that on
nonmembers. The threshold exponent has an explicit finite polynomial code. -/
def smallBoundedProbability : ComplexityClass :=
  fun L => ∃ machine : FairMachine, ∃ bound, ∃ exponent : List Nat,
    polynomialBound bound ∧ machine.binaryWithin bound ∧ ∀ word,
    (L word → 2 ^ (bound word.length) ≤
      2 ^ (Counting.polynomialValue exponent word.length) * machine.acceptCount word (bound word.length)) ∧
    (¬ L word →
      2 ^ (Counting.polynomialValue exponent word.length + 1) * machine.acceptCount word (bound word.length) ≤
      2 ^ (bound word.length))

theorem rp_in_sbp : Includes oneSidedPolynomialTime smallBoundedProbability := by
  intro L ⟨machine, bound, polynomial, binary, correct⟩
  refine ⟨machine, bound, [1], polynomial, binary, ?_⟩
  intro word
  constructor
  · intro member
    simpa [Counting.polynomialValue] using (correct word).1 member
  · intro outside
    simp [(correct word).2 outside]

end InclusionBench.Randomized
