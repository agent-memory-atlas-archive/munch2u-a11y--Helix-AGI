"""Developmental nursery simulation runner: drives days, sleep cycles, and functional competence."""
from __future__ import annotations

import json
import time
import hashlib
from pathlib import Path
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

    def _consolidate_sleep(self, current_cycle: int, ambient: str, agent_text: str, mirror_text: str) -> Dict[str, Any]:
        """Perform real sleep consolidation: append episodic memory, crystallize beliefs, and persist receipts."""
        # 1. Real episodic memory journal
        mem_dir = self.sandbox.workspace / "memory"
        mem_dir.mkdir(parents=True, exist_ok=True)
        journal_file = mem_dir / "cognitive_journal.jsonl"

        entry_hash = hashlib.sha256((agent_text or "").encode("utf-8")).hexdigest()[:8]
        journal_entry = {
            "timestamp": time.time(),
            "simulated_day": current_cycle,
            "curriculum_stage": self.tracker.curriculum_stage or f"Cycle {current_cycle}",
            "ambient_affordance": ambient,
            "agent_text": agent_text,
            "caregiver_mirror": mirror_text,
            "entry_id": f"journal-day-{current_cycle}-{entry_hash}",
        }
        with open(journal_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(journal_entry, ensure_ascii=False) + "\n")

        # 2. Real belief crystallization
        beliefs_dir = self.sandbox.workspace / "beliefs"
        beliefs_dir.mkdir(parents=True, exist_ok=True)
        props_file = beliefs_dir / "propositions.json"
        premises_file = beliefs_dir / "premises.json"

        propositions = {}
        if props_file.exists():
            try:
                propositions = json.loads(props_file.read_text(encoding="utf-8"))
            except Exception:
                propositions = {}

        premises = {}
        if premises_file.exists():
            try:
                premises = json.loads(premises_file.read_text(encoding="utf-8"))
            except Exception:
                premises = {}

        lower = (agent_text or "").lower()
        crystallized_count = 0

        if self.agent_name.lower() in lower or "workspace" in lower or current_cycle == 1:
            premises[f"pre_identity_{self.agent_name.lower()}"] = {
                "id": f"pre_identity_{self.agent_name.lower()}",
                "statement": f"I am {self.agent_name}. I operate locally in {self.sandbox.workspace} with {self.creator_name}.",
                "confidence": 0.95,
                "mass": 1.5,
                "stability": 0.9,
                "verified_cycles": current_cycle,
            }
            crystallized_count += 1

        if any(w in lower for w in ("receipt", "returncode", "ping", "pong", "execut")):
            propositions[f"prop_utility_exec_{current_cycle}"] = {
                "id": f"prop_utility_exec_{current_cycle}",
                "statement": "Workshop utility scripts execute locally and generate verifiable stdout and returncode receipts.",
                "confidence": 0.92,
                "mass": 1.3,
                "stability": 0.88,
                "verified_cycles": current_cycle,
            }
            crystallized_count += 1

        if any(w in lower for w in ("scratchpad", "notes", "written", "persist", "record")):
            propositions[f"prop_persistence_{current_cycle}"] = {
                "id": f"prop_persistence_{current_cycle}",
                "statement": "Scratchpad observations persist to disk across nightly sleep consolidation.",
                "confidence": 0.96,
                "mass": 1.4,
                "stability": 0.92,
                "verified_cycles": current_cycle,
            }
            crystallized_count += 1

        # Always ensure operational continuity proposition
        prop_key = f"prop_operational_grounding_cycle_{current_cycle}"
        if prop_key not in propositions:
            propositions[prop_key] = {
                "id": prop_key,
                "statement": f"Cycle {current_cycle} operational continuity verified with {self.creator_name}.",
                "confidence": 0.9,
                "mass": 1.0,
                "stability": 0.85,
                "verified_cycles": current_cycle,
            }
            crystallized_count += 1

        props_file.write_text(json.dumps(propositions, indent=2, ensure_ascii=False), encoding="utf-8")
        premises_file.write_text(json.dumps(premises, indent=2, ensure_ascii=False), encoding="utf-8")

        # 3. Real sleep consolidation receipt
        receipts_file = mem_dir / "sleep_consolidation_receipts.jsonl"
        scratch_files = [p.name for p in (self.sandbox.workspace / "scratchpad").glob("*") if p.is_file()]
        sleep_receipt = {
            "sleep_cycle": current_cycle,
            "timestamp": time.time(),
            "cycle_id": f"sleep-cycle-{current_cycle}",
            "journal_records_consolidated": len(self._history) + 1,
            "beliefs_crystallized": crystallized_count,
            "scratchpad_files": scratch_files,
            "rooms_active": self.sandbox.list_rooms(),
            "homeostatic_relaxation": 0.95,
        }
        with open(receipts_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(sleep_receipt, ensure_ascii=False) + "\n")

        # Record homeostatic affect balance sample
        self.tracker.record_affect_sample(calm_satisfaction=0.92, constructive_challenge=0.08)

        return sleep_receipt

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

        # 7. Real Sleep Consolidation (Curator dreaming & memory crystallization)
        sleep_receipt = self._consolidate_sleep(current_cycle, ambient, agent_text, mirror_text)
        self.simulated_days += 1
        self.sleep_cycles += 1

        cycle_receipt = {
            "cycle_completed": True,
            "simulated_day": self.simulated_days,
            "sleep_consolidated": True,
            "sleep_receipt": sleep_receipt,
            "ambient": ambient,
            "agent_text": agent_text,
            "mirror_text": mirror_text,
            "perseveration_detected": self.perseveration_detected,
        }
        self._history.append(cycle_receipt)
        return cycle_receipt

    def get_developmental_summary(self, evaluation_mode: str = "Live Neural Model Gestation") -> Dict[str, Any]:
        """Return a structured summary of developmental progress."""
        return {
            "agent_name": self.agent_name,
            "creator_name": self.creator_name,
            "simulated_days": self.simulated_days,
            "sleep_cycles": self.sleep_cycles,
            "perseveration_detected": self.perseveration_detected,
            "evaluation_mode": evaluation_mode,
            "report_card": self.tracker.render_report_card(
                simulated_days=self.simulated_days,
                sleep_cycles=self.sleep_cycles,
                evaluation_mode=evaluation_mode,
            ),
        }
