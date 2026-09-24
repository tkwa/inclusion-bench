"""Generate compact source for resource-bounded large-export integration tests.

The proof is reflexivity. Distinct string definitions and retained let bindings
make the export genuinely large while keeping kernel reduction inexpensive.
Run large configurations only in the verifier's bounded container.
"""


def large_export_source(count=129, literal_bytes=256 * 1024, *, literature=False):
    if type(count) is not int or type(literal_bytes) is not int or not (1 <= count <= 2048) or not (1 <= literal_bytes <= 1024 * 1024):
        raise ValueError("Invalid large-export fixture dimensions")
    assumptions = '''  let proposition := Declaration.defnDecl {
    name := `LargeExportProposition, levelParams := [], type := .sort .zero,
    value := proof, hints := .regular 0, safety := .safe }
  match env.addDeclCore 1000000000 proposition none true with
  | .error _ => throwError "Large fixture proposition was not kernel-valid"
  | .ok next => env := next
  let assumption := Declaration.axiomDecl {
    name := `Literature.large, levelParams := [],
    type := mkConst `LargeExportProposition, isUnsafe := false }
  match env.addDeclCore 1000000000 assumption none true with
  | .error _ => throwError "Large fixture literature statement was not kernel-valid"
  | .ok next => env := next
  proof := mkConst `Literature.large
''' if literature else ""
    return f'''import TrustedBaseline
import Lean

open Lean Elab Command
open InclusionBench InclusionBench.Support InclusionBench.Support.Classes

set_option maxRecDepth 100000
set_option maxHeartbeats 0

theorem largeExportSeed : Includes P P := includes_refl _

run_cmd do
  let mut env ← getEnv
  let some seed := env.find? `largeExportSeed | throwError "Missing seed"
  let padding := String.mk (List.replicate {literal_bytes} 'x')
  let mut proof := {"seed.type" if literature else "mkConst `largeExportSeed"}
  for index in [:{count}] do
    let name := Name.num `LargeExportString index
    let value := Expr.lit (.strVal (toString index ++ ":" ++ padding))
    let declaration := Declaration.defnDecl {{
      name, levelParams := [], type := mkConst ``String, value,
      hints := .regular 0, safety := .safe }}
    match env.addDeclCore 1000000000 declaration none true with
    | .error _ => throwError "Large fixture definition was not kernel-valid"
    | .ok next => env := next
    proof := .letE .anonymous (mkConst ``String) (mkConst name) proof false
{assumptions}  let declaration := Declaration.thmDecl {{
    name := `submitted, levelParams := [], type := seed.type, value := proof }}
  match env.addDeclCore 1000000000 declaration none true with
  | .error _ => throwError "Large fixture theorem was not kernel-valid"
  | .ok next => setEnv next
'''


def large_literature_export_source(count=129, literal_bytes=256 * 1024):
    """Put the large dependency closure in an exact literature-review context."""
    return large_export_source(count, literal_bytes, literature=True)
