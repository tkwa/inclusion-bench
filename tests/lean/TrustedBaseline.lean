import Lean

/- Minimal baseline for standalone audit regression tests. Production uses
the generated, dataset-bound TrustedBaseline module instead. -/
namespace InclusionBench.TrustedBaseline

def allowedAxiomNames : List String := ["propext", "Classical.choice", "Quot.sound"]
def expected_0 : Prop := True

end InclusionBench.TrustedBaseline
