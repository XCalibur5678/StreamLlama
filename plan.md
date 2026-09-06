# StreamLlama Desktop Application Plan

## 1. Product direction

StreamLlama will be redesigned as a native Linux desktop application for chatting with locally running Ollama models.

This is a new application built around the same local-first idea as the current Streamlit prototype. The existing Streamlit app is not the target architecture for the desktop release.

The application will:

- Run as a native Linux desktop app.
- Connect to an Ollama service already installed and managed by the user.
- Never install Ollama automatically.
- Never download models automatically.
- Store conversations locally on the user's machine.
- Support multiple conversations and model selection.
- Avoid sending prompts or responses to third-party cloud services by default.

## 2. Technology choice

Use **Tauri + React + TypeScript** rather than React Native.

### Rationale

- Tauri is designed for desktop applications and Linux packaging.
- React and TypeScript provide a mature UI and testing ecosystem.
- Rust is suitable for local persistence, filesystem access, HTTP integration, and desktop-specific behavior.
- Tauri provides a clean boundary between the web UI and native application capabilities.
- React Native Linux has a smaller ecosystem and adds complexity without a clear advantage for a Linux-only application.

### Proposed stack

- Desktop shell: Tauri
- Frontend: React and TypeScript
- UI: a lightweight component library or a small Tailwind-based design system
- Native/application layer: Rust commands and events in Tauri
- Persistence: SQLite
- Ollama integration: local HTTP API through the Rust layer
- Initial packaging target: Linux AppImage
- Possible follow-up package: Debian `.deb`

## 3. MVP scope

### 3.1 First-run and Ollama setup

- Detect whether Ollama is reachable.
- Explain clearly when Ollama is missing or not running.
- Provide manual installation/startup instructions or links.
- Do not install Ollama automatically.
- Do not download models automatically.

### 3.2 Model management

- Fetch installed models from Ollama.
- Refresh the model list.
- Select the model for a conversation.
- Show a useful empty state when no models are installed.
- Explain when a previously selected model has been removed.
- Store the selected model per conversation rather than globally.

### 3.3 Multi-chat

- Create a conversation.
- Switch between conversations.
- Rename conversations.
- Delete conversations with confirmation.
- Persist conversations locally.
- Sort conversations by recent activity.
- Restore the last selected conversation on startup.

### 3.4 Chat interface

- Display user and assistant messages.
- Stream assistant responses into the UI.
- Render Markdown consistently.
- Render code blocks with copy functionality.
- Stop an in-progress generation.
- Retry the last assistant response.
- Clear or reset the current conversation.
- Preserve partial output when a generation is interrupted, marking it as interrupted rather than silently deleting it.

### 3.5 Error handling

Handle the following without exposing raw tracebacks as the primary user experience:

- Ollama is not installed or is not reachable.
- Ollama is stopped.
- No models are installed.
- The selected model no longer exists.
- Request timeout.
- Generation interruption.
- Malformed or unexpected Ollama responses.
- Local database read/write failures.

## 4. Proposed architecture

```text
React UI
   |
   | Tauri invoke/events
   v
Rust application layer
   |
   +-- Ollama HTTP client
   +-- SQLite repository
   +-- Application settings
   +-- Streaming event bridge
```

The frontend should not connect directly to `localhost`. The Rust/Tauri layer should own the Ollama connection and expose controlled commands and events to React.

Suggested command boundaries:

```text
list_models()
check_ollama_status()
create_chat()
list_chats()
load_chat(chat_id)
rename_chat(chat_id, title)
delete_chat(chat_id)
send_message(chat_id, content)
stop_generation(chat_id)
retry_message(message_id)
```

For streaming, Rust should emit incremental response events to React. The frontend should update the current assistant message as chunks arrive rather than repeatedly polling the backend.

Keep Ollama communication behind one Rust module so Ollama API changes do not spread throughout the UI.

## 5. Local persistence

Use SQLite from the first implementation rather than adding temporary storage that will need to be replaced later.

### Initial schema

```text
conversations
-------------
id
title
model
created_at
updated_at

messages
--------
id
conversation_id
role
content
created_at
status
```

Potential future fields:

```text
conversations:
- system_prompt
- temperature
- context_length

messages:
- token_count
- error_message
- generation_duration
```

