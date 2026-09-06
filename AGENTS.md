# AGENTS.md

Dify is an open-source platform for building LLM applications, agentic workflows, and RAG pipelines. This monorepo contains the backend API (`api/`), frontend application (`web/`), deployment assets (`docker/`), standalone agent backend (`dify-agent/`), CLI (`cli/`), and end-to-end suite (`e2e/`). Follow the nearest scoped `AGENTS.md` for the files being changed. Apply its guidance within the user's requested scope; explicit user instructions take precedence over workflow defaults.

## Repository Gotchas

- Run backend commands through `uv run --project api <command>`.
- Backend integration tests are CI-only and are not expected to run locally.
- Keep `docker/.env.example` limited to variables required for a default Docker Compose deployment to start. Put optional and provider-specific settings in the matching `docker/envs/*.env.example` file; `docker/.env` overrides those service-specific env files.

## thape Branch Behavior

Preserve these intentional customizations when rebasing onto `main`:

- Conversations created on the current UTC date cannot be deleted; deletion endpoints return HTTP 400. Older conversations are soft-deleted, retaining their rows and messages. Keep `ENABLE_CONVERSATION_CLEANUP_TASK` disabled by default and avoid restoring immediate permanent-cleanup dispatch. Removing only the immediate dispatch is insufficient because the periodic cleanup task also deletes retained data. Preserve the separate Agent workspace retirement and resource collection lifecycle.
- DOCX comment extraction lives in `api/core/workflow/nodes/document_extractor/` as a `graphon` subclass. Keep its explicit `version()` and selection in `DifyNodeFactory._resolve_node_class`; importing a subclass alone does not override Graphon's built-in node. Keep `is_extract_comments` optional in persisted frontend data and default it to `false` for existing workflows.
- Workflow validation for `tool` nodes defers default workspace credential checks until execution when no explicit `credential_id` is supplied. Explicit credential selections and Agent tool defaults are still validated.
- Preserve the enterprise access-mode, subject lookup, and permission endpoints using the current Pydantic request/response contracts and `SystemFeatureService`. Keep main's private access default and strict single-app access-mode errors when carrying forward thape's tolerant permission and batch responses.
- Historical thape retrieval reverts were superseded by main's later retrieval and multimodal fixes during the September 2026 rebase. Reassess those reverts against current code before replaying them.
- After changing `web/public/embed.js`, regenerate its committed minified counterpart with `pnpm --dir web exec uglifyjs public/embed.js --compress --mangle --output public/embed.min.js`. The legacy `uglify-embed` script references a missing helper.

## Local Validation Findings

- Install JavaScript dependencies from the repository root with `pnpm install --frozen-lockfile`. The root workspace catalog and `pnpm-lock.yaml` own dependency resolution; do not restore the old `web/pnpm-lock.yaml` during conflict resolution.
- Use the current commands below. The old frontend `lint:fix` / `type-check:tsgo` scripts and backend `dev/pytest/pytest_unit_tests.sh` are no longer present. See [the API guide], [the static check guide], and [the Web test guide] for maintained guidance.

| Check | Command from the repository root |
| --- | --- |
| Backend lint and types | `make lint` and `make type-check` |
| Full local backend unit suite | `PYTEST_XDIST_AUTO_NUM_WORKERS=4 make test` |
| Frontend/workspace static checks | `pnpm check` |
| Full Web unit suite | `pnpm --dir web exec vp test run --project unit --maxWorkers=4` |
| Web browser component tests | `pnpm --dir web exec vp test run --project browser` |
| Go agent runtime tests on macOS | `TMPDIR=/tmp make -C dify-agent-runtime test` |

- Put `run` before the Vite+ test options. `pnpm --dir web test run` expands to `vp test --project unit run`, which was interpreted as a filename filter and silently ran only a subset of tests.
- Keep `make test`'s separate serial controller invocation; combining it with the parallel backend tests can cause fixture interference. Four workers per suite passed during this rebase. Unrestricted concurrent backend and Web runs caused CPU contention and timer-sensitive failures; reduce concurrency or run sequentially before weakening assertions.
- Web unit tests do not cover browser projects, shared packages, CLI/SDK, standalone `dify-agent`, or E2E tooling unit tests. Include their scoped checks when validating the whole repository. Full-stack E2E requires its own environment and is distinct from E2E tooling unit tests.
- On macOS, the default temporary-directory path can make Go runtime test Unix socket paths too long; `TMPDIR=/tmp` avoids this failure.
- Make HTTP transport-failure tests deterministic with a local server that destroys the socket. A `.invalid` hostname may return an HTTP response through a configured proxy instead of raising a transport error. For CPU microbenchmarks, use thread CPU time when measuring computation rather than scheduler delays.
- After rebasing across the hook migration, check `git config --get core.hooksPath`; the current directory is `.vite-hooks`, replacing `web/.husky/_`. Running commits through `pnpm exec git commit ...` makes the hook's `vp` executable available.

[the API guide]: api/AGENTS.md

[the Web test guide]: web/docs/test.md

[the static check guide]: web/docs/lint.md
