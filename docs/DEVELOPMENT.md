# Development and embedding

The AI adapter harness and consequence scorer use the Python standard library. The [evaluation protocol](EVALUATION.md) explains model/run records and proof admission. Run commands from the repository root; an editable installation (`python3 -m pip install -e .`) also exposes the `inclusion-bench` command.

## Reproducible checks

```sh
python3 scripts/build_release.py
python3 -m unittest discover -s tests -v
python3 scripts/check_generated.py
python3 scripts/check_lean.py
```

Install the Lean version named in `lean/lean-toolchain`, or set `LEAN_BIN` to that compiler's absolute path. The check script builds modules serially and checks exported inference traces; it does not need mathlib. The optional complete 50-class build adds the pinned Mathlib quantum extension; see [its build instructions](../quantum/README.md). CI also uses a single compiler worker. The source download is pinned to the official Lean release.

The research inputs are `research/classical.json` and `research/quantum.json`. The importer assembles them into `data/knowledge.json`; changing generated data alone will fail the reproducibility check. The catalog seed script is an authoring utility, not part of every build: changes to class specifications should edit `data/classes.json` and then rerun the importer/build. Keep independent literature evidence and uncertainties with each change.

## Export an actual consequence to Lean

```sh
python3 -m inclusion_bench.cli export-lean separation PSPACE P \
  --assuming examples/bpp-strictly-below-np.json \
  --output lean/ExampleConsequence.lean
python3 scripts/check_lean.py
```

The generated theorem visibly assumes the cited baseline leaves, the submitted claims and any cited rule/complement identities used. It proves the actual inference trace with the semantic lemmas. Its conclusion is conditional; compiling it does not prove the submitted breakthrough. Export rejects independence atoms because they require the separate metatheory interface.

The checked examples exercise transitivity, both separation directions, a complement swap, forward conditional rules and contraposition. The Python tests also check generic soundness over all interpretations of three class symbols as subsets of a two-element universe.

## Embed the leaderboard

The generator reads repository-relative run manifest paths from `data/leaderboard_runs.json`. It re-evaluates each run and refuses publication unless the run has an official score. Keep the referenced proof artifacts and both review registries alongside the manifest. The initial list is empty. Ranks are computed separately for identical taskset, access-track and budget cohorts; equal scores share a rank. Do not compare ranks across cohorts. The site displays the cohort beside each run.

Serve the four files in `web/` over HTTP: `index.html`, `styles.css`, `app.js` and `benchmark.json`. They use relative URLs and no external dependencies. Copy that directory into a subdirectory of an existing website, or embed a hosted copy:

```html
<iframe
  src="https://tkwa.github.io/inclusion-bench/"
  title="InclusionBench leaderboard and complexity-class explorer"
  style="width:100%;height:1200px;border:0"
  loading="lazy">
</iframe>
```

GitHub Actions publishes the directory to GitHub Pages after checks pass. The public site includes the dataset version and hash, the draft admission notice, an initially empty model/run leaderboard, the historical zero reference and separately labeled scoring examples. Deploying this repository does not change any other website.
