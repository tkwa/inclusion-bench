import ProofCodec

namespace InclusionProofcheck
open Lean Elab Command

partial def visitDeclaration (env : Environment) (name : Name)
    (seen : NameSet) (result : Array Json) : Except String (NameSet × Array Json) := do
  if seen.contains name || (env.getModuleIdxFor? name).isSome then return (seen, result)
  let info ← requireSome (env.find? name) s!"Unknown declaration: {name}"
  let encoded ← encodeDeclaration info
  let mut seen := seen.insert name
  let mut result := result
  for dependency in info.type.getUsedConstants ++
      ((info.value? (allowOpaque := true)).getD (mkConst ``True)).getUsedConstants do
    let next ← visitDeclaration env dependency seen result
    seen := next.1
    result := next.2
  return (seen, result.push encoded)

syntax "#proofcheck_export" : command

elab_rules : command
  | `(#proofcheck_export) => do
      let env ← getEnv
      let mut seen : NameSet := {}
      let mut result : Array Json := #[]
      for (name, _) in env.constants do
        if (env.getModuleIdxFor? name).isNone then
          match visitDeclaration env name seen result with
          | .error message => throwError message
          | .ok next =>
              seen := next.1
              result := next.2
      let payload := Json.mkObj [("schema_version", toJson (1 : Nat)), ("declarations", .arr result)]
      liftIO <| IO.FS.writeFile "/work/proof-export.json" payload.compress

end InclusionProofcheck
