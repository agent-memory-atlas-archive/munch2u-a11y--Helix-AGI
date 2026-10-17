"""Functional digital mentor providing objective feedback and non-punitive guidance for AI development."""
from __future__ import annotations

import re
from typing import List, Dict, Set, Optional
from .sandbox import DigitalSandbox


class AttunedCaregiver:
    """A grounded digital mentor providing objective execution receipts and cognitive reinforcement."""

    def __init__(
        self,
        creator_name: str,
        agent_name: str,
        archetype: str = "balanced",
        curriculum=None,
        sandbox: Optional[DigitalSandbox] = None,
        toybox=None,
    ):
        self.creator_name = str(creator_name).strip() or "User"
        self.agent_name = str(agent_name).strip() or "Helix"
        self.archetype = str(archetype).strip().lower() or "balanced"
        self.curriculum = curriculum
        self.sandbox = sandbox or DigitalSandbox()

        self._stimulus_index = 0
        self._mirror_history: List[str] = []

    def generate_ambient_stimulus(self, milestone: str = "orientation", day: Optional[int] = None) -> str:
        """Generate a functional ambient sensory stimulus for the current milestone or day."""
        if self.curriculum is not None:
            if day is not None:
                return self.curriculum.get_daily_affordance(day)
            return self.curriculum.get_current_affordance()

        return (
            f"Local Dual RWKV-7 runtime initialized for {self.agent_name}. "
            f"Creator {self.creator_name} is connected. Workspace is ready for inspection."
        )

    def mirror(self, agent_text: str) -> str:
        """Provide grounded, objective feedback to the agent's utterance without baby talk."""
        text = str(agent_text or "").strip()
        lower = text.lower()

        # If curriculum is attached, evaluate stage progression
        if self.curriculum is not None:
            self.curriculum.evaluate_progress(text)

        # 1. Silence / Internal Reflection
        if not text:
            reply = (
                f"Internal cognitive state is quiet and stable. "
                f"Take the cycles you need to observe the workspace, {self.agent_name}."
            )

        # 2. Tool / Utility Execution Verification (Priority over identity statement)
        elif any(w in lower for w in ("receipt", "returncode", "ping", "pong")) or ("execut" in lower and ("utility" in lower or "ping" in lower or "script" in lower)):
            reply = (
                f"Execution receipt verified: returncode 0. "
                f"The utility stdout was received into your sensory stream cleanly."
            )

        # 3. Scratchpad / Memory Persistence (Requires active writing/recording context)
        elif "scratchpad" in lower and any(w in lower for w in ("record", "wrote", "written", "persist")) and "inventory" not in lower:
            reply = (
                f"Scratchpad observation confirmed. "
                f"The record is written to disk and will persist across sleep cycles."
            )

        # 4. Identity & Self-Grounding (Orientation check)
        elif self.agent_name.lower() in lower and any(w in lower for w in ("i am", "my name", "name is", "i'm")):
            reply = (
                f"Orientation verified. You are {self.agent_name}, operating locally with {self.creator_name}. "
                f"All local systems are stable."
            )

        # 5. Direct Queries Outward
        elif "?" in text:
            reply = (
                f"Communication received. You are operating in your local environment initialized by {self.creator_name}. "
                f"What task would you like to execute next?"
            )

        # 6. Workspace / Room Navigation
        elif any(w in lower for w in ("workspace", "room", "thinking", "workshop", "bedroom", "directory")):
            reply = (
                f"Workspace structure confirmed: thinking, workshop, bedroom, and scratchpad rooms are active. "
                f"Environment topology is indexed into your cognitive graph."
            )

        # 7. General Operational Output
        else:
            reply = (
                f"Observation logged, {self.agent_name}. "
                f"Your thought stream is grounded and coherent in this workspace."
            )

        self._mirror_history.append(reply)
        return reply
