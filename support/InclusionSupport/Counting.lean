import InclusionBench.Counting
import InclusionBench.Transducers
import InclusionBench.RealSyntax
import InclusionBench.ProofSystems

/-!
Textbook counting interfaces over the benchmark's exact machine definitions.

The six declarations in `Literature` are explicit existing-result imports.
Their statements, source locators and model alignment are recorded in
`support/registry-counting.json`. Everything outside that namespace is a
kernel-checked consequence. In particular, no submitted result becomes an
assumption, and no unrelativized theorem is silently relativized.
-/

namespace InclusionBench.Support

open Counting Transducers RealSyntax

namespace Literature

/-- FFK, section 3, the #P closure discussion and Corollary 3.6. -/
axiom sharpP_add {f g : Word → Nat} (hf : SharpP f) (hg : SharpP g) :
  SharpP (fun word => f word + g word)

/-- FFK, section 3, closure property 4 and the #P closure discussion. -/
axiom sharpP_mul {f g : Word → Nat} (hf : SharpP f) (hg : SharpP g) :
  SharpP (fun word => f word * g word)

/-- The preprocessing function is total polynomial time, not arbitrary. -/
axiom sharpP_precompose {f : Word → Nat} {preprocess : Word → Word}
    (hf : SharpP f) (hp : PolynomialTimeComputable preprocess) :
  SharpP (fun word => f (preprocess word))

/-- Binary integer output may be signed; this is the integer FP-to-GapP bridge. -/
axiom gapP_of_fp {f : Word → Int} (hf : FP f) : GapP f

/-- One uniform GapP function receives the input and a polynomial-length
binary index. Summation has exponentially many terms, implemented by guessing
the index. This is not closure under an arbitrary family of GapP functions. -/
axiom gapP_sum_bits {f : Word → Int} (hf : GapP f) (length : List Nat) :
  GapP (fun word => ((Randomized.coinStrings (polynomialValue length word.length)).map
    (fun bits => f (ProofSystems.encodeTriple word bits []))).sum)

/-- Only polynomially many factors are permitted. The index is unary and
the same uniform GapP machine handles every input/index pair. -/
axiom gapP_product_range {f : Word → Int} (hf : GapP f) (bound : List Nat) :
  GapP (fun word => ((List.range (polynomialValue bound word.length)).map
    (fun index => f (ProofSystems.encodeTriple word (unary index) []))).foldr (· * ·) 1)

end Literature

theorem sharpP_congr {f g : Word → Nat} (hf : SharpP f)
    (same : ∀ word, f word = g word) : SharpP g := by
  have eq : f = g := funext same
  simpa only [← eq] using hf

theorem gapP_congr {f g : Word → Int} (hf : GapP f)
    (same : ∀ word, f word = g word) : GapP g := by
  have eq : f = g := funext same
  simpa only [← eq] using hf

theorem sharpP_add {f g : Word → Nat} (hf : SharpP f) (hg : SharpP g) :
    SharpP (fun word => f word + g word) := Literature.sharpP_add hf hg

theorem sharpP_mul {f g : Word → Nat} (hf : SharpP f) (hg : SharpP g) :
    SharpP (fun word => f word * g word) := Literature.sharpP_mul hf hg

theorem sharpP_nat (value : Nat) : SharpP (fun _ => value) := by
  induction value with
  | zero => exact Counting.sharpP_zero
  | succ value ih => exact sharpP_add ih Counting.sharpP_one

theorem gapP_of_sharpP {f : Word → Nat} (hf : SharpP f) :
    GapP (fun word => (f word : Int)) := by
  refine ⟨f, fun _ => 0, hf, Counting.sharpP_zero, ?_⟩
  intro word
  simp

theorem gapP_zero : GapP (fun _ => 0) := gapP_of_sharpP Counting.sharpP_zero

theorem gapP_one : GapP (fun _ => 1) := gapP_of_sharpP Counting.sharpP_one

theorem gapP_neg {f : Word → Int} (hf : GapP f) :
    GapP (fun word => -f word) := Counting.gapP_negation hf

