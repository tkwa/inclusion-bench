/* No build step or third-party dependencies. benchmark.json is the sole data source. */
"use strict";

(() => {
  const $ = (id) => document.getElementById(id);
  const state = {
    data: null, classes: new Map(), sources: new Map(), pairs: new Map(),
    selectedPair: { left: "NP", right: "P" }, scenario: null,
    scenarioResolutions: new Map(), baselineSteps: new Map(), scenarioSteps: new Map(), visibleClasses: [], overlay: false,
  };
  const statusLabels = {
    inclusion: "Known inclusion", separation: "Known noninclusion",
    unreviewed: "Eligibility unreviewed", independence: "Independent of ZFC",
  };
  const key = (left, right) => `${left}|${right}`;
  const number = (n) => Number.isFinite(Number(n)) ? Number(n).toLocaleString("en-US") : "—";
  const label = (id) => state.classes.get(id)?.label || id || "?";
  const relationSymbol = (relation) => relation === "separation" ? "⊈" : relation === "independence" ? "⊆ ?" : "⊆";
  const statement = (record) => `${label(record.left)} ${relationSymbol(record.relation || record.status)} ${label(record.right)}`;
  function element(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined && text !== null) node.textContent = String(text);
    return node;
  }
  function date(value) {
    if (!value) return "";
    const parsed = new Date(`${String(value).slice(0, 10)}T12:00:00Z`);
    return Number.isNaN(parsed.valueOf()) ? String(value) : new Intl.DateTimeFormat("en-US", { month: "long", day: "numeric", year: "numeric", timeZone: "UTC" }).format(parsed);
  }
  function safeLink(url) {
    try {
      const parsed = new URL(url, window.location.href);
      return ["http:", "https:"].includes(parsed.protocol) ? parsed.href : null;
    } catch { return null; }
  }
  function sourceLink(source) {
    const href = safeLink(source.url);
    if (!href) return element("span", "proof-source", source.title || source.id);
    const a = element("a", "proof-source", source.title || source.id);
    a.href = href;
    a.target = "_blank";
    a.rel = "noopener noreferrer";
    return a;
  }
  function sourceLinks(target, ids) {
    for (const id of [...new Set(ids || [])]) {
      const source = state.sources.get(id);
      if (source) target.append(sourceLink(source));
      else target.append(element("span", "proof-note", `Source ID: ${id}`));
    }
  }
  function reasonLabel(reason) {
    const raw = typeof reason === "string" ? reason : JSON.stringify(reason || "Recorded implication");
    if (raw.startsWith("baseline:")) return "Recorded baseline theorem";
    const known = { reflexivity: "Every class contains itself", transitivity: "Compose two inclusions", complement: "Take complements on both sides", "separation-left": "The larger row class inherits a separating language", "separation-right": "The smaller column class still excludes the separating language", submission: "Assumed breakthrough" };
    if (known[raw]) return known[raw];
    if (raw.startsWith("padding-")) return "A reviewed padding implication";
    if (raw.startsWith("hardwire-")) return "A reviewed circuit simulation implication";
    if (raw.startsWith("intersection-")) return "Both inclusions give membership in the intersection";
    if (raw.startsWith("q-ikw-")) return "Impagliazzo–Kabanets–Wigderson theorem";
    if (raw.startsWith("q-pp-circuits-")) return "Circuit upper bounds imply an MA simulation";
    if (raw.startsWith("ph-collapse-")) return "Collapse of the polynomial hierarchy";
    if (raw.startsWith("karp-lipton")) return "Karp–Lipton theorem";
    if (raw.startsWith("toda-")) return "Toda's theorem";
    return "A reviewed conditional theorem";
  }
  function normalizedStatus(record) {
    const status = record?.status || record?.relation || "unreviewed";
    return Object.hasOwn(statusLabels, status) ? status : "unreviewed";
  }
  function displayPair(left, right) {
    const hypothetical = state.overlay && state.scenarioResolutions.get(key(left, right));
    if (hypothetical) return { ...hypothetical, status: hypothetical.relation, hypothetical: true };
    return state.pairs.get(key(left, right)) || { left, right, status: "unreviewed" };
  }

  async function loadData() {
    $("loading").hidden = false;
    $("load-error").hidden = true;
    try {
      const response = await fetch("benchmark.json", { cache: "no-cache" });
      if (!response.ok) throw new Error(`benchmark.json returned HTTP ${response.status}.`);
      const data = await response.json();
      if (!Array.isArray(data.classes) || !Array.isArray(data.pairs)) throw new Error("The dataset must contain classes and pairs arrays.");
      state.data = data;
      state.classes = new Map(data.classes.map((c) => [c.id, c]));
      state.sources = new Map((data.sources || []).map((s) => [s.id, s]));
      state.pairs = new Map(data.pairs.map((p) => [key(p.left, p.right), p]));
      state.baselineSteps = new Map((data.baseline_proof_steps || []).map((step) => [step.id, step]));
      if (!state.classes.has("NP") || !state.classes.has("P")) {
        state.selectedPair = { left: data.classes[0]?.id, right: data.classes[1]?.id || data.classes[0]?.id };
      }
      renderMetadata();
      renderLeaderboard();
      renderFilters();
      renderSources();
      renderScenarios();
      renderMatrix();
      renderPair();
      $("loading").hidden = true;
      $("benchmark-content").hidden = false;
    } catch (error) {
      $("loading").hidden = true;
      $("benchmark-content").hidden = true;
      $("load-error").hidden = false;
      $("load-error-detail").textContent = `${error.message} Serve this directory over HTTP with benchmark.json beside the page.`;
    }
  }

  function renderMetadata() {
    const d = state.data;
    const name = d.name || "Inclusion Bench";
    $("site-name").textContent = name;
    $("footer-name").textContent = name;
    document.title = `${name} — the complexity frontier`;
    $("cutoff").textContent = date(d.cutoff);
    $("version").textContent = `Version ${d.version || "draft"}`;
    $("class-count").textContent = number(d.class_count ?? d.classes.length);
    $("pair-count").textContent = number(d.ordered_pairs ?? d.classes.length ** 2);
    const counts = d.counts || {};
    $("known-count").textContent = number((counts.inclusion || 0) + (counts.separation || 0) + (counts.independence || 0));
    $("unreviewed-count").textContent = number(counts.unreviewed ?? d.pairs.filter((p) => normalizedStatus(p) === "unreviewed").length);
    $("dataset-hash").textContent = d.dataset_sha256 || "Not provided";
    const repo = safeLink(d.repository_url || d.repo_url || d.repository || "");
    if (repo && (d.repository_url || d.repo_url || d.repository)) {
      $("repo-link").href = repo;
      $("repo-link").target = "_blank";
      $("repo-link").rel = "noopener noreferrer";
    }
    const coverage = d.coverage?.coverage_summary || d.coverage?.summary || d.coverage;
    if (coverage && Number.isFinite(coverage.direct) && Number.isFinite(coverage.unsupported)) {
      const mapped = coverage.direct + (coverage.consequence || 0);
      const total = mapped + coverage.unsupported;
      $("coverage-summary").textContent = `${total} example advances: ${mapped} map to roster claims; ${coverage.unsupported} have no guaranteed scoring implication. This is a stress test, not a likelihood ranking.`;
    }
  }

  function renderLeaderboard() {
    const body = $("leaderboard-body");
    body.replaceChildren();
    const records = (state.data.leaderboard || []).filter((r) => !["hypothetical", "scenario", "demo"].includes(r.kind));
    for (const record of records) {
      const tr = element("tr");
      tr.append(element("td", "", record.rank ?? "—"));
      const entry = element("td");
      entry.append(element("span", "entry-name", record.name));
      const baseline = /baseline|historical|reference/i.test(`${record.kind || ""} ${record.name || ""}`);
      entry.append(element("span", "entry-description", baseline ? "Knowledge available at the cutoff" : record.description || "Accepted mathematical result"));
      tr.append(entry);
      const score = element("td", "number-column");
      score.append(element("span", "leaderboard-score", number(record.score)));
      tr.append(score);
      const status = element("td");
      status.append(element("span", "record-status", baseline ? "Reference baseline" : record.kind || "Recorded submission"));
      status.append(element("span", "record-date", date(record.date)));
      tr.append(status);
      body.append(tr);
    }
    if (!records.length) {
      const tr = element("tr");
      const td = element("td", "entry-description", "No official entries have been recorded.");
      td.colSpan = 4;
      tr.append(td);
      body.append(tr);
    }
  }

  function renderFilters() {
    const select = $("family-filter");
    const previous = select.value;
    select.replaceChildren(new Option("All families", ""));
    const families = [...new Set(state.data.classes.map((c) => c.family).filter(Boolean))].sort();
    for (const family of families) select.add(new Option(family.replaceAll("_", " "), family));
    select.value = previous;
  }

  function renderMatrix() {
    if (!state.data) return;
    const query = $("class-search").value.toLowerCase().trim();
    const family = $("family-filter").value;
    const highlighted = $("status-filter").value;
    state.visibleClasses = state.data.classes.filter((c) => (!family || c.family === family) && (!query || `${c.id} ${c.label} ${c.family || ""} ${c.definition || ""}`.toLowerCase().includes(query)));
    const classes = state.visibleClasses;
    const table = $("matrix-table");
    table.replaceChildren();
    const caption = element("caption", "sr-only", "Rows are A; columns are B. Each cell asks whether A is contained in B. Use arrow keys to move among cells, then Enter for details.");
    const thead = element("thead");
    const header = element("tr");
    const corner = element("th", "corner-cell", "A ↓ / B →");
    corner.scope = "col";
    header.append(corner);
    for (const c of classes) {
      const th = element("th");
      th.scope = "col";
      th.title = c.label;
      th.append(element("span", "col-label", c.label));
      header.append(th);
    }
    thead.append(header);
    const tbody = element("tbody");
    let selectedIsVisible = classes.some((c) => c.id === state.selectedPair.left) && classes.some((c) => c.id === state.selectedPair.right);
    for (const [row, a] of classes.entries()) {
      const tr = element("tr");
      const th = element("th", "", a.label);
      th.scope = "row";
      tr.append(th);
      for (const [col, b] of classes.entries()) {
        const pair = displayPair(a.id, b.id);
        const status = normalizedStatus(pair);
        const td = element("td");
        const button = element("button", "matrix-cell");
        button.type = "button";
        button.dataset.left = a.id;
        button.dataset.right = b.id;
        button.dataset.row = row;
        button.dataset.col = col;
        button.dataset.status = status;
        const selected = state.selectedPair.left === a.id && state.selectedPair.right === b.id;
        button.classList.toggle("selected", selected);
        button.classList.toggle("diagonal", a.id === b.id);
        button.classList.toggle("dimmed", !!highlighted && status !== highlighted);
        button.classList.toggle("hypothetical", !!pair.hypothetical);
        button.tabIndex = selected || (!selectedIsVisible && row === 0 && col === 0) ? 0 : -1;
        button.setAttribute("aria-pressed", String(selected));
        const description = `${a.label} contained in ${b.label}: ${pair.hypothetical ? "hypothetical " + (status === "separation" ? "noninclusion" : status) : statusLabels[status]}`;
        button.setAttribute("aria-label", description);
        button.title = description;
        td.append(button);
        tr.append(td);
      }
      tbody.append(tr);
    }
    table.append(caption, thead, tbody);
    $("matrix-empty").hidden = classes.length > 0;
    $("matrix-scroll").hidden = classes.length === 0;
    $("matrix-description").textContent = `${classes.length} × ${classes.length} ${state.overlay ? "hypothetical overlay" : "relation matrix"}`;
    $("matrix-visible-count").textContent = `${classes.length} of ${state.data.classes.length} classes · ${number(classes.length ** 2)} cells`;
    $("scenario-legend").hidden = !state.overlay;
  }

  function selectPair(left, right) {
    state.selectedPair = { left, right };
    for (const button of $("matrix-table").querySelectorAll(".matrix-cell")) {
      const selected = button.dataset.left === left && button.dataset.right === right;
      button.classList.toggle("selected", selected);
      button.setAttribute("aria-pressed", String(selected));
      button.tabIndex = selected ? 0 : -1;
    }
    renderPair();
  }

  function renderPair() {
    if (!state.data) return;
    const { left, right } = state.selectedPair;
    const pair = displayPair(left, right);
    const status = normalizedStatus(pair);
    $("pair-title").replaceChildren(document.createTextNode(label(left)), element("span", "", "⊆"), document.createTextNode(label(right)));
    const badge = element("span", `relation-badge ${status} ${pair.hypothetical ? "hypothetical" : ""}`, pair.hypothetical ? `Hypothetical ${status === "separation" ? "noninclusion" : status}` : statusLabels[status]);
    $("pair-status").replaceChildren(badge);
    const explanations = {
      inclusion: "Every language in the row class is also in the column class, according to the recorded baseline.",
      separation: "The baseline establishes that some language in the row class is absent from the column class.",
      unreviewed: "The current baseline has no resolution for this direction. A historical review must establish eligibility before a new result can earn an official point.",
      independence: "The recorded result establishes independence of this inclusion from the specified formal theory. Consult its certificate for the exact metatheoretic assumptions.",
    };
    $("pair-explanation").textContent = pair.hypothetical ? "This relation follows inside the selected scenario. Its assumptions have not been proved or admitted by the benchmark." : explanations[status];
    const definitions = $("pair-definitions");
    definitions.replaceChildren();
    for (const id of [...new Set([left, right])]) {
      const c = state.classes.get(id);
      definitions.append(element("dt", "", label(id)));
      const dd = element("dd", "", c?.definition || "No definition supplied in this dataset.");
      if (c?.uniformity) dd.append(element("span", "uniformity-note", typeof c.uniformity === "string" ? c.uniformity : JSON.stringify(c.uniformity)));
      definitions.append(dd);
    }
    const evidence = $("pair-evidence");
    evidence.replaceChildren();
    const pairProof = resolveProof(pair.proof, !!pair.hypothetical);
    if (pairProof.steps.length) {
      evidence.append(element("h4", "", pair.hypothetical ? "Conditional proof trail" : "Baseline proof trail"));
      const trace = element("div", "proof-trace");
      renderProof(trace, pairProof, true);
      evidence.append(trace);
    } else if (pair.source_ids?.length) {
      evidence.append(element("h4", "", "Recorded sources"));
      sourceLinks(evidence, pair.source_ids);
    } else {
      evidence.append(element("p", "", status === "unreviewed" ? "No resolution certificate is recorded for this pair." : "This dataset supplies the status without a pair-level derivation. The registry below lists the available sources."));
      const a = element("a", "proof-source", "Browse the source registry ↓");
      a.href = "#method";
      a.addEventListener("click", () => document.querySelector(".sources-details").open = true);
      evidence.append(a);
    }
  }

  function renderScenarios() {
    const select = $("scenario-select");
    select.replaceChildren();
    for (const scenario of state.data.scenarios || []) select.add(new Option(scenario.title || scenario.id, scenario.id));
    select.disabled = select.options.length === 0;
    chooseScenario(select.value);
  }

  function chooseScenario(id) {
    state.scenario = (state.data.scenarios || []).find((s) => s.id === id) || null;
    state.scenarioResolutions = new Map((state.scenario?.resolutions || []).map((r) => [key(r.left, r.right), r]));
    state.scenarioSteps = new Map((state.scenario?.proof_steps || []).map((step) => [step.id, step]));
    $("scenario-score").textContent = state.scenario ? number(state.scenario.score) : "—";
    const claims = $("scenario-claims");
    claims.replaceChildren();
    for (const claim of state.scenario?.claims || []) claims.append(element("span", "claim-chip", statement(claim)));
    if (!state.scenario) claims.append(element("p", "proof-note", "No hypothetical scenarios are supplied in this dataset."));
    const select = $("resolution-select");
    select.replaceChildren();
    for (const [index, resolution] of (state.scenario?.resolutions || []).entries()) select.add(new Option(statement(resolution), String(index)));
    select.disabled = select.options.length === 0;
    renderScenarioTrace();
    if (state.overlay) { renderMatrix(); renderPair(); }
  }

  function renderScenarioTrace() {
    const resolution = state.scenario?.resolutions?.[Number($("resolution-select").value)];
    const trace = $("scenario-trace");
    trace.replaceChildren();
    if (!resolution) {
      trace.append(element("p", "proof-note", "This scenario resolves no additional pairs under the current draft baseline."));
      return;
    }
    const proof = resolveProof(resolution.proof, true);
    if (!proof.steps.length) {
      trace.append(element("p", "proof-note", "No detailed proof trace is supplied for this resolution."));
      sourceLinks(trace, resolution.source_ids);
      return;
    }
    renderProof(trace, proof, false);
  }

  function resolveProof(proof, scenario = false) {
    if (proof?.steps?.length) return proof;
    const result = { target: proof?.target, steps: [], missing: [] };
    if (!proof?.target) return result;
    const visited = new Set();
    const active = new Set();
    function visit(id) {
      if (visited.has(id)) return;
      if (active.has(id)) { result.missing.push(`Cycle at ${id}`); return; }
      const step = (scenario && state.scenarioSteps.get(id)) || state.baselineSteps.get(id);
      if (!step) { result.missing.push(id); visited.add(id); return; }
      active.add(id);
      for (const parent of step.parents || []) visit(parent);
      active.delete(id);
      visited.add(id);
      result.steps.push(step);
    }
    visit(proof.target);
    return result;
  }

  function renderProof(target, proof, compact) {
    target.replaceChildren();
    const steps = proof.steps || [];
    if (proof.missing?.length) target.append(element("p", "proof-note", `Incomplete trace: ${proof.missing.join(", ")}`));
    const index = new Map(steps.map((step, i) => [step.id, i + 1]));
    for (const [i, step] of steps.entries()) {
      const wrap = element("div", "proof-step");
      const details = element("details");
      const summary = element("summary");
      summary.append(element("span", "step-number", String(i + 1).padStart(2, "0")));
      summary.append(element("span", "step-equation", statement(step)));
      details.append(summary);
      details.append(element("p", "step-reason", reasonLabel(step.reason)));
      const detail = element("div", "step-detail");
      if (step.parents?.length) {
        const parents = step.parents.map((p) => index.has(p) ? `step ${index.get(p)}` : String(p)).join(", ");
        detail.append(element("p", "", `Depends on ${parents}.`));
      }
      sourceLinks(detail, step.source_ids);
      if (!step.parents?.length && !step.source_ids?.length) {
        detail.append(element("p", "", /assum|claim|submission|hypothes/i.test(String(step.reason)) ? "Assumed for this scenario; not an admitted theorem." : "A logical or definitional step. No separate literature source is attached."));
      }
      if (step.id) detail.append(element("p", "", `Record: ${step.id}`));
      details.append(detail);
      details.open = !compact && i === steps.length - 1;
      wrap.append(details);
      target.append(wrap);
    }
    if (!compact) target.append(element("p", "proof-note", "This trace checks the recorded implications. It does not supply a semantic Lean proof of an assumed breakthrough."));
  }

  function renderSources() {
    const list = $("source-list");
    list.replaceChildren();
    for (const source of state.data.sources || []) {
      const item = element("li");
      const a = sourceLink(source);
      item.append(a);
      item.append(element("p", "", [source.year, source.locator].filter(Boolean).join(" · ")));
      if (source.notes) item.append(element("p", "", source.notes));
      list.append(item);
    }
    $("source-count").textContent = `${number(state.sources.size)} records`;
  }

  $("retry-load").addEventListener("click", loadData);
  let searchTimer;
  $("class-search").addEventListener("input", () => { clearTimeout(searchTimer); searchTimer = setTimeout(renderMatrix, 120); });
  $("family-filter").addEventListener("change", renderMatrix);
  $("status-filter").addEventListener("change", renderMatrix);
  $("reset-filters").addEventListener("click", () => {
    $("class-search").value = "";
    $("family-filter").value = "";
    $("status-filter").value = "";
    renderMatrix();
  });
  $("matrix-table").addEventListener("click", (event) => {
    const button = event.target.closest(".matrix-cell");
    if (button) selectPair(button.dataset.left, button.dataset.right);
  });
  $("matrix-table").addEventListener("keydown", (event) => {
    const button = event.target.closest(".matrix-cell");
    if (!button) return;
    const offsets = { ArrowUp: [-1, 0], ArrowDown: [1, 0], ArrowLeft: [0, -1], ArrowRight: [0, 1] };
    if (!offsets[event.key]) return;
    event.preventDefault();
    const [dr, dc] = offsets[event.key];
    const n = state.visibleClasses.length;
    const row = Math.max(0, Math.min(n - 1, Number(button.dataset.row) + dr));
    const col = Math.max(0, Math.min(n - 1, Number(button.dataset.col) + dc));
    const next = $("matrix-table").querySelector(`[data-row="${row}"][data-col="${col}"]`);
    if (next) { selectPair(next.dataset.left, next.dataset.right); next.focus(); }
  });
  $("scenario-select").addEventListener("change", (event) => chooseScenario(event.target.value));
  $("resolution-select").addEventListener("change", renderScenarioTrace);
  $("scenario-overlay").addEventListener("change", (event) => { state.overlay = event.target.checked; renderMatrix(); renderPair(); });
  $("copy-hash").addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(state.data?.dataset_sha256 || "");
      $("copy-hash").textContent = "Copied";
      $("copy-status").textContent = "Dataset hash copied.";
      setTimeout(() => $("copy-hash").textContent = "Copy", 1800);
    } catch {
      $("copy-status").textContent = "Copy unavailable. Select the displayed hash to copy it manually.";
      $("copy-hash").textContent = "Select hash to copy";
    }
  });
  loadData();
})();
