import InclusionBench.Randomized

/-!
# Probabilistic and unambiguous logarithmic space

The same finite-control machines used for polynomial-time classes are required
here to obey logarithmic work space on *every* computation prefix. The input
head and read-only input do not count as work space. Random bits are streamed,
never supplied on a freely revisitable random tape. Every branch has an
explicit polynomial time bound, including rejecting branches.

`PL` uses strict majority, with ties rejecting. `UL` counts computation paths
with their multiplicities. These are definitions for this concrete model;
standard model equivalences are cited in the formalization dossier, not
asserted as axioms or inherited from the names.
-/

namespace InclusionBench.LogspaceClasses

open Machines Randomized Counting

def logBound (coefficient n : Nat) : Nat :=
  coefficient * (Nat.log2 (n + 1) + 1)

/-- All random prefixes through the time limit obey the space bound.
Halting padding is included and does not grant a readable random tape. -/
def fairSpaceWithin (machine : FairMachine) (bound : Nat → Nat)
    (coefficient : Nat) : Prop :=
  ∀ word coins, coins.length ≤ bound word.length →
    (machine.run word coins).work.footprint ≤ logBound coefficient word.length

def BPL : ComplexityClass :=
  fun L => ∃ machine : FairMachine, ∃ bound coefficient,
    polynomialBound bound ∧ machine.bppWithin bound L ∧
    fairSpaceWithin machine bound coefficient

/-- Unbounded-error polynomial-time, logarithmic-work-space computation.
The strict inequality makes the treatment of exact ties explicit. -/
def PL : ComplexityClass :=
  fun L => ∃ machine : FairMachine, ∃ bound coefficient,
    polynomialBound bound ∧ machine.binaryWithin bound ∧
    fairSpaceWithin machine bound coefficient ∧
    ∀ word, L word ↔ 2 ^ (bound word.length) <
      2 * machine.acceptCount word (bound word.length)

/-- Space is charged on every reachable nondeterministic branch, not just
on the accepting one. -/
def nondeterministicSpaceWithin (machine : NMachine) (bound : Nat → Nat)
    (coefficient : Nat) : Prop :=
  ∀ word time, time ≤ bound word.length →
    ∀ config, machine.reachable word time config →
      config.work.footprint ≤ logBound coefficient word.length

/-- Natural-valued functions counting accepting paths of a single
polynomial-time logarithmic-space machine. -/
def SharpL (f : Word → Nat) : Prop :=
  ∃ machine : NMachine, ∃ bound coefficient,
    polynomialBound bound ∧ allBranchesHaltWithin machine bound ∧
    nondeterministicSpaceWithin machine bound coefficient ∧
    ∀ word, f word = acceptingPaths machine word (bound word.length)

def GapL (g : Word → Int) : Prop :=
  ∃ positive negative : Word → Nat,
    SharpL positive ∧ SharpL negative ∧
    ∀ word, g word = (positive word : Int) - (negative word : Int)

def UL : ComplexityClass :=
  fun L => ∃ f : Word → Nat, SharpL f ∧
    ∀ word, f word ≤ 1 ∧ (L word ↔ 0 < f word)

theorem sharpL_in_sharpP {f : Word → Nat} (hf : SharpL f) : SharpP f := by
  obtain ⟨machine, bound, _, poly, halts, _, value⟩ := hf
  exact ⟨machine, bound, poly, halts, value⟩

theorem gapL_in_gapP {g : Word → Int} (hg : GapL g) : GapP g := by
  obtain ⟨positive, negative, hp, hn, value⟩ := hg
  exact ⟨positive, negative, sharpL_in_sharpP hp, sharpL_in_sharpP hn, value⟩

theorem ul_in_up : Includes UL UP := by
  intro L ⟨f, hf, correct⟩
  exact ⟨f, sharpL_in_sharpP hf, correct⟩

theorem bpl_in_bpp : Includes BPL boundedErrorPolynomialTime := by
  intro L ⟨machine, bound, _, poly, correct, _⟩
  exact ⟨machine, bound, poly, correct⟩

/-- A bounded-error machine's same acceptance count has the correct strict
majority; no amplification or machine simulation is needed. -/
theorem bpl_in_pl : Includes BPL PL := by
  intro L ⟨machine, bound, coefficient, poly, bpp, space⟩
  obtain ⟨binary, correct⟩ := bpp
  refine ⟨machine, bound, coefficient, poly, binary, space, ?_⟩
  intro word
  have positive : 0 < 2 ^ (bound word.length) := Nat.two_pow_pos _
  constructor
  · intro member
    have h := (correct word).1 member
    omega
  · intro majority
    apply Classical.byContradiction
    intro outside
    have h := (correct word).2 outside
    omega

end InclusionBench.LogspaceClasses
