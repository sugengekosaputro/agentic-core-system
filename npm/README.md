# agentkit-core (npx wrapper)

Thin Node wrapper so you can run agentkit without a manual Python install step:

```sh
npx agentkit init
npx agentkit validate
```

The actual engine is the Python package `agentkit-core` (single source of truth).
This wrapper locates Python 3.10+, installs the package on first run if needed, and
forwards arguments to `agentkit.cli`. If you prefer, install directly:

```sh
pipx install agentkit-core
```
