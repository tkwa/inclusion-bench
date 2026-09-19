import InclusionBench.Transducers
import InclusionBench.ProofSystems

/-!
# Statistical Difference with concrete uniform samplers

A sampler is a finite-control output transducer, with a finite polynomial
runtime description and halting on every encoded or malformed binary input.
It receives the injective encoding `encodeTriple input coins []`. There is no
unrestricted sampling function, circuit-advice family, or interpretation
parameter. The common random-string length is an explicit polynomial; unused
random bits can be ignored by a sampler.

Each outcome list retains one entry for every fair-coin string. Repeated
outputs therefore retain their probability mass. The support is the
deduplicated union of both output lists. The sum of the absolute differences
of their multiplicities, divided by `2 * 2^randomBits`, is total variation
distance. We retain this fraction as a numerator/denominator pair and use
cross-multiplied inequalities, never truncated natural-number division.

`SZK` below is the Statistical-Difference characterization, restricted to
total languages by requiring the distance gap on EVERY input. Its equivalence
to the catalog's interactive statistical zero-knowledge definition is an
unproved obligation, not a theorem supplied by this module.

Primary reference: Amit Sahai and Salil Vadhan, *A Complete Problem for
Statistical Zero Knowledge*, JACM 50(2), 196–249, 2003, Theorem 3.1 (p. 208)
and the Polarization Lemma in Section 3.2:
https://www.cs.ucla.edu/~sahai/work/web/2003%20Publications/J.ACM2003.pdf
The paper uses distance > 2/3 versus < 1/3, and notes (2/3)^2 > 1/3.
Our weak inequalities have the same intended meaning: finite fair-coin
distributions have dyadic distance, so neither boundary is attainable.
The strict/weak equivalence and the sampler/circuit equivalence are not proved
here. Variable-length outputs can be encoded injectively into fixed-length
outputs using their polynomial length bound; that bridge is also unproved.
-/

namespace InclusionBench.Statistical

open Counting (polynomialValue)
open Randomized (coinStrings coinStrings_length)

structure Sampler where
  machine : Transducers.Transducer
  runtime : List Nat
  halts : ∀ encoded,
    machine.haltsAt encoded (polynomialValue runtime encoded.length)

def samplerInput (input coins : Word) : Word :=
  ProofSystems.encodeTriple input coins []

def Sampler.sample (sampler : Sampler) (input coins : Word) : Word :=
  let encoded := samplerInput input coins
  sampler.machine.output encoded (polynomialValue sampler.runtime encoded.length)

/-- This is a list of equiprobable outcomes, not a set. Equal outputs occur
once for each random string producing them. -/
def Sampler.draws (sampler : Sampler) (input : Word) (randomBits : Nat) : List Word :=
  (coinStrings randomBits).map (sampler.sample input)

def outcomeSupport (first second : List Word) : List Word :=
  (first ++ second).eraseDups

/-- A finite sum over distinct output words. `first` and `second` themselves
are not deduplicated: their counts carry the probability masses. -/
def countDifferenceSum (first second : List Word) : List Word → Nat
  | [] => 0
  | outcome :: remaining =>
      ((first.count outcome : Int) - (second.count outcome : Int)).natAbs +
        countDifferenceSum first second remaining

def variationNumerator (first second : Sampler) (input : Word) (randomBits : Nat) : Nat :=
  let draws₀ := first.draws input randomBits
  let draws₁ := second.draws input randomBits
  countDifferenceSum draws₀ draws₁ (outcomeSupport draws₀ draws₁)

def variationDenominator (randomBits : Nat) : Nat := 2 * 2 ^ randomBits

/-- The exact, possibly unreduced rational fraction. -/
def totalVariationFraction (first second : Sampler) (input : Word)
    (randomBits : Nat) : Nat × Nat :=
  (variationNumerator first second input randomBits, variationDenominator randomBits)

def far (first second : Sampler) (input : Word) (randomBits : Nat) : Prop :=
  2 * variationDenominator randomBits ≤ 3 * variationNumerator first second input randomBits

