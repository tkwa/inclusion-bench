import InclusionSupport.Counting
import InclusionSupport.Hierarchy

set_option warningAsError true

open InclusionBench InclusionBench.Support
open InclusionBench.Counting InclusionBench.CountingHierarchy

/- These fixtures exercise textbook proof patterns. Hypotheses stay explicit;
none is a new benchmark claim or a new trusted assumption. -/

example {f g : Word → Int} (hf : GapP f) (hg : GapP g) :
    GapP (fun word => (f word * g word - 17) ^ 3) :=
  gapP_pow (gapP_sub (gapP_mul hf hg) (gapP_int 17)) 3

example : SharpP (fun _ => 19) := sharpP_nat 19

example : GapP (fun _ => (-27 : Int)) := gapP_int (-27)

example {language : Language} (member : SPP language) :
    GapP (characteristic language) := (spp_iff_characteristic _).mp member

example {first second : Language} (hf : SPP first) (hs : SPP second) :
    SPP (fun word => first word ∧ ¬ second word) :=
  spp_intersection hf (spp_complement hs)

example {first second : Language} (hf : SPP first) (hs : SPP second) :
    SPP (fun word => first word ∨ second word) := spp_union hf hs

example {language : Language} (member : PP language) :
    PP (complementLanguage language) := pp_complement member

example {language : Language} {preprocess : Word → Word}
    (member : SPP language) (computable : RealSyntax.PolynomialTimeComputable preprocess) :
    SPP (fun word => language (preprocess word)) := spp_precompose member computable

example {f : Word → Int} (hf : GapP f) :
    GapP (fun word => ((Randomized.coinStrings (polynomialValue [1, 1] word.length)).map
      (fun bits => f (ProofSystems.encodeTriple word bits []))).sum) :=
  gapP_sum_bits hf [1, 1]

example {f : Word → Int} (hf : GapP f) :
    GapP (fun word => ((List.range (polynomialValue [2, 0, 1] word.length)).map
      (fun index => f (ProofSystems.encodeTriple word (Transducers.unary index) []))).foldr (· * ·) 1) :=
  gapP_product_range hf [2, 0, 1]

-- The empty product is one; the zero-bit sum has one index, not zero indices.
example {f : Word → Int} (hf : GapP f) : GapP (fun _ => 1) := by
  simpa [polynomialValue] using gapP_product_range hf []

example {f : Word → Int} (hf : GapP f) :
    GapP (fun word => f (ProofSystems.encodeTriple word [] [])) := by
  simpa [polynomialValue, Randomized.coinStrings] using gapP_sum_bits hf []

-- A counting-hierarchy target reduces to an algebraic sign condition.
theorem hierarchy_from_gap_algebra {language : Language} {f g : Word → Int}
    (hf : GapP f) (hg : GapP g)
    (correct : ∀ word, language word ↔ 0 < f word * g word - 5) : CH language :=
  ch_of_pp (pp_of_gap (gapP_sub (gapP_mul hf hg) (gapP_int 5)) correct)

example : Includes SPP CH := class_in_ch_of_level 1 Counting.spp_in_pp

example {target : ComplexityClass} (baseP : Includes Machines.polynomialTime target)
    (basePP : Includes PP target) (closed : Includes (PPOracle target) target) :
    Includes CH target := ch_in_of_ppOracle_closed baseP basePP closed

example {small large : ComplexityClass} (included : Includes small large) :
    Includes (Oracles.POracle small) (Oracles.POracle large) := pOracle_mono included

#print axioms InclusionBench.Support.spp_intersection
#print axioms InclusionBench.Support.pp_complement
#print axioms InclusionBench.Support.ch_in_of_ppOracle_closed
