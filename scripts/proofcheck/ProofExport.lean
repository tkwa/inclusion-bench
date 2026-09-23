import ProofCodec

namespace InclusionProofcheck
open Lean Elab Command

partial def visitDeclaration (env : Environment) (name : Name)
    (seen : NameSet) (result : Array Json) : Except String (NameSet × Array Json) := do
  if seen.contains name || (env.getModuleIdxFor? name).isSome then return (seen, result)
  let info ← requireSome (env.find? name) s!"Unknown declaration: {name}"
  let encoded ← encodeExportDeclaration info
  let mut seen := seen.insert name
  let mut result := result
  for dependency in info.type.getUsedConstants ++
      ((info.value? (allowOpaque := true)).getD (mkConst ``True)).getUsedConstants do
    let next ← visitDeclaration env dependency seen result
    seen := next.1
    result := next.2
  return (seen, result.push encoded)

def exportDeclarationRoots (env : Environment) (roots : Array Name) : Except String Json := do
  let mut seen : NameSet := {}
  let mut result : Array Json := #[]
  for name in roots do
    let next ← visitDeclaration env name seen result
    seen := next.1
    result := next.2
  return Json.mkObj [("schema_version", toJson (3 : Nat)), ("declarations", .arr result)]

def writeExport (roots : Array Name) : CommandElabM Unit := do
  match exportDeclarationRoots (← getEnv) roots with
  | .error message => throwError message
  | .ok payload => liftIO <| IO.FS.writeFile "/work/proof-export.json" payload.compress

syntax "#proofcheck_export" : command
syntax "#proofcheck_export_targets" "[" str,* "]" : command

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

end InclusionProofcheck
