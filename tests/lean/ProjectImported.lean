import Lean

def ProjectLibrary.LocalStatement : Prop := True
theorem ProjectLibrary.helper : ProjectLibrary.LocalStatement := True.intro
axiom ProjectLibrary.forbidden : False
axiom Literature.module_fact : ProjectLibrary.LocalStatement
unsafe def ProjectLibrary.unused : IO Unit := pure ()