def close (first second : Sampler) (input : Word) (randomBits : Nat) : Prop :=
  3 * variationNumerator first second input randomBits ≤ variationDenominator randomBits

/-- Every input must reduce to the correct side of the Statistical Difference
promise. The samplers and random-length polynomial are fixed for all inputs. -/
def SZK : ComplexityClass :=
  fun L => ∃ first second : Sampler, ∃ randomLength : List Nat,
    ∀ input,
      (L input → far first second input (polynomialValue randomLength input.length)) ∧
      (¬ L input → close first second input (polynomialValue randomLength input.length))

theorem samplerInput_injective {input coins otherInput otherCoins : Word}
    (same : samplerInput input coins = samplerInput otherInput otherCoins) :
    input = otherInput ∧ coins = otherCoins := by
  have decoded := ProofSystems.encodeTriple_injective same
  exact ⟨decoded.1, decoded.2.1⟩

theorem samplerInput_length (input coins : Word) :
    (samplerInput input coins).length = 2 * (input.length + coins.length) + 3 := by
  simpa [samplerInput] using ProofSystems.encodeTriple_length input coins []

theorem sample_length_le_runtime (sampler : Sampler) (input coins : Word) :
    (sampler.sample input coins).length ≤
      polynomialValue sampler.runtime (samplerInput input coins).length := by
  exact Transducers.output_length_le_time sampler.machine (samplerInput input coins)
    (polynomialValue sampler.runtime (samplerInput input coins).length)

theorem draws_length (sampler : Sampler) (input : Word) (randomBits : Nat) :
    (sampler.draws input randomBits).length = 2 ^ randomBits := by
  simp [Sampler.draws, coinStrings_length]

theorem outcome_count_le_trials (sampler : Sampler) (input outcome : Word)
    (randomBits : Nat) : (sampler.draws input randomBits).count outcome ≤ 2 ^ randomBits := by
  exact Nat.le_trans List.count_le_length (Nat.le_of_eq (draws_length sampler input randomBits))

theorem denominator_positive (randomBits : Nat) : 0 < variationDenominator randomBits := by
  exact Nat.mul_pos (by decide) (Nat.two_pow_pos randomBits)

theorem countDifferenceSum_self (draws support : List Word) :
    countDifferenceSum draws draws support = 0 := by
  induction support with
  | nil => rfl
  | cons outcome remaining ih => simp [countDifferenceSum, ih]

theorem identical_numerator_zero (sampler : Sampler) (input : Word) (randomBits : Nat) :
    variationNumerator sampler sampler input randomBits = 0 := by
  exact countDifferenceSum_self _ _

theorem identical_samplers_close (sampler : Sampler) (input : Word) (randomBits : Nat) :
    close sampler sampler input randomBits := by
  simp [close, identical_numerator_zero]

theorem far_close_disjoint (first second : Sampler) (input : Word) (randomBits : Nat) :
    ¬ (far first second input randomBits ∧ close first second input randomBits) := by
  intro ⟨distant, near⟩
  have positive := denominator_positive randomBits
  unfold far at distant
  unfold close at near
  omega

theorem identical_samplers_not_far (sampler : Sampler) (input : Word) (randomBits : Nat) :
    ¬ far sampler sampler input randomBits := by
  intro distant
  exact far_close_disjoint sampler sampler input randomBits
    ⟨distant, identical_samplers_close sampler input randomBits⟩

/-- A concrete sampler whose distribution is concentrated on the empty word. -/
def emptySampler : Sampler :=
  { machine := Transducers.zeroTransducer
    runtime := []
    halts := fun _ => rfl }

/-- A concrete sampler concentrated on the two-bit word `01`. -/
def distinctSampler : Sampler :=
  { machine := Transducers.oneTransducer
    runtime := [2]
    halts := fun _ => rfl }

theorem distinct_point_masses_have_distance_one (input : Word) :
    totalVariationFraction emptySampler distinctSampler input 0 = (2, 2) := by
  rfl

theorem duplicate_outcomes_retain_mass :
    countDifferenceSum [[], []] [[true], [true]]
      (outcomeSupport [[], []] [[true], [true]]) = 4 := by
  rfl

end InclusionBench.Statistical