theorem gapP_nat (value : Nat) : GapP (fun _ => (value : Int)) :=
  gapP_of_sharpP (sharpP_nat value)

theorem gapP_int (value : Int) : GapP (fun _ => value) := by
  cases value with
  | ofNat value => exact gapP_nat value
  | negSucc value => exact gapP_neg (gapP_nat (value + 1))

theorem gapP_add {f g : Word → Int} (hf : GapP f) (hg : GapP g) :
    GapP (fun word => f word + g word) := by
  obtain ⟨fp, fn, hfp, hfn, ef⟩ := hf
  obtain ⟨gp, gn, hgp, hgn, eg⟩ := hg
  refine ⟨fun word => fp word + gp word, fun word => fn word + gn word,
    sharpP_add hfp hgp, sharpP_add hfn hgn, ?_⟩
  intro word
  simp only [ef word, eg word, Int.natCast_add]
  omega

theorem gapP_sub {f g : Word → Int} (hf : GapP f) (hg : GapP g) :
    GapP (fun word => f word - g word) := by
  simpa only [Int.sub_eq_add_neg] using gapP_add hf (gapP_neg hg)

theorem gapP_mul {f g : Word → Int} (hf : GapP f) (hg : GapP g) :
    GapP (fun word => f word * g word) := by
  obtain ⟨fp, fn, hfp, hfn, ef⟩ := hf
  obtain ⟨gp, gn, hgp, hgn, eg⟩ := hg
  refine ⟨fun word => fp word * gp word + fn word * gn word,
    fun word => fp word * gn word + fn word * gp word,
    sharpP_add (sharpP_mul hfp hgp) (sharpP_mul hfn hgn),
    sharpP_add (sharpP_mul hfp hgn) (sharpP_mul hfn hgp), ?_⟩
  intro word
  simp only [ef word, eg word, Int.natCast_add, Int.natCast_mul, Int.sub_mul, Int.mul_sub]
  omega

theorem gapP_pow {f : Word → Int} (hf : GapP f) (power : Nat) :
    GapP (fun word => f word ^ power) := by
  induction power with
  | zero => simpa using gapP_one
  | succ power ih => simpa only [Int.pow_succ] using gapP_mul ih hf

theorem sharpP_precompose {f : Word → Nat} {preprocess : Word → Word}
    (hf : SharpP f) (hp : PolynomialTimeComputable preprocess) :
    SharpP (fun word => f (preprocess word)) := Literature.sharpP_precompose hf hp

theorem gapP_precompose {f : Word → Int} {preprocess : Word → Word}
    (hf : GapP f) (hp : PolynomialTimeComputable preprocess) :
    GapP (fun word => f (preprocess word)) := by
  obtain ⟨positive, negative, hpositive, hnegative, correct⟩ := hf
  exact ⟨fun word => positive (preprocess word), fun word => negative (preprocess word),
    sharpP_precompose hpositive hp, sharpP_precompose hnegative hp,
    fun word => correct (preprocess word)⟩

theorem gapP_of_fp {f : Word → Int} (hf : FP f) : GapP f := Literature.gapP_of_fp hf

theorem gapP_sum_bits {f : Word → Int} (hf : GapP f) (length : List Nat) :
    GapP (fun word => ((Randomized.coinStrings (polynomialValue length word.length)).map
      (fun bits => f (ProofSystems.encodeTriple word bits []))).sum) :=
  Literature.gapP_sum_bits hf length

theorem gapP_product_range {f : Word → Int} (hf : GapP f) (bound : List Nat) :
    GapP (fun word => ((List.range (polynomialValue bound word.length)).map
      (fun index => f (ProofSystems.encodeTriple word (unary index) []))).foldr (· * ·) 1) :=
  Literature.gapP_product_range hf bound

/-- Integer characteristic functions expose SPP without path-count witnesses. -/
noncomputable def characteristic (language : Language) (word : Word) : Int := by
  classical
  exact if language word then 1 else 0

