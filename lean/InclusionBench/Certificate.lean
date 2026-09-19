import InclusionBench.Derivation
import Lean

namespace InclusionBench

deriving instance Lean.ToJson, Lean.FromJson for Fact
deriving instance Lean.ToJson, Lean.FromJson for Rule

/-- A JSON-serializable topologically ordered proof DAG. Referenced baseline
facts and rules are checked by value against the pinned lists. -/
inductive CertificateStep (C : Type) where
  | baseline (fact : Fact C)
  | submitted (fact : Fact C)
  | applyRule (rule : Rule C)
  deriving Repr, Lean.ToJson, Lean.FromJson

def CertificateStep.evaluate {C : Type} [DecidableEq C]
    (baseline submitted : List (Fact C)) (rules : List (Rule C))
    (known : List (Fact C)) : CertificateStep C → Option (Fact C)
  | .baseline f => if f ∈ baseline then some f else none
  | .submitted f => if f ∈ submitted then some f else none
  | .applyRule r =>
      if r ∈ rules ∧ r.premises.all (fun f => decide (f ∈ known)) then
        some r.conclusion
      else none

theorem certificateStep_sound {C : Type} [DecidableEq C] (model : Interpretation C)
    (baseline submitted : List (Fact C)) (rules : List (Rule C))
    (known : List (Fact C)) (step : CertificateStep C)
    (hb : ∀ f ∈ baseline, f.Holds model)
    (hs : ∀ f ∈ submitted, f.Holds model)
    (hr : ∀ r ∈ rules, r.Sound model)
    (hk : ∀ f ∈ known, f.Holds model)
    {result : Fact C}
    (success : step.evaluate baseline submitted rules known = some result) :
    result.Holds model := by
  cases step with
  | baseline f =>
      simp only [CertificateStep.evaluate] at success
      split at success
      · cases success
        exact hb result (by assumption)
      · contradiction
  | submitted f =>
      simp only [CertificateStep.evaluate] at success
      split at success
      · cases success
        exact hs result (by assumption)
      · contradiction
  | applyRule r =>
      simp only [CertificateStep.evaluate] at success
      split at success
      · next conditions =>
        cases success
        apply hr r conditions.1
        intro f hf
        apply hk f
        have allKnown := List.all_eq_true.mp conditions.2
        simpa using allKnown f hf
      · contradiction

def checkCertificate {C : Type} [DecidableEq C]
    (baseline submitted : List (Fact C)) (rules : List (Rule C)) :
    List (CertificateStep C) → List (Fact C) → Option (List (Fact C))
  | [], known => some known
  | step :: rest, known => do
      let f ← step.evaluate baseline submitted rules known
      checkCertificate baseline submitted rules rest (f :: known)

theorem checkCertificate_sound {C : Type} [DecidableEq C] (model : Interpretation C)
    (baseline submitted : List (Fact C)) (rules : List (Rule C))
    (certificate : List (CertificateStep C))
    (hb : ∀ f ∈ baseline, f.Holds model)
    (hs : ∀ f ∈ submitted, f.Holds model)
    (hr : ∀ r ∈ rules, r.Sound model)
    (known : List (Fact C)) (hk : ∀ f ∈ known, f.Holds model)
    {result : List (Fact C)}
    (success : checkCertificate baseline submitted rules certificate known = some result) :
    ∀ f ∈ result, f.Holds model := by
  induction certificate generalizing known with
  | nil =>
      simp only [checkCertificate, Option.some.injEq] at success
      subst result
      exact hk
  | cons step rest ih =>
      cases he : step.evaluate baseline submitted rules known with
      | none => simp [checkCertificate, he] at success
      | some f =>
          have hf := certificateStep_sound model baseline submitted rules known step hb hs hr hk he
          apply ih (f :: known)
          · intro g hg
            cases List.mem_cons.mp hg with
            | inl eq => simpa only [eq] using hf
            | inr old => exact hk g old
          · simpa [checkCertificate, he] using success

end InclusionBench
