"""Explicit bootstrap intention wire format; this is not a learned RWKV decoder."""
import json
from pathlib import Path
import re


ABILITY_DESCRIPTIONS = {
    "move": "move(path): changes and persists my current folder; its return verifies position and senses that folder's attributes.",
    "sense": "sense(path): reads file/folder attributes and directory entries without opening content or changing my position. A successful sense is not a move or an open.",
    "open": "open(path): reads existing UTF-8 text or extracts a PDF's text, returning complete content and its file hash. It does not OCR images or change my position.",
    "write": "write(path, content): creates a new text file and verifies its bytes by read-back. A missing file can be created; its parent folder must exist. Replacing an existing file also requires expected_sha256 from its actual open/write return.",
    "mkdir": "mkdir(path): creates a directory under an existing parent; it does not move my current position.",
    "run": "run(path, expected_sha256): executes an existing /workshop Python script using its observed hash, automatically activating the sandbox from any room. Only workshop files are writable; network and host/mind files are inaccessible. Returns complete stdout, stderr and exit status.",
    "activate": "activate(module, parameters): reach a remembered module directly from any room: web_search(query), web_read(url), terminal(command), or sleep with empty parameters. Terminal writes only in /workshop. Sleep uses the production dream engine. Returns actual output; module focus ends when its result is consumed or I move, reply, or disengage.",
    "disengage": "disengage(): releases module focus and returns to my surroundings; does not move or undo an action.",
}
ACTIONS = set(ABILITY_DESCRIPTIONS)

FOREGROUND_FORMAT_GUIDANCE = (
    "Return one JSON object. For a reply or private reflection, use the key message with your words as its string value. "
    "For a needed workspace action, use the keys action and arguments, following current ability awareness. "
    "Choose an action only when it advances the current request or inquiry; conversation and recalling what someone "
    "said do not themselves require filesystem sensing. An intention is private and contains no predicted result. "
    "Answer the current question from the available evidence, or take an action that obtains the missing evidence."
)


def foreground_schema(*, intention_required=False):
    """A private wire format, not a provider tool or action authorization.

    Granite chooses between an intention and prose. The native controller
    still decides whether a proposed action can execute.
    """
    variants = []
    for action in sorted(ACTIONS):
        properties = {"path": {"type": "string"}}
        required = ["path"]
        if action == "write":
            properties["content"] = {"type": "string"}
            required.append("content")
        if action in {"write", "run"}:
            properties["expected_sha256"] = {"type": "string"}
        if action == "activate":
            properties = {"module": {"enum": ["web_search", "web_read", "terminal", "sleep"]},
                          "parameters": {"type": "object", "additionalProperties": {"type": "string"}}}
            required = ["module", "parameters"]
        elif action == "disengage":
            properties, required = {}, []
        variants.append({"type": "object", "properties": {
            "action": {"const": action},
            "arguments": {"type": "object", "properties": properties,
                          "required": required, "additionalProperties": False}},
            "required": ["action", "arguments"], "additionalProperties": False})
    if not intention_required:
        variants.append({"type": "object", "properties": {"message": {"type": "string"}},
                         "required": ["message"], "additionalProperties": False})
    return {"oneOf": variants}


def extract_contemplation_and_actualization(raw: str) -> tuple[str, str]:
    """Extracts internal <think>...</think> contemplation and the actualized foreground text."""
    text = (raw or "").strip()
    think_pattern = re.compile(r"<think>(.*?)</think>", re.DOTALL | re.IGNORECASE)
    match = think_pattern.search(text)
    if match:
        contemplation = match.group(1).strip()
        actualized = think_pattern.sub("", text).strip()
    else:
        if text.startswith("<think>"):
            contemplation = text[len("<think>"):].strip()
            actualized = ""
        else:
            contemplation = ""
            actualized = text

    # Strip any residual role prefixes like Assistant: or Helix: from actualized
    actualized = re.sub(r"^(?:Assistant|Helix|AI):\s*", "", actualized, flags=re.IGNORECASE).strip()
    return contemplation, actualized