theorem spp_iff_characteristic (language : Language) :
    SPP language ↔ GapP (characteristic language) := by
  classical
  constructor
  · rintro ⟨gap, hgap, correct⟩
    apply gapP_congr hgap
    intro word
    by_cases member : language word
    · simp [characteristic, member, (correct word).1 member]
    · simp [characteristic, member, (correct word).2 member]
  · intro computable
    refine ⟨characteristic language, computable, ?_⟩
    intro word
    exact ⟨fun member => by simp [characteristic, member],
      fun outside => by simp [characteristic, outside]⟩

theorem spp_complement {language : Language} (member : SPP language) :
    SPP (complementLanguage language) := by
  classical
  apply (spp_iff_characteristic _).mpr
  apply gapP_congr (gapP_sub gapP_one ((spp_iff_characteristic _).mp member))
  intro word
  by_cases h : language word <;> simp [characteristic, complementLanguage, h]

theorem spp_intersection {first second : Language} (hf : SPP first) (hs : SPP second) :
    SPP (fun word => first word ∧ second word) := by
  classical
  apply (spp_iff_characteristic _).mpr
  apply gapP_congr (gapP_mul ((spp_iff_characteristic _).mp hf)
    ((spp_iff_characteristic _).mp hs))
  intro word
  by_cases hfirst : first word <;> by_cases hsecond : second word <;>
    simp [characteristic, hfirst, hsecond]

theorem spp_union {first second : Language} (hf : SPP first) (hs : SPP second) :
    SPP (fun word => first word ∨ second word) := by
  classical
  have h := spp_complement (spp_intersection (spp_complement hf) (spp_complement hs))
  have same : complementLanguage (fun word =>
      complementLanguage first word ∧ complementLanguage second word) =
      (fun word => first word ∨ second word) := by
    funext word
    by_cases hfirst : first word <;> by_cases hsecond : second word <;>
      simp [complementLanguage, hfirst, hsecond]
  exact same ▸ h

theorem spp_precompose {language : Language} {preprocess : Word → Word}
    (member : SPP language) (hp : PolynomialTimeComputable preprocess) :
    SPP (fun word => language (preprocess word)) := by
  obtain ⟨gap, hgap, correct⟩ := member
  exact ⟨fun word => gap (preprocess word), gapP_precompose hgap hp,
    fun word => correct (preprocess word)⟩

theorem pp_of_gap {language : Language} {gap : Word → Int} (hgap : GapP gap)
    (correct : ∀ word, language word ↔ 0 < gap word) : PP language :=
  ⟨gap, hgap, correct⟩

theorem ceqp_of_gap {language : Language} {gap : Word → Int} (hgap : GapP gap)
    (correct : ∀ word, language word ↔ gap word = 0) : CeqP language :=
  ⟨gap, hgap, correct⟩

theorem pp_complement {language : Language} (member : PP language) :
    PP (complementLanguage language) := by
  obtain ⟨gap, hgap, correct⟩ := member
  refine ⟨fun word => 1 - gap word, gapP_sub gapP_one hgap, ?_⟩
  intro word
  change (¬ language word) ↔ 0 < 1 - gap word
  rw [correct word]
  omega

theorem pp_precompose {language : Language} {preprocess : Word → Word}
    (member : PP language) (hp : PolynomialTimeComputable preprocess) :
    PP (fun word => language (preprocess word)) := by
  obtain ⟨gap, hgap, correct⟩ := member
  exact ⟨fun word => gap (preprocess word), gapP_precompose hgap hp,
    fun word => correct (preprocess word)⟩

theorem ceqp_precompose {language : Language} {preprocess : Word → Word}
    (member : CeqP language) (hp : PolynomialTimeComputable preprocess) :
    CeqP (fun word => language (preprocess word)) := by
  obtain ⟨gap, hgap, correct⟩ := member
  exact ⟨fun word => gap (preprocess word), gapP_precompose hgap hp,
    fun word => correct (preprocess word)⟩

end InclusionBench.Support