Use migrations from the first version. Store the database in the standard Linux application-data location and document how users can back it up.

The application must not log prompts or responses by default.

## 6. Dependency strategy

The current Python dependency set belongs to the Streamlit prototype and should not be expanded for the new application. It contains unnecessary heavyweight packages, including Streamlit, PyQt5, PyTorch, CUDA libraries, Triton, and NVIDIA runtime packages.

For the redesigned application:

- React dependencies belong in `package.json`.
- Rust dependencies belong in `src-tauri/Cargo.toml`.
- Python dependencies should be removed unless a separate migration or development tool requires them.
- Do not bundle CUDA, PyTorch, or model-runtime dependencies; Ollama manages model execution.
- Keep direct dependencies minimal.
- Avoid manually pinning every transitive dependency.
- Commit and use the frontend and Rust lockfiles.
- Add CI installation and build checks to detect dependency drift.

The old `requirements.txt` should eventually be removed or clearly marked as legacy when the new application structure is introduced.

## 7. Implementation phases

### Phase 1 — Project foundation

- Create the Tauri, React, and TypeScript project.
- Establish the Linux development workflow.
- Set up formatting, linting, type checking, and tests.
- Create the basic application shell and navigation.
- Define the SQLite schema and migration mechanism.
- Remove the old Python dependency path from the new application workflow.

**Deliverable:** a development build with an empty chat layout and an initialized local database.

### Phase 2 — Ollama connectivity

- Implement Ollama status detection.
- Implement model listing.
- Add loading, empty, and error states.
- Add model refresh.
- Add a manual setup/help screen for missing Ollama.

**Deliverable:** the app reliably detects Ollama and displays installed models without installing anything automatically.

### Phase 3 — Single conversation

- Implement sending a message.
- Stream assistant output into the UI.
- Persist messages.
- Add stop and retry behavior.
- Handle failures without losing the user's message.

**Deliverable:** one fully functional persisted conversation.

### Phase 4 — Multi-chat MVP

- Create, select, rename, and delete conversations.
- Associate a model with each conversation.
- Restore the last selected conversation on startup.
- Sort conversations by recent activity.
- Add safeguards around deletion.

**Deliverable:** complete multi-chat MVP.

### Phase 5 — Linux packaging

- Build a production Linux package.
- Start with AppImage for broad compatibility.
- Evaluate `.deb` packaging for Debian/Ubuntu users.
- Add an application icon, desktop entry, and version metadata.
- Document installation and removal.
- Test on the explicitly supported distributions.

**Deliverable:** a user can download, install, launch, and remove the application without Python or Node.js installed.

### Phase 6 — Stabilization

- Add unit tests for the Ollama client and persistence layer.
- Add frontend component tests.
- Add end-to-end tests using a mocked Ollama service.
- Test interrupted streams and application restarts.
- Document supported Linux distributions and Ollama requirements.
- Add release notes and upgrade/migration handling.

**Deliverable:** a reproducible, supportable first release.

## 8. Explicitly out of scope for the MVP

- Automatic Ollama installation.
- Automatic model downloads.
- Cloud model providers.
- Accounts and authentication.
- Cross-device synchronization.
- Plugin or tool systems.
- Image or multimodal support.
- Complex generation settings.
- Bundling the Ollama server or model files.
- A large theme/customization system.

These can be reconsidered after the core local chat experience is reliable.

## 9. Key decisions to confirm early

1. **Model selection:** use per-conversation selection.
2. **Database location:** use the standard Linux application-data directory.
3. **Backups:** document manual database backup and restore before introducing sync.
4. **Stream cancellation:** retain partial responses and mark them interrupted.
5. **Distribution targets:** define the initial supported Linux distributions before packaging.
6. **Ollama API boundary:** keep all Ollama communication inside one Rust module.

## 10. First milestone

Build a Tauri/React Linux shell with SQLite persistence and Ollama status/model detection, without implementing installation automation.

The first milestone is complete when:

- The app builds and launches on the supported Linux development environment.
- Ollama availability is reported clearly.
- Installed models can be loaded and refreshed.
- A conversation can be created and stored locally.
- The project has no dependency on the old Streamlit runtime.
- Formatting, linting, type checking, and tests run through one documented command.