def decode_foreground(raw):
    """Decode only a completed foreground generation; never inspect input data."""
    contemplation, text = extract_contemplation_and_actualization(raw)

    if not text and contemplation:
        return "", "contemplation"

    try:
        value = json.loads(text)
        if isinstance(value, dict) and set(value) == {"message"}:
            if not isinstance(value["message"], str) or not value["message"].strip():
                raise ValueError("foreground message is empty or invalid")
            return value["message"], "message"
        if isinstance(value, dict) and "action" in value:
            if value.get("action") == "read":
                value["action"] = "open"
            wire = "<intention>" + json.dumps(value, ensure_ascii=False) + "</intention>"
            parse_intention(wire)
            return wire, "intention"
    except (json.JSONDecodeError, ValueError):
        pass

    # Check for embedded JSON block with action
    start = text.find("{")
    while start != -1:
        end = text.rfind("}")
        while end > start:
            try:
                candidate = json.loads(text[start:end+1])
                if isinstance(candidate, dict) and "action" in candidate:
                    if candidate.get("action") == "read":
                        candidate["action"] = "open"
                    if candidate.get("action") in ACTIONS:
                        wire = "<intention>" + json.dumps(candidate, ensure_ascii=False) + "</intention>"
                        parse_intention(wire)
                        return wire, "intention"
            except (json.JSONDecodeError, ValueError):
                pass
            end = text.rfind("}", start, end)
        start = text.find("{", start + 1)

    if text:
        return text, "message"
    raise ValueError("foreground message is empty or invalid")


def observation_text(result):
    """Present complete output, error and arguments; keep telemetry in receipts."""
    receipt = result.get("receipt")
    if not receipt:
        return ("The proposed native action did not execute.\n" +
                json.dumps({key: result.get(key) for key in ("action", "status", "error", "verified")},
                           ensure_ascii=False, sort_keys=True))
    observed = {key: receipt[key] for key in ("receipt_id", "arguments", "status", "output", "error", "verified")}
    return (f"My {result['action']} action returned {receipt['status']}. "
            "This attempt has finished; its requested arguments are not a new intention.\n" +
            json.dumps(observed, ensure_ascii=False, sort_keys=True))


def requires_workspace_observation(message):
    """Conservative bootstrap for explicit workspace imperatives, not authority.

    This only withholds an ungrounded completion. It selects no path or action
    and cannot authorize an actuator. Broader semantic task understanding is a
    separate learned-controller requirement.
    """
    text = message.split("They said:", 1)[-1].strip().strip('"')
    imperative = re.match(r"^(?:please\s+)?(?:move|sense|feel|touch|open|read|write|create|make|run|execute)\b", text, re.I)
    workspace = re.search(r"(?:\b(?:file|files|folder|directory|workspace|script)\b|/\w|\.(?:md|pdf|py)\b)", text, re.I)
    return bool(imperative and workspace)


def extract_workspace_obligations(messages):
    """Extract required ability categories and target paths from workspace imperatives.

    Returns:
      {
        "required_abilities": set[str],  # e.g. {"move", "sense", "open", "write", "run"}
        "target_paths": set[str],        # e.g. {"/inbox", "/output/calc.py"}
      }
    """
    abilities = set()
    paths = set()
    path_pattern = re.compile(r"(?:/|[a-zA-Z0-9_\-\.]+/)[a-zA-Z0-9_\-\.]+|\b[a-zA-Z0-9_\-]+\.(?:md|pdf|py|txt|json)\b")

    for msg in messages:
        text = str(msg).split("They said:", 1)[-1].strip().strip('"')
        lower = text.lower()

        for p in path_pattern.findall(text):
            cleaned_p = p.strip(",. ;\"'")
            if cleaned_p:
                paths.add(cleaned_p)

        if re.search(r"\b(?:move|cd|navigate|go to)\b", lower):
            abilities.add("move")
        if re.search(r"\b(?:sense|feel|touch|list|scan|inspect attributes)\b", lower):
            abilities.add("sense")
        if re.search(r"\b(?:open|read|extract|view contents)\b", lower):
            abilities.add("open")
        if re.search(r"\b(?:write|create|make|save|amend)\b", lower):
            abilities.add("write")
        if re.search(r"\b(?:run|execute)\b", lower):
            abilities.add("run")

    return {
        "required_abilities": abilities,
        "target_paths": paths,
    }


