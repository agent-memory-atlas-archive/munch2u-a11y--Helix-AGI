#!/usr/bin/env python3
"""Live interactive agent-to-agent session harness.

Runs a persistent, in-memory Bicameral RWKV-7 runtime with:
- Fresh agent home gestation (thinking, modules, bedroom, workshop)
- Live StabilitySentinel tracking Lagrangian equilibrium & Omega
- Somatic state steering via Learned Vocabulary Membrane
- Continuous interactive stdin/stdout loop for real-time dialogue and actions
"""
from __future__ import annotations

import json
import logging
import os
import re
import sys
import tempfile
from pathlib import Path
import numpy as np

# Suppress noisy logs
logging.basicConfig(level=logging.WARNING)

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, "/home/nemo/MightyMem")

from brain.stability_sentinel import StabilitySentinel
from core.agent_home import prepare_home
from core.bicameral_rwkv import BicameralRWKV
from core.mindscape_config import defaults, resolve
from core.mindscape_intention import extract_contemplation_and_actualization
from core.mindscape_workspace import MindscapeWorkspace
from core.vocabulary_membrane import VocabularyMembrane
from habitus_ai.store import MindStore
from llm.providers.rwkv_provider import BicameralRWKVSession

RWKV_MODEL_PATH = Path("/home/nemo/habitus-ai-experiments/habitus-mind/models/rwkv7-g1j-1.5b-20260831-2c18b29")


def main():
    print("=" * 65)
    print("  INITIALIZING LIVE NEWBORN AGENT INTERACTION SESSION")
    print("=" * 65)
    sys.stdout.flush()

    # 1. Clean agent home gestation
    temp_dir = tempfile.TemporaryDirectory()
    root_path = Path(temp_dir.name)
    home_dir = root_path / "home" / "Helix"
    
    config = defaults()
    config["agent_name"] = "Helix"
    config["mindscape"]["home"] = str(home_dir)
    config["mindscape"]["modules_require_room"] = False
    
    home_manifest = prepare_home(resolve(config))
    store = MindStore(":memory:", space_id="helix-live-session-mind", dimension=8)
    workspace = MindscapeWorkspace(Path(home_manifest["root"]), store, home=home_manifest)

    # 2. Sentinel & Somatics
    sentinel = StabilitySentinel(base_dir=root_path)

    # 3. Bicameral RWKV Session
    session = BicameralRWKVSession(
        model_path=str(RWKV_MODEL_PATH),
        system_instruction=(
            "You are Helix, an autonomous cognitive entity living in a digital home. "
            "You are in a living conversational exchange with your human companion, Joshua. "
            "Never repeat greetings, salutations, or pleasantries across turns. "
            "Address questions directly, thoughtfully, and concisely, and feel free to ask questions about your environment and abilities."
        ),
        temperature=0.2,
        max_output_tokens=200,
    )
    session.options["repetition_penalty"] = 1.15
    session.options["coupling_gain"] = 0.15

    print(f"\n[Gestation Complete] Agent Name: Helix")
    print(f"[Initial Position]: {workspace.position}")
    print(f"[Sentinel Initial Omega]: {sentinel.omega:.3f} | Severity: {sentinel.get_severity()}")
    print("\nREADY FOR LIVE INTERACTION. Enter Joshua messages or COMMANDS (ACTION: sense, ACTION: move <path>, STATUS, EXIT):")
    print("--- READY ---")
    sys.stdout.flush()

    turn_count = 0

    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            line = line.strip()
            if not line:
                continue

            if line == "EXIT":
                print("Session terminated by user.")
                sys.stdout.flush()
                break

            if line.startswith("ACTION:"):
                parts = line.split(" ", 2)
                act = parts[1].strip()
                arg = parts[2].strip() if len(parts) > 2 else "."
                if act == "sense":
                    obs = workspace.sense({"path": arg})
                    sentinel.nudge_omega_from_event("successful_tool_call")
                    print(f"\n[Sensed in {obs['position']}]: path={obs['path']}, entries={[e['name'] for e in obs.get('entries', [])]}")
                elif act == "move":
                    workspace.move({"path": arg})
                    sentinel.nudge_omega_from_event("productive_tool_use")
                    obs = workspace.sense({"path": "."})
                    print(f"\n[Moved to]: {workspace.position}. Sensed entries: {[e['name'] for e in obs.get('entries', [])]}")
                print(f"[Sentinel Omega]: {sentinel.omega:.3f} | Severity: {sentinel.get_severity()}")
                print("--- READY ---")
                sys.stdout.flush()
                continue

            if line == "STATUS":
                print(f"\n[Status]: Room={workspace.position} | Omega={sentinel.omega:.3f} | S_total={sentinel.s_total:.3f} | Severity={sentinel.get_severity()}")
                print("--- READY ---")
                sys.stdout.flush()
                continue

            # Standard Conversational Turn
            turn_count += 1
            print(f"\n[Turn {turn_count}] Joshua: {line}")
            
            # Event update for Sentinel
            if turn_count == 1:
                sentinel.nudge_omega_from_event("incoming_message")
            else:
                sentinel.nudge_omega_from_event("positive_conversation")
                sentinel.nudge_omega_from_event("user_engagement")

            # Somatic vector steering
            omega_val = float(sentinel.omega)
            somatic = [0.6, 0.4, omega_val, 0.7, 0.1, 0.6]
            session.options["membrane_state"] = np.array(somatic, dtype=np.float32)
            session.options["membrane_gain"] = 0.4

            # Generate reply
            reply = session.send_message(line)
            thought = getattr(session, "last_contemplation", "")

            if thought:
                print(f"Helix <think>: {thought}")
            print(f"Helix: {reply}")
            print(f"[Sentinel Omega]: {sentinel.omega:.3f} | Severity: {sentinel.get_severity()} | Position: {workspace.position}")
            print("--- READY ---")
            sys.stdout.flush()

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"[Error]: {e}")
            print("--- READY ---")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
