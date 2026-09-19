# Provider adapters

These Python standard-library adapters send one benchmark attempt to a selected provider and save its answer, proof files, API records, and token usage. They make no automatic retries and provide no tools or retrieval to the model. Each invocation starts a fresh conversation.

| Provider | Adapter | Credential |
| --- | --- | --- |
| OpenAI Responses API | `openai_responses.py` | `OPENAI_API_KEY` |
| Anthropic Messages API | `anthropic_messages.py` | `ANTHROPIC_API_KEY` |

There is no default model. Set `configuration.model_id` in the harness request, set `INCLUSION_MODEL`, or supply the exact API model ID as `model.version`. That is the precedence order; conflicting configuration and environment IDs are rejected. Use an immutable snapshot where the provider offers one. The adapter records the requested ID and the provider's returned ID; an explicit alias is not automatically an immutable snapshot.

## Check the setup without spending

From the repository root, set `INCLUSION_MODEL` to the exact model you intend to evaluate and make its credential available through the standard environment variable. This check reports presence only and does not contact the provider:

```sh
python3 evaluation/adapters/openai_responses.py --preflight
python3 evaluation/adapters/anthropic_messages.py --preflight
```

`--preflight` exits with code 2 if either the environment model or credential is missing. It does not verify account access, model availability, or provider support for the requested settings.

To inspect the actual prompt and API payload, feed a harness request to `--dry-run`. No credential is needed and no network request occurs. Run it in a disposable output directory, using the adapter's absolute path:

```sh
python3 /absolute/path/inclusion-bench/evaluation/adapters/openai_responses.py \
  --dry-run < /absolute/path/request.json
```

The result is marked `dry_run: true` and earns no evaluation credit. The planned API payload is written beneath `adapter-artifacts/` in the current directory. For a real evaluation, select the adapter as the harness command and declare the model and budgets there; the harness supplies one request per attempt. Running the adapter without `--dry-run` makes provider requests and can incur model charges.

## Harness request

The adapters accept the benchmark task, class catalog, knowledge base, and optional formalization material in the existing request. These fields control execution:

| Field | Meaning |
| --- | --- |
| `model.version` | Exact API model ID, unless overridden as above |
| `configuration.model_id` | Explicit API model ID override |
| `limits.max_output_tokens` | Positive per-attempt generation cap |
| `limits.max_total_tokens_remaining` | Nonnegative remaining input-plus-output budget for the run |
| `limits.remaining_output_tokens` | Optional additional generation cap |
| `time_remaining_seconds` | Remaining wall time for counting and generation together |
| `limits.wall_seconds` | Wall-time fallback if `time_remaining_seconds` is absent |
| `configuration.reasoning_effort` | Optional provider reasoning/effort setting, sent only when supplied |
| `configuration.temperature` | Optional explicit sampling temperature |
| `configuration.input_token_reserve` | Extra input-token allowance; defaults to 0 for OpenAI and 256 for Anthropic |
| `configuration.thinking` | Anthropic only: `adaptive` or `disabled` |
| `configuration.thinking_budget_tokens` | Anthropic only: explicit thinking budget, at least 1,024 and below the available output cap |

Choose settings supported by the selected model. Unsupported settings produce a recorded provider error; the adapter does not silently change the model or retry with different settings. For Anthropic, `thinking` takes precedence over `thinking_budget_tokens` when it is `adaptive` or `disabled`.

Before generation, the adapter calls the provider's input-token counting endpoint with the same prompt and schema. It then sets the generation cap to the smaller of the output limit and the remaining total budget minus input count and reserve. It sends no generation request when that leaves no output budget. OpenAI documents exact input counts; Anthropic describes its count as an estimate, so the reserve provides headroom but cannot guarantee an exact hard cap on the eventual total. Observed overruns are flagged and their answers are not returned as proof candidates. [OpenAI token counting](https://developers.openai.com/api/docs/guides/token-counting), [Anthropic token counting](https://platform.claude.com/docs/en/build-with-claude/token-counting).

The provider enforces the generation limit. Both providers include reasoning tokens within reported output usage; the adapter does not add those tokens again. Anthropic cache-read and cache-creation input tokens are included in the normalized input total. [OpenAI output-token accounting](https://developers.openai.com/api/docs/guides/token-counting), [Anthropic response usage](https://platform.claude.com/docs/en/api/messages/create).

## Results and evidence

The model returns structured JSON containing `status`, exact `claims`, `proof_markdown`, `lean_sources`, and `notes`. The adapter validates that structure, checks catalog IDs and source filenames, and writes natural-language proofs and Lean source to files. It does not execute model-written code or verify the mathematics. A candidate remains subject to the benchmark's proof review. The JSON formats follow [OpenAI Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs) and [Anthropic Structured Outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs).

The adapter emits one JSON object on standard output:

- `status`: `unsolved`, `proof_candidate`, `error`, or `budget_exhausted`.
- `claims`: exact relation objects; empty for errors and exhausted attempts.
- `artifacts`: paths relative to the attempt's working directory.
- `usage`: normalized `input_tokens`, `output_tokens`, `total_tokens`, reasoning detail, and the original provider usage object when available.
- `usage_complete`: whether input and output usage are known.
- `request_made`: whether a generation request was attempted; a counting request alone leaves this false.
- `budget_charge_tokens`: actual total usage when known; the entire remaining allowance when a generation request may have been charged but its usage is unknown.
- `model_requested`, `provider_model`, `response_id`, and `finish_reason`: provider provenance when available.

Unknown usage is `null`, never zero. A timeout cannot guarantee cancellation of generation already running at the provider. Charging the remaining allowance conservatively tells the harness to stop the run instead of spending again. Counting-only failures have zero model-generation charge. HTTP failures, malformed outputs, refusals, and truncated responses retain available artifacts and usage; there are no automatic retries.

Each invocation creates a unique artifact directory containing the harness request, planned request, counting and generation exchanges, returned model text, usage, and adapter result. Successful responses also include a combined transcript; proof candidates include `proof.md` and any `.lean` files. Authorization headers are never logged, known credential strings are redacted from saved content, response bodies are capped at 8 MB, and redirects are not followed. The runner hashes these artifacts when sealing the attempt.

## Local verification

```sh
python3 -m unittest discover -s tests -p test_adapters.py -v
```

The tests use a loopback HTTP server with fake credentials. They cover provider payloads, model IDs, proof artifacts, token accounting, budget reservations, HTTP errors, unknown usage, timeouts, truncation, malformed outputs, filename traversal, offline checks, and credential redaction. They make no external API calls.

For those tests only, `INCLUSION_API_BASE_URL` may select a loopback HTTP endpoint when `INCLUSION_ALLOW_TEST_ENDPOINT=1`. Production requests are restricted to the official provider origin. The adapters do not support arbitrary proxy endpoints or custom inference gateways.
