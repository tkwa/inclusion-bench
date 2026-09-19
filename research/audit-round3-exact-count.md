# Round 3: exact-count implications

All four normalized rules are accepted after an independent reconstruction. The two original holds are discharged. The [JSON dossier](audit-round3-exact-count.json) records the argument, boundary checks, source locators, and the hash of the cross-review being checked.

| Hypothesis | Accepted consequences |
| --- | --- |
| C₌P ⊆ AWPP | PH, PP, ⊕P ⊆ AWPP |
| C₌P ⊆ WPP | PH, PP, ⊕P ⊆ WPP |
| C₌P ⊆ ⊕P | PH, PP ⊆ ⊕P |
| C₌P ⊆ QMA | PH, ⊕P ⊆ PP |

## D1: one exact-count certificate

Write a one-query computation as a #P value F(x) followed by a polynomial-time predicate b(x,j). Choose a polynomial width w with F(x)<2^w(|x|). Guess exactly w bits for j, ask whether F(x)=j, and accept only when equality holds and b accepts. A strict upper bound includes the largest count; fixed-width representations give exactly one guessed word per integer. Incorrect guesses cannot create a second accepting branch.

The exact-count language is C₌P: use the gap F(x)−j on a well-formed pair and gap1 on malformed inputs. A containment hypothesis changes only the class in which this same oracle language lies. It does not change the oracle answers or require the hypothetical containment to relativize.

The construction covers PH by the strong one-#P-query Toda theorem. It covers ⊕P by testing a count's parity. For the repository's GapP presentation of PP, write its gap as f₁−f₂. If both nonnegative counts are below2^q, the single #P value2^q f₁+f₂ encodes both counts; division and remainder recover them for comparison. Thus the PP endpoint does not depend on silently substituting another definition.

The last closure steps are unconditional. [STT, printedp22](https://urresearch.rochester.edu/fileDownloadForInstitutionalItem.action?itemFileId=464&itemId=374), requires unambiguity with the actual oracle and gives UP^AWPP ⊆ AWPP. Its printedp24 gives UP^WPP ⊆ coC₌P. Under C₌P ⊆ WPP, the ordinary inclusion WPP ⊆ C₌P and complement closure make coC₌P=WPP. For parity, use UP^⊕P ⊆ ⊕P^⊕P=⊕P; [OH, Proposition2.7(3)](https://urresearch.rochester.edu/fileDownloadForInstitutionalItem.action?itemFileId=7017&itemId=4661), supplies the final equality. No unrestricted WPP Turing closure is asserted.

## D2: the quantum premise only needs exact counting

Use the same total exact-count language A. Encode each guessed pair as1ⁿ0xj, where n=|x| and j has w(n) bits. Every query for a fixed input has length ℓ(n)=2n+1+w(n). This is essential: the threshold below must be identical for all guesses.

Under C₌P ⊆ QMA, A belongs to QMA and hence A0PP. [Vyalyi, Lemma3 and Theorem1](https://eccc.weizmann.ac.il/report/2003/021/download/), gives a GapP function h₀ with a positive length-dependent power-of-two threshold: a yes query exceeds the threshold; a no query has nonnegative value below half of it. Raise h₀ to power ℓ+2. Polynomially bounded products remain GapP. Call the new common threshold S.

Sum b(x,j)h(encode(x,j)) over all w-bit guesses. Exponentially many guessed summands still give one GapP function H. A filtered-out summand contributes gap0, implemented with a cancelling accept/reject pair, rather than a lone rejecting branch.

On a yes input, the unique correct count contributes more than S and all other terms are nonnegative. On a no input, the correct count is filtered out. At most2^w wrong terms each contribute less than2^−(ℓ+2)S, so their sum is below S/4. Therefore H−S is positive exactly on the language. S has polynomial bit length and is an FP function, so the subtraction is allowed.

This works for every P^#P[1] language, including both PH and ⊕P. It requires neither PP ⊆ QMA nor QMA complement closure. The weaker C₌P premise is an explicit adaptation of the published argument; it is not attributed to the text of Vyalyi's corollary.

Adding these four rules to the inspected baseline produced no contradiction and no new unconditional labels. The parent owns the complete SAT replay. Existing counting closure and quantum model-equivalence theorems remain trusted mathematical inputs under the user's waiver; this review does not represent them as new Lean proofs.
