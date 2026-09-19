import InclusionBench.Machines

/-!
# Counting classes for the concrete nondeterministic machine model

The recursion below counts finite computation paths, preserving multiplicity
in each transition list. It does not count distinct reachable configurations.
A halted accepting branch contributes one, regardless of unused time. A
nonhalting branch at the depth limit contributes zero; `SharpP` additionally
requires that every branch has halted at that limit.

These are operational definitions in the model of `Machines.lean`. Their
equivalence with textbook machine models remains unproved. In particular, no
catalog containment is imported as a theorem. LWPP and WPP are omitted until
there is a concrete polynomial-time integer-output transducer model.
-/

namespace InclusionBench.Counting

open Machines

/-- Accepting leaves at depth at most `fuel`, with transition-list
multiplicities retained even when two actions reach the same configuration. -/
def acceptingPathsFrom (machine : NMachine) (word : Word) :
    Nat → Configuration machine.states → Nat
  | 0, config =>
      match machine.successors word config with
      | [] => if machine.accept config.state then 1 else 0
      | _ :: _ => 0
  | fuel + 1, config =>
      match machine.successors word config with
      | [] => if machine.accept config.state then 1 else 0
      | first :: rest =>
          acceptingPathsFrom machine word fuel first +
            (rest.map (acceptingPathsFrom machine word fuel)).sum

def acceptingPaths (machine : NMachine) (word : Word) (fuel : Nat) : Nat :=
  acceptingPathsFrom machine word fuel {}

/-- Since halted branches have no successors, this also permits branches
that halted before `bound`. No branch may continue beyond the bound. -/
def allBranchesHaltWithin (machine : NMachine) (bound : Nat → Nat) : Prop :=
  ∀ word config, machine.reachable word (bound word.length) config →
    machine.successors word config = []

/-- A natural-valued function counts accepting paths of one polynomial-time
machine that halts on every branch, on every input. -/
def SharpP (f : Word → Nat) : Prop :=
  ∃ machine : NMachine, ∃ bound : Nat → Nat,
    polynomialBound bound ∧ allBranchesHaltWithin machine bound ∧
    ∀ word, f word = acceptingPaths machine word (bound word.length)

/-- Integer differences of two #P functions. -/
def GapP (g : Word → Int) : Prop :=
  ∃ positive negative : Word → Nat,
    SharpP positive ∧ SharpP negative ∧
    ∀ word, g word = (positive word : Int) - (negative word : Int)

def UP : ComplexityClass :=
  fun L => ∃ f : Word → Nat, SharpP f ∧
    ∀ word, f word ≤ 1 ∧ (L word ↔ 0 < f word)

def coUP : ComplexityClass := coClass UP

def FewP : ComplexityClass :=
  fun L => ∃ f : Word → Nat, SharpP f ∧
    ∃ bound : Nat → Nat, polynomialBound bound ∧
    ∀ word, f word ≤ bound word.length ∧ (L word ↔ 0 < f word)

def SPP : ComplexityClass :=
  fun L => ∃ g : Word → Int, GapP g ∧
    ∀ word, (L word → g word = 1) ∧ (¬ L word → g word = 0)

def CeqP : ComplexityClass :=
  fun L => ∃ g : Word → Int, GapP g ∧ ∀ word, L word ↔ g word = 0

def PP : ComplexityClass :=
  fun L => ∃ g : Word → Int, GapP g ∧ ∀ word, L word ↔ 0 < g word

def parityP : ComplexityClass :=
  fun L => ∃ f : Word → Nat, SharpP f ∧ ∀ word, L word ↔ f word % 2 = 1

/-- A finite, explicit polynomial with natural coefficients, evaluated by
Horner's rule. Coefficient lists contain no advice or arbitrary function. -/
def polynomialValue : List Nat → Nat → Nat
  | [], _ => 0
  | coefficient :: remaining, n => coefficient + n * polynomialValue remaining n

