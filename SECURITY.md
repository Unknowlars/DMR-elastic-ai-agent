# Security

Do not commit real credentials, local endpoints, raw exports, or private assistant configuration.

Before publishing a fork:

```bash
rg --hidden -g '!.git/*' -g '!old/*' -i '(api[_-]?key|authorization:|bearer |password|secret|token|sk-[A-Za-z0-9]|192\.168\.)' .
```

Rotate any API key that has ever been committed or copied into local notes. If a secret was pushed to a public remote, remove it from git history or publish from a fresh repository.
