import InclusionBench

/- Inspect the kernel dependencies of the principal proved statements.
Standard Lean foundations (propext, Classical.choice, Quot.sound) are allowed.
No project-specific axiom or incomplete proof may appear in this output. -/

#print axioms InclusionBench.includes_trans
#print axioms InclusionBench.nonincludes_expand
#print axioms InclusionBench.includes_complement_iff
#print axioms InclusionBench.horn_contrapositive
#print axioms InclusionBench.derivation_sound
#print axioms InclusionBench.certificateStep_sound
#print axioms InclusionBench.checkCertificate_sound
#print axioms InclusionBench.no_contradictory_derivations
#print axioms InclusionBench.score_bound
#print axioms InclusionBench.score_monotone
#print axioms InclusionBench.duplicate_eligibility_same_score
#print axioms InclusionBench.full_matrix_score_bound
#print axioms InclusionBench.empty_submission_zero
#print axioms InclusionBench.emptyTheory_independent
#print axioms InclusionBench.Arithmetic.zeroEqualsOne_false
#print axioms InclusionBench.Arithmetic.trueInN_neg
#print axioms InclusionBench.Arithmetic.successorNonzero_true
#print axioms InclusionBench.Arithmetic.additionCommutes_true
#print axioms InclusionBench.classicalExplosion_arithmeticExplosion
#print axioms InclusionBench.arithmeticSound_not_provable_false
#print axioms InclusionBench.arithmeticSound_not_refutable_true
#print axioms InclusionBench.arithmeticSound_implies_consistent
#print axioms InclusionBench.ConditionalIndependenceCertificate.conditional
#print axioms InclusionBench.ConditionalIndependenceCertificate.instantiate
#print axioms InclusionBench.ConditionalIndependenceCertificate.ofStrongerPremise
#print axioms InclusionBench.liftConsistencyIndependence
#print axioms InclusionBench.liftConsistencyIndependence_sentence
#print axioms InclusionBench.IndependencePremise.unconditional_holds
#print axioms InclusionBench.IndependencePremise.arithmeticSoundness_implies_consistency
#print axioms InclusionBench.admitSoundnessFromConsistency
#print axioms InclusionBench.admitSoundnessFromConsistency_sentence
#print axioms InclusionBench.Machines.dtime_monotone
#print axioms InclusionBench.Machines.dspace_monotone
#print axioms InclusionBench.Machines.linear_exponential_in_exponential
#print axioms InclusionBench.Machines.nlinear_exponential_in_nexponential
#print axioms InclusionBench.Machines.simultaneous_in_polynomial_time
#print axioms InclusionBench.Circuits.nc1_in_polynomial_circuits
#print axioms InclusionBench.Circuits.ac0_in_acc0
#print axioms InclusionBench.Randomized.coinStrings_length
#print axioms InclusionBench.Randomized.halted_padding
#print axioms InclusionBench.Randomized.rp_in_sbp
#print axioms InclusionBench.Counting.up_in_fewp
#print axioms InclusionBench.Counting.spp_in_pp
#print axioms InclusionBench.Counting.spp_in_awpp
#print axioms InclusionBench.Counting.duplicate_branches_count_two
#print axioms InclusionBench.Oracles.theta2_in_delta2
#print axioms InclusionBench.Oracles.sigma2_in_ph
#print axioms InclusionBench.Transducers.output_length_le_time
#print axioms InclusionBench.Transducers.spp_in_wpp
#print axioms InclusionBench.Transducers.spp_in_lwpp
#print axioms InclusionBench.UniformCircuits.encode_naturals_injective
#print axioms InclusionBench.UniformCircuits.nc_in_polynomial_circuits
#print axioms InclusionBench.ProofSystems.encodeTriple_injective
#print axioms InclusionBench.LogCFL.transduced_output_polynomial_length
#print axioms InclusionBench.Statistical.far_close_disjoint
#print axioms InclusionBench.Statistical.distinct_point_masses_have_distance_one
#print axioms InclusionBench.Statistical.duplicate_outcomes_retain_mass
#print axioms InclusionBench.roster_size
#print axioms InclusionBench.operational_definition_count
