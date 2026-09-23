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

/-- Bind a literature statement to the submitted definitions that give its
constants meaning. Only prior reconstructed declarations occur in `payloads`;
trusted imported constants terminate traversal. Sorting siblings makes the
dependency-first order independent of unrelated payload declaration order. -/
partial def collectLiteratureContext (env : Environment) (payloads : NameMap Json)
    (roots : Array Name) (seen : NameSet := {}) (result : Array Json := #[]) :
    Except String (NameSet × Array Json) := do
  let mut seen := seen
  let mut result := result
  for name in roots.qsort Name.lt do
    unless seen.contains name do
      seen := seen.insert name
      if let some json := payloads.find? name then
        let info ← requireSome (env.find? name) s!"Missing reconstructed dependency: {name}"
        let dependencies := info.type.getUsedConstants ++
          ((info.value? (allowOpaque := true)).map Expr.getUsedConstants).getD #[]
        let next ← collectLiteratureContext env payloads dependencies seen result
        seen := next.1
        result := next.2.push json
  return (seen, result)

def readLiteratureRequests (path? : Option System.FilePath) : IO NameSet := do
  let some path := path? | return {}
  let manifest ← parseOrFail (Json.parse (← IO.FS.readFile path))
  let requests ← parseOrFail ((← parseOrFail (manifest.getObjVal? "requests")).getArr?)
  let mut names : NameSet := {}
  for request in requests do
    let text ← parseOrFail (request.getObjValAs? String "name")
    let name := text.toName
    unless isLiteratureName name && name.toString == text do
      auditFailure s!"Invalid literature request name: {text}"
    if names.contains name then auditFailure s!"Duplicate literature request: {text}"
    names := names.insert name
  return names

def runAudit (payloadPath targetsPath : System.FilePath)
    (literaturePath? : Option System.FilePath := none) : IO Json := do
  let payload ← parseOrFail (Json.parse (← IO.FS.readFile payloadPath))
  let targets ← parseOrFail (Json.parse (← IO.FS.readFile targetsPath))
  let requestedLiterature ← readLiteratureRequests literaturePath?
  let version ← parseOrFail (payload.getObjValAs? Nat "schema_version")
  if version != 1 && version != 2 && version != 3 then auditFailure "Unknown proof export version"
  let declarations ← parseOrFail ((← parseOrFail (payload.getObjVal? "declarations")).getArr?)
  if declarations.size > 100000 then auditFailure "Too many declarations"
  let mut env ← importModules #[{module := `TrustedBaseline}, {module := `ProofExport}] {}
  let allowed := InclusionBench.TrustedBaseline.allowedAxiomNames
  let mut newNames : Array Name := #[]
  let mut literatureNames : NameSet := {}
  let mut literatureDependencies : Array Json := #[]
  let mut reconstructedPayloads : NameMap Json := {}
  for json in declarations do
    let declaration ← parseOrFail (
      if version == 1 then decodeDeclaration json
      else if version == 2 then decodeDeclarationV2 json
      else decodeDeclarationV3 json)
    for name in declaration.getNames do
      if env.contains name then auditFailure s!"Attempt to replace trusted declaration: {name}"
      if "InclusionBench.TrustedBaseline".isPrefixOf name.toString then
        auditFailure "Reserved baseline namespace"
      newNames := newNames.push name
    if let .axiomDecl value := declaration then
      unless requestedLiterature.contains value.name do
        auditFailure s!"Unrequested literature axiom: {value.name}"
      literatureNames := literatureNames.insert value.name
    env ← addChecked env declaration
    if let .axiomDecl value := declaration then
      let (_, context) ← parseOrFail <|
        collectLiteratureContext env reconstructedPayloads value.type.getUsedConstants
      let options := ({} : Options).setBool `pp.fullNames true
        |>.setBool `pp.universes true |>.setNat `pp.maxSteps 10000
      let statement ← PrettyPrinter.ppExprLegacy env {} {} options value.type
      -- Preserve precisely the data that was reconstructed and kernel-checked.
      -- The caller binds this declaration and the separate citation request
      -- together for review; neither the name nor a citation grants approval.
      literatureDependencies := literatureDependencies.push (Json.mkObj [
        ("name", toJson value.name.toString), ("declaration", json),
        ("context", .arr context), ("statement", toJson statement.pretty)])
    for name in declaration.getNames do
      reconstructedPayloads := reconstructedPayloads.insert name json
  -- Audit every reconstructed declaration, including unused helpers.
  for name in newNames do
    for axiomName in actualAxioms env name do
      unless allowed.contains axiomName.toString || literatureNames.contains axiomName do
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
  -- Even unused literature entries in a hand-crafted payload require review.
  -- Ordinary exports contain only the target closure, including dependencies
  -- in the types of requested literature axioms.
  let status := if literatureDependencies.isEmpty then "verified" else "needs_literature_review"
  return Json.mkObj [("status", toJson status), ("kernel_status", toJson "verified"),
    ("literature_dependencies", .arr literatureDependencies),
    ("declaration_count", toJson declarations.size), ("targets", .arr records)]

def main (arguments : List String) : IO UInt32 := do
  try
    let result ← match arguments with
      | [payload, targets] => runAudit payload targets
      | [payload, targets, literature] => runAudit payload targets (some literature)
      | _ => auditFailure "Expected payload and target paths, and optionally a literature manifest"
    IO.println result.compress
    return (0 : UInt32)
  catch error =>
    IO.println (Json.mkObj [("status", toJson "rejected"), ("reason", toJson error.toString)]).compress
    return (1 : UInt32)
