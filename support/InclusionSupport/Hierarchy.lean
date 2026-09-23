import InclusionSupport.Counting
import InclusionBench.CountingHierarchy

/-!
Kernel-proved oracle and finite-hierarchy interfaces. This module introduces
no axioms. A CH containment proof can provide its mathematical base cases and
closure step without constructing or destructuring an oracle machine.
-/

namespace InclusionBench.Support

open Machines Counting Oracles CountingHierarchy

theorem pOracle_mono {small large : ComplexityClass} (included : Includes small large) :
    Includes (POracle small) (POracle large) := by
  rintro language ⟨oracle, member, computation⟩
  exact ⟨oracle, included oracle member, computation⟩

theorem npOracle_mono {small large : ComplexityClass} (included : Includes small large) :
    Includes (NPOracle small) (NPOracle large) := by
  rintro language ⟨oracle, member, computation⟩
  exact ⟨oracle, included oracle member, computation⟩

theorem ppOracle_mono {small large : ComplexityClass} (included : Includes small large) :
    Includes (PPOracle small) (PPOracle large) := ppOracle_monotone included

theorem pOracle_iff {oracleClass : ComplexityClass} {language : Language} :
    POracle oracleClass language ↔
      ∃ oracle, oracleClass oracle ∧ deterministicPolynomialWith oracle language := Iff.rfl

theorem npOracle_iff {oracleClass : ComplexityClass} {language : Language} :
    NPOracle oracleClass language ↔
      ∃ oracle, oracleClass oracle ∧ nondeterministicPolynomialWith oracle language := Iff.rfl

theorem ppOracle_iff {oracleClass : ComplexityClass} {language : Language} :
    PPOracle oracleClass language ↔
      ∃ oracle, oracleClass oracle ∧ PPWith oracle language := Iff.rfl

theorem pOracle_intro {oracleClass : ComplexityClass} {oracle language : Language}
    (member : oracleClass oracle) (computation : deterministicPolynomialWith oracle language) :
    POracle oracleClass language := ⟨oracle, member, computation⟩

theorem npOracle_intro {oracleClass : ComplexityClass} {oracle language : Language}
    (member : oracleClass oracle) (computation : nondeterministicPolynomialWith oracle language) :
    NPOracle oracleClass language := ⟨oracle, member, computation⟩

theorem ppOracle_intro {oracleClass : ComplexityClass} {oracle language : Language}
    (member : oracleClass oracle) (computation : PPWith oracle language) :
    PPOracle oracleClass language := ⟨oracle, member, computation⟩

theorem ch_iff_level {language : Language} :
    CH language ↔ ∃ level, countingLevel level language := Iff.rfl

theorem ch_intro {language : Language} (level : Nat) (member : countingLevel level language) :
    CH language := ⟨level, member⟩

theorem ph_iff_level {language : Language} :
    PH language ↔ ∃ level, sigmaLevel level language := Iff.rfl

theorem ph_intro {language : Language} (level : Nat) (member : sigmaLevel level language) :
    PH language := ⟨level, member⟩

theorem ch_of_pp {language : Language} (member : PP language) : CH language := ch_intro 1 member

theorem ch_of_p {language : Language} (member : polynomialTime language) : CH language :=
  ch_intro 0 member

theorem ch_of_fixed_pp_oracle {oracle language : Language} (level : Nat)
    (member : countingLevel (level + 1) oracle) (computation : PPWith oracle language) :
    CH language := ch_intro (level + 2) (ppOracle_intro member computation)

theorem pSharpP_iff {language : Language} :
    PSharpP language ↔ ∃ oracle, PP oracle ∧ deterministicPolynomialWith oracle language := Iff.rfl

theorem pSharpP_intro {oracle language : Language} (member : PP oracle)
    (computation : deterministicPolynomialWith oracle language) : PSharpP language :=
  pOracle_intro member computation

/-- A fixed class containing P and PP and closed under its PP oracle operator
contains every finite counting-hierarchy level. No relativization is inferred. -/
theorem ch_in_of_ppOracle_closed {target : ComplexityClass}
    (baseP : Includes polynomialTime target) (basePP : Includes PP target)
    (closed : Includes (PPOracle target) target) : Includes CH target := by
  let rec levelIncluded : (level : Nat) → Includes (countingLevel level) target
    | 0 => baseP
    | 1 => basePP
    | level + 2 => includes_trans (ppOracle_mono (levelIncluded (level + 1))) closed
  rintro language ⟨level, member⟩
  exact levelIncluded level language member

/-- The analogous induction interface for the polynomial hierarchy. -/
theorem ph_in_of_npOracle_closed {target : ComplexityClass}
    (baseP : Includes polynomialTime target) (baseNP : Includes nondeterministicPolynomialTime target)
    (closed : Includes (NPOracle target) target) : Includes PH target := by
  let rec levelIncluded : (level : Nat) → Includes (sigmaLevel level) target
    | 0 => baseP
    | 1 => baseNP
    | level + 2 => includes_trans (npOracle_mono (levelIncluded (level + 1))) closed
  rintro language ⟨level, member⟩
  exact levelIncluded level language member

theorem class_in_ch_of_level {source : ComplexityClass} (level : Nat)
    (included : Includes source (countingLevel level)) : Includes source CH :=
  includes_trans included (level_in_ch level)

end InclusionBench.Support
