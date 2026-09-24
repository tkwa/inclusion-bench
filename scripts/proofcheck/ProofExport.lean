import ProofCodec

namespace InclusionProofcheck
open Lean Elab Command

partial def visitDeclaration (env : Environment) (name : Name)
    (seen : NameSet) (result : Array Json) (candidateModules : NameSet := {}) :
    Except String (NameSet × Array Json) := do
  if seen.contains name then return (seen, result)
  if let some moduleIdx := env.getModuleIdxFor? name then
    unless candidateModules.contains env.header.moduleNames[moduleIdx]! do
      return (seen, result)
  let info ← requireSome (env.find? name) s!"Unknown declaration: {name}"
  let encoded ← encodeExportDeclaration info
  let mut seen := seen.insert name
  let mut result := result
  for dependency in info.type.getUsedConstants ++
      ((info.value? (allowOpaque := true)).getD (mkConst ``True)).getUsedConstants do
    let next ← visitDeclaration env dependency seen result candidateModules
    seen := next.1
    result := next.2
  return (seen, result.push encoded)

def exportDeclarationRoots (env : Environment) (roots : Array Name)
    (candidateModules : NameSet := {}) : Except String Json := do
  let mut seen : NameSet := {}
  let mut result : Array Json := #[]
  for name in roots do
    let next ← visitDeclaration env name seen result candidateModules
    seen := next.1
    result := next.2
  return Json.mkObj [("schema_version", toJson (3 : Nat)), ("declarations", .arr result)]

def writeExport (roots : Array Name) (candidateModules : NameSet := {}) : CommandElabM Unit := do
  match exportDeclarationRoots (← getEnv) roots candidateModules with
  | .error message => throwError message
  | .ok payload =>
      match boundedJsonSize payload maxProofExportBytes with
      | .error _ => throwError "Proof export exceeds 256 MiB"
      | .ok _ => liftIO <| IO.FS.writeFile "/work/proof-export.json" payload.compress

syntax "#proofcheck_export" : command
syntax "#proofcheck_export_targets" "[" str,* "]" : command
syntax "#proofcheck_export_project" "[" str,* "]" "[" str,* "]" : command

elab_rules : command
  | `(#proofcheck_export) => do
      let env ← getEnv
      let mut roots := #[]
      for (name, _) in env.constants do
        if (env.getModuleIdxFor? name).isNone then
          roots := roots.push name
      writeExport roots
  | `(#proofcheck_export_targets [$names:str,*]) =>
      writeExport (names.getElems.map fun name => name.getString.toName)
  | `(#proofcheck_export_project [$modules:str,*] [$names:str,*]) => do
      let candidateModules := modules.getElems.foldl
        (fun seen module => seen.insert module.getString.toName) ({} : NameSet)
      writeExport (names.getElems.map fun name => name.getString.toName) candidateModules

end InclusionProofcheck
