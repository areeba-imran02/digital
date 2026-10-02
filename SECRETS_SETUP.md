# VERITAS secrets setup

No `.env` file is included in this project.

For Streamlit Cloud, open **Settings → Secrets** and add:

```toml
OPENAI_API_KEY = "your-api-key"
VERITAS_AI_MODEL = "gpt-6-luna"
```

The app works without the key using its local evidence engine. With the key present,
VERITAS adds input-specific generative reasoning and natural-language answers.

Never commit an API key to GitHub.
