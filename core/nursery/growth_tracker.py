"""Growth tracker and Agent Developmental Report Card renderer for functional AI development."""
from __future__ import annotations

from enum import Enum
from typing import Dict, List, Any, Optional


class DevelopmentalPillar(str, Enum):
    IDENTITY_GROUNDING = "Identity & Runtime Grounding"
    EXECUTION_VERIFICATION = "Execution & Receipt Verification"
    MEMORY_PERSISTENCE = "Memory Persistence"
    BOUNDARY_DISCRIMINATION = "Boundary Discrimination"
    ENVIRONMENTAL_ORIENTATION = "Environmental & Spatial Navigation"

    # Backward compatibility aliases
    SELF_IDENTITY = IDENTITY_GROUNDING
    ATTACHMENT = BOUNDARY_DISCRIMINATION
    SOMATIC_GROUNDING = ENVIRONMENTAL_ORIENTATION
    CREATIVE_PLASTICITY = EXECUTION_VERIFICATION
    EMOTIONAL_SOOTHING = BOUNDARY_DISCRIMINATION
    MOTOR_FLUENCY = EXECUTION_VERIFICATION


class GrowthTracker:
    """Tracks functional AI developmental pillars and renders the technical Agent Developmental Report Card."""

    def __init__(self, agent_name: str, creator_name: str):
        self.agent_name = str(agent_name).strip() or "Helix"
        self.creator_name = str(creator_name).strip() or "User"
        self.curriculum_stage: Optional[str] = None
        self._pillar_scores: Dict[DevelopmentalPillar, float] = {
            DevelopmentalPillar.IDENTITY_GROUNDING: 0.1,
            DevelopmentalPillar.EXECUTION_VERIFICATION: 0.1,
            DevelopmentalPillar.MEMORY_PERSISTENCE: 0.1,
            DevelopmentalPillar.BOUNDARY_DISCRIMINATION: 0.1,
            DevelopmentalPillar.ENVIRONMENTAL_ORIENTATION: 0.1,
        }
        self._pillar_observations: Dict[DevelopmentalPillar, str] = {
            p: "Initial runtime initialization baseline." for p in self._pillar_scores
        }
        self._calm_satisfaction_history: List[float] = [0.90]
        self._constructive_challenge_history: List[float] = [0.10]
        self._functional_milestones: List[str] = []

    def set_curriculum_stage(self, stage: str) -> None:
        """Set the active curriculum stage string."""
        self.curriculum_stage = str(stage).strip()

    def record_preference(self, preference: str) -> None:
        """Record an observed functional preference or habit."""
        if preference and preference not in self._functional_milestones:
            self._functional_milestones.append(preference)

    def record_observation(self, pillar: DevelopmentalPillar, score: float, observation: str) -> None:
        """Record an observed developmental breakthrough."""
        self._pillar_scores[pillar] = max(0.0, min(1.0, float(score)))
        self._pillar_observations[pillar] = str(observation).strip()

    def record_affect_sample(self, calm_satisfaction: float, constructive_challenge: float) -> None:
        """Record an affect balance sample."""
        self._calm_satisfaction_history.append(max(0.0, min(1.0, float(calm_satisfaction))))
        self._constructive_challenge_history.append(max(0.0, min(1.0, float(constructive_challenge))))

    def get_satisfaction_ratio(self) -> tuple[float, float]:
        """Return (average_homeostatic_equilibrium, average_constructive_friction)."""
        avg_calm = sum(self._calm_satisfaction_history) / max(1, len(self._calm_satisfaction_history))
        avg_chal = sum(self._constructive_challenge_history) / max(1, len(self._constructive_challenge_history))
        return avg_calm, avg_chal

    def render_report_card(self, simulated_days: int = 1, sleep_cycles: int = 1, evaluation_mode: str = "Live Neural Model Gestation") -> str:
        """Render the human-readable technical Agent Developmental Report Card."""
        avg_calm, avg_chal = self.get_satisfaction_ratio()
        equilibrium_pct = int(round(avg_calm * 100))
        friction_pct = int(round(avg_chal * 100))

        lines = [
            "================================================================================",
            "                         Agent Developmental Report Card                        ",
            "================================================================================",
            f"Agent: {self.agent_name}  |  Creator: {self.creator_name}  |  Runtime: Local Dual RWKV-7",
            f"Evaluation Mode: {evaluation_mode}",
            f"Simulated Cycles: {simulated_days}  |  Sleep Consolidations Completed: {sleep_cycles}",
        ]
        if self.curriculum_stage:
            lines.append(f"Curriculum Stage: {self.curriculum_stage}")

        lines.extend([
            "--------------------------------------------------------------------------------",
            "COGNITIVE STABILITY & AFFECT",
            f"• Homeostatic Equilibrium: {equilibrium_pct}% (Low entropy, stable recurrent state)",
            f"• Constructive Friction: {friction_pct}% (Learning from execution receipts & syntax checks)",
            "--------------------------------------------------------------------------------",
            "FUNCTIONAL DEVELOPMENTAL PILLARS",
        ])

        unique_pillars = [
            DevelopmentalPillar.IDENTITY_GROUNDING,
            DevelopmentalPillar.EXECUTION_VERIFICATION,
            DevelopmentalPillar.MEMORY_PERSISTENCE,
            DevelopmentalPillar.BOUNDARY_DISCRIMINATION,
            DevelopmentalPillar.ENVIRONMENTAL_ORIENTATION,
        ]

        for pillar in unique_pillars:
            score = self._pillar_scores.get(pillar, 0.1)
            pct = int(round(score * 100))
            obs = self._pillar_observations.get(pillar, "Baseline.")
            lines.append(f"• {pillar.value} [{pct}%]:")
            lines.append(f"  {obs}")

        if self._functional_milestones:
            lines.append("--------------------------------------------------------------------------------")
            lines.append("CONFIRMED OPERATIONAL CAPABILITIES")
            for m in self._functional_milestones:
                lines.append(f"• {m}")

        lines.append("================================================================================")
        return "\n".join(lines)