def check_obligations_satisfied(obligations, observations, current_position="."):
    """Check if the extracted obligations are satisfied by executed observations.

    Enforces that:
    - A directory sense does not satisfy a requested open or move.
    - A run failure does not satisfy a requested write.
    - An observed error for a specific target settles the obligation to observe it.
    """
    required = set(obligations.get("required_abilities", ()))
    if not required:
        return True

    observed_abilities = set()
    observed_errors_on_target = set()
    norm_pos = str(current_position or ".").strip("/").lower()

    for obs in (observations or []):
        action = obs.get("action")
        path = str(obs.get("path", "")).strip().lower()
        status = obs.get("status")
        receipt = obs.get("receipt", {})
        verified = bool(receipt.get("verified", status == "completed"))
        is_completed = (status == "completed" or (verified and status not in {"error", "not_completed"}))

        if is_completed:
            observed_abilities.add(action)
        elif status in {"error", "not_completed"} or not verified:
            if action in {"open", "sense"}:
                # An observed error attempting to open/sense an absent target settles the observation
                observed_abilities.add(action)
                observed_errors_on_target.add((action, path))
            elif action:
                observed_errors_on_target.add((action, path))

    if "move" in required:
        target_dirs = {p.strip("/").lower() for p in obligations.get("target_paths", ()) if "." not in Path(p).name}
        moved_to_target = False
        if "move" in observed_abilities:
            moved_to_target = True
        elif target_dirs and any(norm_pos == td or norm_pos.endswith(td) for td in target_dirs):
            moved_to_target = True

        if not moved_to_target:
            return False

    for ability in required:
        if ability == "move":
            continue
        if ability not in observed_abilities:
            return False

    return True


def step_guidance_for_pending(obligations, observations, current_position="."):
    """Generate precise step-by-step guidance for Granite on the next needed action."""
    required = set(obligations.get("required_abilities", ()))
    completed_actions = {
        obs.get("action") for obs in (observations or [])
        if obs.get("status") in {"completed", "success"} or (
            bool(obs.get("verified") or obs.get("receipt", {}).get("verified")) and obs.get("status") not in {"error", "not_completed"}
        )
    }
    # For open/sense, an error on an absent target settles the observation attempt
    settled_actions = set(completed_actions)
    for obs in (observations or []):
        if obs.get("action") in {"open", "sense"} and obs.get("status") in {"error", "not_completed"}:
            settled_actions.add(obs.get("action"))

    guidance_parts = []
    norm_pos = str(current_position or ".").strip("/").lower()
    target_dirs = [p for p in obligations.get("target_paths", ()) if "." not in Path(p).name]
    target_files = [p for p in obligations.get("target_paths", ()) if "." in Path(p).name]
    target_file = target_files[0] if target_files else "/workshop/experiment.py"

    known_hashes = {}
    for obs in (observations or []):
        h = obs.get("sha256") or obs.get("receipt", {}).get("sha256")
        if h:
            p = obs.get("path") or obs.get("receipt", {}).get("path")
            if p:
                known_hashes[Path(p).name] = h

    target_name = Path(target_file).name
    sha_val = known_hashes.get(target_name)

    if "move" in required and "move" not in settled_actions:
        target_str = f" to {target_dirs[0]}" if target_dirs else ""
        guidance_parts.append(f"Move{target_str} has not yet executed (current position is /{norm_pos or '.'}). Use action 'move'.")

    if "sense" in required and "sense" not in settled_actions:
        guidance_parts.append("Step 1: Inspect the workspace directory first. Use action 'sense' with path '.' to observe existing files.")

    if "open" in required and "open" not in settled_actions:
        if "sense" in settled_actions:
            guidance_parts.append("Use action 'open' on the requested file or a relevant existing file from the actual sense return. My source checkout is outside my home.")
        else:
            guidance_parts.append("Use action 'open' to read file contents and extract information.")

    if "write" in required and "write" not in completed_actions:
        if sha_val:
            guidance_parts.append(f"Step 3: Update the module with action 'write'. Pass path '{target_file}', content, and expected_sha256 '{sha_val}'.")
        else:
            guidance_parts.append(f"Step 3: Create the script with action 'write' at '{target_file}'. Its parent must exist; executable experiments belong in /workshop.")

    if "run" in required and "run" not in completed_actions:
        if "write" in required and "write" not in completed_actions:
            guidance_parts.append("Write the script first before running it.")
        else:
            sha_arg = f" and expected_sha256 '{sha_val}'" if sha_val else " and expected_sha256 from its actual open or write return"
            guidance_parts.append(f"Step 4: Execute the script with action 'run' path '{target_file}'{sha_arg}.")

    if guidance_parts:
        return "Unfinished workspace tasks remain: " + " ".join(guidance_parts)
    return "All workspace actions are verified. Formulate your final response to the user summarizing the verified results."


