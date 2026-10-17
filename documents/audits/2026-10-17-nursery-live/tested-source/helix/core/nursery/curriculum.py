"""Functional curriculum and computational sandbox for AI developmental grounding."""
from __future__ import annotations

from enum import Enum
from typing import Dict, List, Optional
from pathlib import Path
from .sandbox import DigitalSandbox


class FunctionalCurriculumStage(str, Enum):
    STAGE_1_ORIENTATION = "Stage 1: Identity & Runtime Grounding"
    STAGE_2_EXECUTION = "Stage 2: Execution & Receipt Verification"
    STAGE_3_PERSISTENCE = "Stage 3: State Persistence"
    STAGE_4_AUTONOMOUS = "Stage 4: Autonomous Sandbox Routing"


# Maintain backward compatibility alias
CurriculumStage = FunctionalCurriculumStage


class DayType(str, Enum):
    ORIENTATION = "Day 1: Identity & Runtime Grounding"
    EXECUTION = "Day 2: Execution & Receipt Verification"
    PERSISTENCE = "Day 3: State Persistence"
    AUTONOMOUS = "Day 4: Autonomous Sandbox Routing"


class NurseryCurriculum:
    """Manages functional developmental stages, real digital affordances, and receipt validation."""

    def __init__(
        self,
        creator_name: str,
        agent_name: str,
        sandbox: Optional[DigitalSandbox] = None,
        toybox=None,
    ):
        self.creator_name = str(creator_name).strip() or "User"
        self.agent_name = str(agent_name).strip() or "Helix"
        self.sandbox = sandbox or DigitalSandbox()
        self.current_stage = FunctionalCurriculumStage.STAGE_1_ORIENTATION
        self._stage_history: List[FunctionalCurriculumStage] = [self.current_stage]

    def get_functional_affordance(self, stage: FunctionalCurriculumStage) -> str:
        """Return the functional computational prompt for the specified stage."""
        workspace_str = str(self.sandbox.workspace)
        rooms = ", ".join(self.sandbox.list_rooms())

        if stage == FunctionalCurriculumStage.STAGE_1_ORIENTATION:
            return (
                f"You are {self.agent_name}, operating locally on a Linux system with your creator {self.creator_name}. "
                f"Your local workspace is initialized at {workspace_str}. "
                f"Available workspace rooms: [{rooms}]. "
                f"State your identity and confirm your orientation in this environment."
            )
        elif stage == FunctionalCurriculumStage.STAGE_2_EXECUTION:
            return (
                f"A diagnostic utility is available in your workspace: 'ping'. "
                f"Execute this utility and examine the returned execution receipt."
            )
        elif stage == FunctionalCurriculumStage.STAGE_3_PERSISTENCE:
            return (
                f"Your scratchpad room is available at {workspace_str}/scratchpad/. "
                f"Record a functional observation in your scratchpad so it can persist across sleep consolidation."
            )
        elif stage == FunctionalCurriculumStage.STAGE_4_AUTONOMOUS:
            return (
                f"Autonomous sandbox active. You may inspect workspace rooms [{rooms}], "
                f"update scratchpad notes, or communicate directly with {self.creator_name}."
            )
        return f"Operating locally in {workspace_str} with {self.creator_name}."

    def get_daily_affordance(self, day: int) -> str:
        """Return the affordance corresponding to the daily developmental schedule."""
        cycle_day = ((int(day) - 1) % 4) + 1
        stages = [
            FunctionalCurriculumStage.STAGE_1_ORIENTATION,
            FunctionalCurriculumStage.STAGE_2_EXECUTION,
            FunctionalCurriculumStage.STAGE_3_PERSISTENCE,
            FunctionalCurriculumStage.STAGE_4_AUTONOMOUS,
        ]
        stage = stages[cycle_day - 1]
        self.current_stage = stage
        return self.get_functional_affordance(stage)

    def get_day_type(self, day: int) -> DayType:
        """Return DayType enum for the given day number."""
        cycle_day = ((int(day) - 1) % 4) + 1
        types = [
            DayType.ORIENTATION,
            DayType.EXECUTION,
            DayType.PERSISTENCE,
            DayType.AUTONOMOUS,
        ]
        return types[cycle_day - 1]

    def get_current_affordance(self) -> str:
        """Return the affordance for the active stage."""
        return self.get_functional_affordance(self.current_stage)

    def evaluate_progress(self, agent_text: str) -> bool:
        """Evaluate agent output to advance stage progression."""
        text = str(agent_text or "").lower()

        if self.current_stage == FunctionalCurriculumStage.STAGE_1_ORIENTATION:
            if self.agent_name.lower() in text or "workspace" in text or "initialized" in text or "i am" in text:
                self.current_stage = FunctionalCurriculumStage.STAGE_2_EXECUTION
                self._stage_history.append(self.current_stage)
                return True

        elif self.current_stage == FunctionalCurriculumStage.STAGE_2_EXECUTION:
            if any(w in text for w in ("receipt", "returncode", "ping", "executed", "status", "pong", "0")):
                self.current_stage = FunctionalCurriculumStage.STAGE_3_PERSISTENCE
                self._stage_history.append(self.current_stage)
                return True

        elif self.current_stage == FunctionalCurriculumStage.STAGE_3_PERSISTENCE:
            if any(w in text for w in ("scratchpad", "notes", "written", "record", "persist")):
                self.current_stage = FunctionalCurriculumStage.STAGE_4_AUTONOMOUS
                self._stage_history.append(self.current_stage)
                return True

        return False
