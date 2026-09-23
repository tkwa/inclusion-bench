import ProofAudit
import ProjectRoot

open Lean InclusionProofcheck

namespace ProofProjectTests

def check (condition : Bool) (message : String) : IO Unit :=
  unless condition do throw (IO.userError message)

def unwrap (value : Except String α) : IO α :=
  match value with | .ok value => pure value | .error message => throw (IO.userError message)

def replay (payload : Json) (target : Name) (requested := false) (extraImports := false) : IO Json := do
  IO.FS.writeFile "project-payload.json" payload.compress
  IO.FS.writeFile "project-targets.json" <| (toJson #[Json.mkObj [
    ("theorem", toJson target.toString),
    ("expected", toJson "InclusionBench.TrustedBaseline.expected_0")]]).compress
  IO.FS.writeFile "project-literature.json" <| (Json.mkObj [("requests", .arr
    (if requested then #[Json.mkObj [("name", toJson "Literature.module_fact")]] else #[]))]).compress
  runAudit "project-payload.json" "project-targets.json" (some "project-literature.json") extraImports

def run (env : Environment) : IO Unit := do
  let modules : NameSet := ({} : NameSet).insert `ProjectImported |>.insert `ProjectRoot
  let payload ← unwrap (exportDeclarationRoots env #[`ProjectSubmission.valid] modules)
  let report ← replay payload `ProjectSubmission.valid
  check ((← unwrap (report.getObjValAs? String "status")) == "verified") "Imported dependency failed replay"
  check ((← unwrap (report.getObjValAs? Nat "declaration_count")) == 3) "Wrong imported declaration closure"
  let direct ← unwrap (exportDeclarationRoots env #[`ProjectLibrary.helper] modules)
  let directReport ← replay direct `ProjectLibrary.helper
  check ((← unwrap (directReport.getObjValAs? Nat "declaration_count")) == 2) "Imported target omitted"
  check (!(exportDeclarationRoots env #[`ProjectSubmission.forged] modules).isOk) "Imported forbidden axiom accepted"
  check (!(exportDeclarationRoots env #[`ProjectLibrary.unused] modules).isOk) "Imported unsafe definition accepted"
  let conditional ← unwrap (exportDeclarationRoots env #[`ProjectSubmission.conditional] modules)
  let unrequested ← try let _ ← replay conditional `ProjectSubmission.conditional; pure false catch _ => pure true
  check unrequested "Unrequested imported axiom accepted"
  let pending ← replay conditional `ProjectSubmission.conditional true
  check ((← unwrap (pending.getObjValAs? String "status")) == "needs_literature_review") "Imported literature became verified"
  let dependencies ← unwrap ((← unwrap (pending.getObjVal? "literature_dependencies")).getArr?)
  let context ← unwrap ((← unwrap (dependencies[0]!.getObjVal? "context")).getArr?)
  check (context.size == 1) "Imported local type definition missing from literature context"
  let external ← unwrap (exportDeclarationRoots env #[`ProjectSubmission.external] modules)
  let absent ← try let _ ← replay external `ProjectSubmission.external; pure false catch _ => pure true
  check absent "Unexpected external declaration in initial baseline"
  let hydrated ← replay external `ProjectSubmission.external false true
  check ((← unwrap (hydrated.getObjValAs? String "status")) == "verified") "Trusted extra imports absent from fresh environment"
  IO.println "Project export tests passed"

end ProofProjectTests

run_cmd Lean.Elab.Command.liftIO <| ProofProjectTests.run (← getEnv)