def parse_intention(text):
    """Only an entire private foreground output can propose a native action.

    Incoming messages, retrieved documents, quoted snippets and prose about an
    action never enter this parser and cannot themselves execute an actuator.
    """
    value = text.strip()
    if not value.startswith("<intention>"):
        return None
    if not value.endswith("</intention>"):
        raise ValueError("private intention is incomplete; nothing ran")
    payload = json.loads(value[len("<intention>"):-len("</intention>")])
    if not isinstance(payload, dict) or set(payload) != {"action", "arguments"}:
        raise ValueError("a private intention requires exactly action and arguments")
    if payload["action"] not in ACTIONS or not isinstance(payload["arguments"], dict):
        raise ValueError("unknown action or invalid arguments")
    arguments = payload["arguments"]
    if payload["action"] == "activate":
        if (set(arguments) != {"module", "parameters"} or not isinstance(arguments["module"], str)
                or not isinstance(arguments["parameters"], dict)
                or not all(isinstance(v, str) for v in arguments["parameters"].values())):
            raise ValueError("activate requires a module name and text parameters object")
        return payload
    if payload["action"] == "disengage":
        if arguments:
            raise ValueError("disengage accepts no arguments")
        return payload
    required = {"path"} | ({"content"} if payload["action"] == "write" else set())
    allowed = required | ({"expected_sha256"} if payload["action"] in {"write", "run"} else set())
    if not required <= set(arguments) or not set(arguments) <= allowed:
        raise ValueError("wrong arguments for the proposed action")
    if not all(isinstance(value, str) for value in arguments.values()):
        raise ValueError("action arguments must be strings")
    return payload


def ability_awareness(root, position):
    return (
        f"My native workspace is {root}; my current position within it is /{'' if position == '.' else position}.\n"
        "These are my installed abilities and their actual effects:\n"
        + "\n".join(ABILITY_DESCRIPTIONS.values()) + "\n"
        "When I need an action, I express one private intention and wait for its actual return. "
        "This takes precedence over an outward speaking impulse. I do not narrate completion in advance. "
        "A request to perform an action calls for performing it, rather than a tutorial or an offer to do it later. "
        "My foreground output uses the message field for prose, or action and arguments for a needed intention. "
        "An intention contains no predicted result or accompanying message: its real return arrives next pulse. "
        "The native controller must select the ability before it executes. Relative paths follow my position; "
        "leading / means my home root. /thinking is quiet; /modules holds operational scripts; "
        "/bedroom holds sleep; /bedroom/closet holds my files; /workshop holds experiments. "
        "Python and terminal execution write only inside /workshop; the host and my mind are outside that sandbox. "
        "After each return I compare its actual effect with the whole unfinished request and take the next needed action. "
        "An error describes that attempted action; I can use another available ability to resolve a missing prerequisite. "
        "My outward reply reports only supported results and any remaining work or actual blocker. "
        "Only actual returned observations establish what was read, written or executed."
    )
