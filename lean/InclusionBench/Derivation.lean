import InclusionBench.Semantics

namespace InclusionBench

/-- Independence is deliberately absent from ordinary mathematical facts. -/
inductive Fact (ClassId : Type) where
  | inclusion (left right : ClassId)
  | noninclusion (left right : ClassId)
  deriving DecidableEq, Repr

def Fact.Holds {C : Type} (model : Interpretation C) : Fact C → Prop
  | .inclusion a b => Includes (model a) (model b)
  | .noninclusion a b => NonIncludes (model a) (model b)

def Fact.flip {C : Type} : Fact C → Fact C
  | .inclusion a b => .noninclusion a b
  | .noninclusion a b => .inclusion a b

theorem Fact.holds_flip_iff {C : Type} (model : Interpretation C) (fact : Fact C) :
    fact.flip.Holds model ↔ ¬ fact.Holds model := by
  classical
  cases fact with
  | inclusion a b => rfl
  | noninclusion a b => exact Classical.not_not.symm

structure Rule (ClassId : Type) where
  premises : List (Fact ClassId)
  conclusion : Fact ClassId
  deriving DecidableEq, Repr

def Rule.Sound {C : Type} (model : Interpretation C) (rule : Rule C) : Prop :=
  (∀ f ∈ rule.premises, f.Holds model) → rule.conclusion.Holds model

/-- The general Horn contrapositive: refuting the conclusion while proving
all other premises refutes the remaining premise. -/
theorem horn_contrapositive {C : Type} (model : Interpretation C)
    (rule : Rule C) (ruleSound : rule.Sound model) (target : Fact C)
    (otherPremises : ∀ f ∈ rule.premises, f ≠ target → f.Holds model)
    (conclusionFalse : rule.conclusion.flip.Holds model) : target.flip.Holds model := by
  classical
  apply (Fact.holds_flip_iff model target).mpr
  intro targetTrue
  apply (Fact.holds_flip_iff model rule.conclusion).mp conclusionFalse
  apply ruleSound
  intro f hf
  by_cases same : f = target
  · simpa only [same] using targetTrue
  · exact otherPremises f hf same

/-- A finite proof tree whose leaves name trusted or submitted statements.
The tree can be serialized; leaf membership and rule application must still
be checked. `derivation_sound` exposes every semantic trust hypothesis. -/
inductive Derives {C : Type} (baseline submitted : List (Fact C))
    (rules : List (Rule C)) : Fact C → Prop where
  | baseline (f) : f ∈ baseline → Derives baseline submitted rules f
  | submitted (f) : f ∈ submitted → Derives baseline submitted rules f
  | applyRule (r) : r ∈ rules →
      (∀ f ∈ r.premises, Derives baseline submitted rules f) →
      Derives baseline submitted rules r.conclusion

theorem derivation_sound {C : Type} (model : Interpretation C)
    {baseline submitted : List (Fact C)} {rules : List (Rule C)}
    (baselineSound : ∀ f ∈ baseline, f.Holds model)
    (submittedSound : ∀ f ∈ submitted, f.Holds model)
    (rulesSound : ∀ r ∈ rules, r.Sound model)
    {f : Fact C} (proof : Derives baseline submitted rules f) : f.Holds model := by
  induction proof with
  | baseline f hf => exact baselineSound f hf
  | submitted f hf => exact submittedSound f hf
  | applyRule r hr _ ih => exact rulesSound r hr ih

def transitivityRule {C : Type} (a b c : C) : Rule C :=
  ⟨[.inclusion a b, .inclusion b c], .inclusion a c⟩

theorem transitivityRule_sound {C : Type} (model : Interpretation C) (a b c : C) :
    (transitivityRule a b c).Sound model := by
  intro h
  exact includes_trans (h (.inclusion a b) (by simp [transitivityRule]))
    (h (.inclusion b c) (by simp [transitivityRule]))

def separationRule {C : Type} (a b c d : C) : Rule C :=
  ⟨[.noninclusion a b, .inclusion a c, .inclusion d b], .noninclusion c d⟩

theorem separationRule_sound {C : Type} (model : Interpretation C) (a b c d : C) :
    (separationRule a b c d).Sound model := by
  intro h
  exact nonincludes_expand (h (.noninclusion a b) (by simp [separationRule]))
    (h (.inclusion a c) (by simp [separationRule]))
    (h (.inclusion d b) (by simp [separationRule]))

def complementInclusionRule {C : Type} (a b ca cb : C) : Rule C :=
  ⟨[.inclusion a b], .inclusion ca cb⟩

theorem complementInclusionRule_sound {C : Type} (model : Interpretation C)
    (a b ca cb : C) (ha : model ca = coClass (model a))
    (hb : model cb = coClass (model b)) :
    (complementInclusionRule a b ca cb).Sound model := by
  intro h
  have ih := includes_complement (h (.inclusion a b) (by simp [complementInclusionRule]))
  simpa only [Fact.Holds, complementInclusionRule, ha, hb] using ih

def complementNoninclusionRule {C : Type} (a b ca cb : C) : Rule C :=
  ⟨[.noninclusion a b], .noninclusion ca cb⟩

theorem complementNoninclusionRule_sound {C : Type} (model : Interpretation C)
    (a b ca cb : C) (ha : model ca = coClass (model a))
    (hb : model cb = coClass (model b)) :
    (complementNoninclusionRule a b ca cb).Sound model := by
  intro h
  have ih := nonincludes_complement (h (.noninclusion a b) (by simp [complementNoninclusionRule]))
  simpa only [Fact.Holds, complementNoninclusionRule, ha, hb] using ih

/-- Under sound assumptions a derivation cannot prove both polarities. -/
theorem no_contradictory_derivations {C : Type} (model : Interpretation C)
    {baseline submitted : List (Fact C)} {rules : List (Rule C)}
    (hb : ∀ f ∈ baseline, f.Holds model)
    (hs : ∀ f ∈ submitted, f.Holds model)
    (hr : ∀ r ∈ rules, r.Sound model) (a b : C)
    (positive : Derives baseline submitted rules (.inclusion a b))
    (negative : Derives baseline submitted rules (.noninclusion a b)) : False :=
  derivation_sound model hb hs hr negative (derivation_sound model hb hs hr positive)

end InclusionBench
