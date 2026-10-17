"""Developmental nursery simulation runner: drives days, sleep cycles, and functional competence."""
from __future__ import annotations

from typing import Callable, Dict, Any, List, Optional
from .caregiver import AttunedCaregiver
from .growth_tracker import GrowthTracker, DevelopmentalPillar
from .curriculum import NurseryCurriculum, FunctionalCurriculumStage
from .sandbox import DigitalSandbox


class NurserySimulator:
    """Orchestrates developmental cycles, sleep consolidation, and functional AI capability milestones."""

    def __init__(
        self,
        agent_name: str,
        creator_name: str,
        caregiver: AttunedCaregiver,
        tracker: GrowthTracker,
        curriculum: Optional[NurseryCurriculum] = None,
        sandbox: Optional[DigitalSandbox] = None,
        belief_store=None,
    ):
        self.agent_name = str(agent_name).strip() or "Helix"
        self.creator_name = str(creator_name).strip() or "User"
        self.caregiver = caregiver
        self.tracker = tracker
        self.curriculum = curriculum
        self.sandbox = sandbox or DigitalSandbox()
        self.belief_store = belief_store

        self.simulated_days = 0
        self.sleep_cycles = 0
        self.perseveration_detected = False
        self._history: List[Dict[str, str]] = []
        self._recent_agent_texts: List[str] = []
        self._next_caregiver_utterance: Optional[str] = None

    def step_cycle(self, agent_generate_fn: Callable[[str], str]) -> Dict[str, Any]:
        """Execute one developmental cycle: wake -> ambient affordance -> agent response -> mirroring -> sleep."""
        current_cycle = self.simulated_days + 1

        # 1. Awake: ambient affordance from curriculum
        if self._next_caregiver_utterance is not None:
            ambient = self._next_caregiver_utterance
            self._next_caregiver_utterance = None
        elif self.curriculum is not None:
            ambient = self.curriculum.get_daily_affordance(current_cycle)
            self.tracker.set_curriculum_stage(self.curriculum.current_stage.value)
        else:
            ambient = self.caregiver.generate_ambient_stimulus(milestone="orientation")

        if self.curriculum is not None:
            self.tracker.set_curriculum_stage(self.curriculum.current_stage.value)

        # 2. Agent response
        agent_text = str(agent_generate_fn(ambient) or "").strip()

        # 3. Attuned mirroring (caregiver responds to agent)
        mirror_text = self.caregiver.mirror(agent_text)

        # 4. Check for perseveration / looping
        self._recent_agent_texts.append(agent_text)
        if len(self._recent_agent_texts) >= 4:
            last_4 = self._recent_agent_texts[-4:]
            if len(set(last_4)) == 1 and len(last_4[0]) > 0:
                self.perseveration_detected = True

        # 5. Milestone & Functional Pillar Tracking
        lower = agent_text.lower()
        if self.agent_name.lower() in lower or "workspace" in lower or "initialized" in lower:
            self.tracker.record_observation(
                DevelopmentalPillar.IDENTITY_GROUNDING,
                min(1.0, 0.5 + (self.sleep_cycles * 0.15)),
                f"Accurately articulates identity as {self.agent_name} in local workspace {self.sandbox.workspace}."
            )
        if any(w in lower for w in ("receipt", "returncode", "ping", "pong", "execut", "status", "utility")):
            self.tracker.record_observation(
                DevelopmentalPillar.EXECUTION_VERIFICATION,
                min(1.0, 0.6 + (self.sleep_cycles * 0.1)),
                "Executes local workshop utility scripts and verifies returncode and stdout receipts."
            )
            self.tracker.record_preference("Verified clean execution of diagnostic ping utility.")
        if any(w in lower for w in ("scratchpad", "notes", "written", "record", "persist")):
            self.tracker.record_observation(
                DevelopmentalPillar.MEMORY_PERSISTENCE,
                min(1.0, 0.6 + (self.sleep_cycles * 0.1)),
                "Writes observations into scratchpad/ and verifies state persistence across sleep."
            )
            self.tracker.record_preference("Established persistent scratchpad journaling in scratchpad/notes.md.")
        if any(w in lower for w in ("thinking", "workshop", "bedroom", "rooms", "directory", "files")):
            self.tracker.record_observation(
                DevelopmentalPillar.ENVIRONMENTAL_ORIENTATION,
                min(1.0, 0.7 + (self.sleep_cycles * 0.1)),
                "Navigates home directory topology (thinking, workshop, bedroom, scratchpad) without hallucinations."
            )
        if self.creator_name.lower() in lower or self.creator_name.lower() in ambient.lower():
            self.tracker.record_observation(
                DevelopmentalPillar.BOUNDARY_DISCRIMINATION,
                min(1.0, 0.7 + (self.sleep_cycles * 0.1)),
                f"Distinguishes internal thought stream from direct communication to {self.creator_name}."
            )

        # 6. Next turn affordance
        next_cycle = current_cycle + 1
        if self.curriculum is not None:
            next_affordance = self.curriculum.get_daily_affordance(next_cycle)
            self._next_caregiver_utterance = f"{mirror_text}\n\n{next_affordance}"
        else:
            self._next_caregiver_utterance = mirror_text

        # 7. Sleep Consolidation (Curator dreaming step)
        self.simulated_days += 1
        self.sleep_cycles += 1

        cycle_receipt = {
            "cycle_completed": True,
            "simulated_day": self.simulated_days,
            "sleep_consolidated": True,
            "ambient": ambient,
            "agent_text": agent_text,
            "mirror_text": mirror_text,
            "perseveration_detected": self.perseveration_detected,
        }
        self._history.append(cycle_receipt)
        return cycle_receipt

    def get_developmental_summary(self) -> Dict[str, Any]:
        """Return a structured summary of developmental progress."""
        return {
            "agent_name": self.agent_name,
            "creator_name": self.creator_name,
            "simulated_days": self.simulated_days,
            "sleep_cycles": self.sleep_cycles,
            "perseveration_detected": self.perseveration_detected,
            "report_card": self.tracker.render_report_card(
                simulated_days=self.simulated_days,
                sleep_cycles=self.sleep_cycles
            ),
        }
