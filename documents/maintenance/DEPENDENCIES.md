# Dependency profiles and setup paths

Reviewed: October 18, 2026.

The requirements files share package declarations under `requirements/`.
The full installation retains all 32 previously declared package requirements;
`packaging` is now explicit because wizard model detection imports it.

| Entry point | Purpose | Coverage |
|---|---|---|
| `requirements-dev.txt` | Offline maintenance checks | Small test environment, no GUI, models or channels |
| `requirements-wizard.txt` | Open the setup UI | Common utilities plus PyQt6 and WebEngine |
| `requirements.txt` | Compatibility full installation | All existing provider, memory, tool, perception, GUI and channel requirements |
| `requirements-mindscape.txt` | Native runtime installation | Full compatibility profile plus the existing Transformers pin, Torch and safetensors |

The internal files group common, memory, provider, tool, perception, GUI and
channel dependencies. They are shared declarations, not independently certified
runtime installations. The existing full requirements remain the runtime entry
points; selecting one provider does not yet create a minimal runtime environment.

## Guided setup

`./install.sh` checks Python 3.11+ and the chosen virtual environment, installs
the wizard profile, then opens the UI. Full native/neural and provider installs
happen after the user selects a composition. A failed dependency install stops
bootstrap and leaves setup incomplete.

The credentials page offers native Mindscape or the separate Helix provider/tool
composition. Native choices are RWKV and Ollama. Helix also exposes implemented
CLI and hosted adapters. OpenAI and Alibaba key fields and package compatibility
remain available, but those providers are not offered as primary models because
the session factory has no corresponding primary adapters.

The credentials page and Models tab share provider validation. RWKV selections
retain the selected checkpoint; configuration takes precedence over stale
provider values in credentials. Model edits retain existing private channel
credentials. Bootstrap receives the chosen provider, model, data directory and
native source/home paths rather than resetting them through mode selection.
Bootstrap retains all enabled channels instead of reducing them to the primary
channel. Saved legacy configurations without a composition retain Helix behavior.

On Linux without a display, or when Qt cannot be imported, `python -m wizard`
forwards arguments to CLI setup and returns its exit status. For direct CLI setup
without installing Qt, follow the command-line examples in the
[launch guide](../mindscape_launch.md).

## Verification and limits

CI installs the wizard profile on Linux/Python 3.12 and runs offscreen widget and
creation diagnostics. It provisions Linux Qt display libraries explicitly.
Offline Python checks run on 3.11 and 3.12. Dashboard JavaScript request/DOM
checks use Node's built-in test runner and introduce no npm dependencies.

These checks do not certify the full runtime resolver, native weights/source
compatibility, GPU variants, macOS/Windows installation, a visible desktop
session or provider connectivity. Installer and bootstrap subprocesses are
mocked in widget regressions. The existing Transformers pin and recorded native
source manifest remain unchanged; a fully locked native environment is deferred
until verified with the actual dependency checkout and checkpoints. There are
no blanket package upgrades or removed compatibility dependencies.
