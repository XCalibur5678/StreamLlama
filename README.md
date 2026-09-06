# StreamLlama

StreamLlama is a small Streamlit interface for chatting with models served by [Ollama](https://ollama.com/). In normal use, prompts and responses are sent only to the Ollama service running on the user's machine. Installing Ollama or downloading a model does require network access unless those dependencies are already available.

## Current status

The prototype currently provides:

- A model selector populated from `ollama list`
- Streaming assistant responses
- In-memory chat history for the current Streamlit session
- A reset-chat action
- Optional bootstrap scripts for installing Ollama and the default `phi3` model

The bootstrap scripts are convenience helpers, not a substitute for a supported installer. Review them before running them with administrator privileges.

## Installation

### 1. Install Ollama

Install Ollama using its official installer, or review one of the repository's platform helpers:

- Linux/macOS: `preload.sh`
- Windows PowerShell: `preload.ps1`

The helpers install Ollama and download `phi3`; they may require administrator privileges. If Ollama is already installed, make sure the Ollama service is running.

### 2. Install Python dependencies

Use a virtual environment where possible:

```shell
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows PowerShell
# .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### 3. Start StreamLlama

```shell
streamlit run app.py
```

Open the URL printed by Streamlit. The Ollama API is expected at its default local endpoint. To use a different endpoint, configure Ollama according to its documentation before starting the app.

## Development plan

The goal is to turn the prototype into a reliable, installable local-first desktop-style chat application without compromising the simple Streamlit experience.

### Phase 0 — Stabilize the current prototype

1. **Define supported environments**: document tested Python, Streamlit, Ollama, and operating-system versions.
2. **Improve startup diagnostics**: distinguish a missing Ollama executable, a stopped service, an empty model list, and an API/version error. Provide a recovery step for each case.
3. **Handle model availability**: show a useful empty state and allow the user to refresh the model list after installing a model.
4. **Make session behavior explicit**: preserve the selected model when possible, reset history when requested, and avoid losing the current conversation during recoverable errors.
5. **Add automated tests** for model-list normalization, error handling, message construction, and the streaming response adapter. Keep Ollama calls behind a small client boundary so tests do not require a running daemon.

**Exit criteria:** a new user can diagnose the three most common startup failures from the UI, and the test suite passes without Ollama installed.

**Recommended first implementation slice:** extract an `OllamaClient` with `list_models()` and `stream_chat()` methods, add a mocked test suite for it, then update `app.py` to use the client. This gives the project a testable seam without changing the user-facing workflow and makes the later health-check and endpoint work substantially lower risk.

### Phase 1 — Improve the chat experience

1. Add model metadata and configurable generation options such as temperature, context length, and maximum tokens.
2. Add stop/cancel behavior for long generations and show a clear in-progress state.
3. Render Markdown safely and consistently, including code blocks and copy-friendly output.
4. Add conversation actions: rename, clear, export to JSON/Markdown, and import a prior conversation.
5. Add an optional system prompt and make it clear which model and settings produced each response.
6. Add a compact settings area rather than placing operational controls in the main chat flow.

**Exit criteria:** users can configure a conversation, stop a generation, and export/import it without editing files manually.

### Phase 2 — Make installation and operations safe

1. Replace privileged, platform-specific auto-install behavior with documented, opt-in setup steps. Never overwrite system directories silently.
2. Make model bootstrap configurable instead of hard-coding `phi3`; support checking, pulling, and removing models through explicit user actions.
3. Pin only direct application dependencies and validate the dependency set on supported Python versions. Avoid bundling unnecessary CUDA/PyQt packages in the default requirements file.
4. Add a health check for the Ollama endpoint and a configurable endpoint setting, with local-only defaults.
5. Add structured logging that does not record prompts or responses by default.
6. Add CI for formatting/linting, unit tests, and a smoke test that uses a mocked Ollama client.

**Exit criteria:** setup is reversible and documented, the default install is suitable for CPU-only machines, and no user content is logged by default.

### Phase 3 — Package the application

1. Extract UI, Ollama client, configuration, and conversation storage into separate modules.
2. Add a versioned configuration format with migrations for future releases.
3. Package the app for the supported platforms, with a clear first-run flow and an uninstall path.
4. Add accessibility checks, keyboard-friendly controls, and responsive layouts.
5. Publish release notes and a support matrix for Python, Ollama, and operating systems.

**Exit criteria:** a non-developer can install, update, configure, and remove StreamLlama using documented steps.

## Design principles

- **Local first:** do not send prompts to third-party services by default.
- **Explicit network actions:** model downloads and updates should be visible and user initiated.
- **Least privilege:** do not require administrator access for normal app usage.
- **Recoverable failures:** an unavailable model or daemon should produce guidance, not a traceback.
- **Small, testable boundaries:** keep Streamlit rendering separate from Ollama communication and persistence.
- **Incremental delivery:** each phase should leave the existing chat usable.

## Contributing

Before opening a change, run the relevant tests and start the app against a local Ollama instance. Changes that affect installation scripts should be tested on the target operating system and should document required privileges and network access.

## Demo

Video demo: <https://youtu.be/4QTL_lFeVTE>

## License

See [LICENSE](LICENSE).