/-- The inequalities express inverse-exponential additive error without
division. The numerator lies in [0, 2^p] on every input. -/
def approximatesCharacteristic (L : Language) (g : Word → Int)
    (normalizer error : List Nat) : Prop :=
  ∀ word,
    let denominator : Int := 2 ^ polynomialValue normalizer word.length
    let accuracy : Int := 2 ^ polynomialValue error word.length
    0 ≤ g word ∧ g word ≤ denominator ∧
    (L word → (accuracy - 1) * denominator ≤ accuracy * g word) ∧
    (¬ L word → accuracy * g word ≤ denominator)

/-- For every requested inverse-exponential polynomial error, one GapP
numerator and one explicit power-of-two polynomial normalizer work on all
inputs. This is not a constant-error relaxation. -/
def AWPP : ComplexityClass :=
  fun L => ∀ error : List Nat, ∃ g : Word → Int, ∃ normalizer : List Nat,
    GapP g ∧ approximatesCharacteristic L g normalizer error

theorem up_in_fewp : Includes UP FewP := by
  intro L ⟨f, hf, correct⟩
  refine ⟨f, hf, fun _ => 1, ?_, correct⟩
  exact ⟨1, 0, fun _ => by simp⟩

theorem spp_in_pp : Includes SPP PP := by
  intro L ⟨g, hg, correct⟩
  refine ⟨g, hg, ?_⟩
  intro word
  constructor
  · intro member
    rw [(correct word).1 member]
    decide
  · intro positive
    apply Classical.byContradiction
    intro outside
    rw [(correct word).2 outside] at positive
    exact (Int.lt_irrefl 0) positive

/-- An exact characteristic GapP function meets every requested AWPP error
bound, with denominator one. -/
theorem spp_in_awpp : Includes SPP AWPP := by
  intro L ⟨g, hg, correct⟩ error
  refine ⟨g, [], hg, ?_⟩
  intro word
  rcases Classical.em (L word) with member | outside
  · simp only [polynomialValue, Int.pow_zero, (correct word).1 member,
      Int.mul_one]
    exact ⟨by decide, by decide, fun _ => by omega, fun h => False.elim (h member)⟩
  · simp only [polynomialValue, Int.pow_zero, (correct word).2 outside,
      Int.mul_zero, Int.mul_one]
    exact ⟨by decide, by decide, fun h => False.elim (outside h), fun _ => by decide⟩

theorem gapP_negation {g : Word → Int} (hg : GapP g) :
    GapP (fun word => -g word) := by
  obtain ⟨positive, negative, hp, hn, equation⟩ := hg
  refine ⟨negative, positive, hn, hp, ?_⟩
  intro word
  change -g word = _
  rw [equation word]
  omega

/-- A machine with no transitions halts at time zero. -/
def constantMachine (accepting : Bool) : NMachine :=
  { states := 0, transition := fun _ _ _ => [], accept := fun _ => accepting }

theorem sharpP_constant (accepting : Bool) :
    SharpP (fun _ => if accepting then 1 else 0) := by
  refine ⟨constantMachine accepting, fun _ => 0, ?_, ?_, ?_⟩
  · exact ⟨0, 0, fun _ => by simp⟩
  · intro word config _
    rfl
  · intro word
    rfl

theorem sharpP_zero : SharpP (fun _ => 0) := sharpP_constant false

theorem sharpP_one : SharpP (fun _ => 1) := sharpP_constant true

theorem halted_branch_count (machine : NMachine) (word : Word)
    (config : Configuration machine.states)
    (halted : machine.successors word config = []) (fuel : Nat) :
    acceptingPathsFrom machine word fuel config =
      if machine.accept config.state then 1 else 0 := by
  cases fuel <;> simp [acceptingPathsFrom, halted]

/-- Both listed actions are the same action. The two branches must count
separately even though their configurations coincide. -/
def duplicateBranchMachine : NMachine :=
  { states := 1
    transition := fun state _ _ =>
      if state.val = 0 then
        let action : Action 1 :=
          { nextState := 1, write := none, inputMove := .stay, workMove := .stay }
        [action, action]
      else []
    accept := fun state => state.val == 1 }

theorem duplicate_branches_count_two :
    acceptingPaths duplicateBranchMachine [] 1 = 2 := by
  rfl

end InclusionBench.Counting
