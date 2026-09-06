# AGENTS.md

Follow the nearest scoped `AGENTS.md` for the files being changed.

## thape Branch Behavior

- Deleting a conversation created today (UTC) returns HTTP 400; older conversations retain their rows and messages after soft deletion. Keep `ENABLE_CONVERSATION_CLEANUP_TASK=false` and immediate permanent-cleanup dispatch disabled: the periodic sweeper can also erase retained data. Preserve the separate Agent workspace retirement and resource collection lifecycle.
- The DOCX comment extractor in `api/core/workflow/nodes/document_extractor/` needs an explicit `version()` and selection in `DifyNodeFactory._resolve_node_class`. Importing its subclass alone does not override Graphon's built-in node. Missing `is_extract_comments` must mean `false` for existing workflows.
- For workflow `tool` nodes, default workspace credential validation is deferred until execution. Explicit credentials and Agent tool defaults are still validated.
- Enterprise permission and batch responses tolerate invalid/unavailable results. Single-app access-mode errors remain strict, and the default access mode remains private.

## Repository Pitfalls

- Optional/provider Docker settings belong in `docker/envs/*.env.example`; `docker/.env.example` is limited to default startup requirements. Values in `docker/.env` override service-specific env files.
- `uglify-embed` references a missing helper. Regenerate the committed embed bundle with `pnpm --dir web exec uglifyjs public/embed.js --compress --mangle --output public/embed.min.js`.
- Run the full Web unit suite with `pnpm --dir web exec vp test run --project unit`. Appending `run` to `pnpm --dir web test` can interpret it as a filename filter and silently select only part of the suite.
- Keep `make test`'s controller tests in their separate serial invocation to avoid fixture interference. If concurrent full suites cause timer failures, use `PYTEST_XDIST_AUTO_NUM_WORKERS=4 make test` and add `--maxWorkers=4` to the Web command.
- On macOS, use `TMPDIR=/tmp make -C dify-agent-runtime test` to avoid Unix socket path-length failures.
- A `.invalid` hostname can return an HTTP response through a proxy. Test transport failures with a local server that destroys the socket.
- Git hooks now live in `.vite-hooks`; an old `core.hooksPath` pointing at `web/.husky/_` silently misses them. `pnpm exec git commit ...` supplies the hook's `vp` executable.
