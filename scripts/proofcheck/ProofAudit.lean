import ProofExport
import TrustedBaseline

open Lean InclusionProofcheck

def auditFailure (message : String) : IO α := throw (IO.userError message)

def parseOrFail (value : Except String α) : IO α :=
  match value with | .ok value => pure value | .error error => auditFailure error

def addChecked (env : Environment) (declaration : Declaration) : IO Environment :=
  match env.addDeclCore 1000000000 declaration none true with
  | .ok next => pure next
  | .error error => do
      let message ← (error.toMessageData {}).toString
      auditFailure s!"Kernel rejected declaration: {message}"

def actualAxioms (env : Environment) (name : Name) : Array Name :=
  (((CollectAxioms.collect name).run env).run {}).2.axioms

def runAudit (payloadPath targetsPath : System.FilePath) : IO Json := do
  let payload ← parseOrFail (Json.parse (← IO.FS.readFile payloadPath))
  let targets ← parseOrFail (Json.parse (← IO.FS.readFile targetsPath))
  let version ← parseOrFail (payload.getObjValAs? Nat "schema_version")
  if version != 1 && version != 2 then auditFailure "Unknown proof export version"
  let declarations ← parseOrFail ((← parseOrFail (payload.getObjVal? "declarations")).getArr?)
  if declarations.size > 100000 then auditFailure "Too many declarations"
  let mut env ← importModules #[{module := `TrustedBaseline}, {module := `ProofExport}] {}
  let allowed := InclusionBench.TrustedBaseline.allowedAxiomNames
  let mut newNames : Array Name := #[]
  for json in declarations do
    let declaration ← parseOrFail (if version == 1 then decodeDeclaration json else decodeDeclarationV2 json)
    for name in declaration.getNames do
      if env.contains name then auditFailure s!"Attempt to replace trusted declaration: {name}"
      if "InclusionBench.TrustedBaseline".isPrefixOf name.toString then
        auditFailure "Reserved baseline namespace"
      newNames := newNames.push name
    env ← addChecked env declaration
  -- Audit every reconstructed declaration, including unused helpers.
  for name in newNames do
    for axiomName in actualAxioms env name do
      unless allowed.contains axiomName.toString do
        auditFailure s!"Forbidden axiom dependency: {axiomName}"
  let targetList ← parseOrFail targets.getArr?
  let mut records : Array Json := #[]
  for i in [:targetList.size] do
    let target := targetList[i]!
    let nameText ← parseOrFail (target.getObjValAs? String "theorem")
    let expectedText ← parseOrFail (target.getObjValAs? String "expected")
    let name := nameText.toName
    unless newNames.contains name do auditFailure s!"Missing submitted theorem: {name}"
    let info ← parseOrFail (requireSome (env.find? name) "Missing theorem")
    unless info.isTheorem do auditFailure "Requested proof declaration is not a theorem"
    unless info.levelParams.isEmpty do auditFailure "Target theorem must be closed and monomorphic"
    -- The expected type is generated in the trusted environment, never parsed
    -- from submitted notation. The kernel checks definitional equality here.
    let assertion : Declaration := .thmDecl {
      name := Name.str `InclusionProofcheck s!"validatedTarget{i}"
      levelParams := []
      type := mkConst expectedText.toName
      value := mkConst name }
    env ← addChecked env assertion
    let axioms := (actualAxioms env name).map (fun n => toJson n.toString)
    records := records.push (Json.mkObj [("theorem", toJson nameText),
      ("expected", toJson expectedText), ("axioms", .arr axioms)])
  return Json.mkObj [("status", toJson "verified"),
    ("declaration_count", toJson declarations.size), ("targets", .arr records)]

def main (arguments : List String) : IO UInt32 := do
  try
    let [payload, targets] := arguments | auditFailure "Expected payload and target paths"
    let result ← runAudit payload targets
    IO.println result.compress
    return (0 : UInt32)
  catch error =>
    IO.println (Json.mkObj [("status", toJson "rejected"), ("reason", toJson error.toString)]).compress
    return (1 : UInt32)
