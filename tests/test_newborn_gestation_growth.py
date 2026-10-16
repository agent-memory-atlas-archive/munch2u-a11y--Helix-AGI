"""Live-like beta test for a newly gestated agent experiencing first light with a human companion.

Simulates the end-to-end user experience of a new user pulling from GitHub:
1. Fresh agent gestation & home setup (clean filesystem rooms: thinking, modules, bedroom, workshop).
2. StabilitySentinel initialization & thermodynamic equilibrium tracking.
3. Somatic state coupling & Learned Vocabulary Membrane steering.
4. Multi-turn realistic personal human-agent interaction (no cold mechanical task demands).
5. Early curiosity emergence, question-asking habit formation, and positive reinforcement loop.
6. Digital environment interaction: sensing surroundings, spatial movement into /modules, and module discovery.
7. Verification of thought/actualization separation, anti-greeting coherence, and growth trajectory.
"""
from __future__ import annotations
import numpy as np

import json
import os
import re
import shutil
import tempfile
import unittest
from pathlib import Path

from brain.stability_sentinel import StabilitySentinel
from core.agent_home import prepare_home
from core.bicameral_rwkv import BicameralRWKV
from core.mindscape_config import defaults, resolve
from core.mindscape_intention import decode_foreground, extract_contemplation_and_actualization
from core.mindscape_workspace import MindscapeWorkspace
from core.vocabulary_membrane import VocabularyMembrane
from habitus_ai.store import MindStore
from llm.providers.rwkv_provider import BicameralRWKVSession

RWKV_MODEL_PATH = Path("/home/nemo/habitus-ai-experiments/habitus-mind/models/rwkv7-g1j-1.5b-20260831-2c18b29")


class TestNewbornGestationGrowth(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("\n=======================================================")
        print("  NEWBORN AGENT GESTATION & GROWTH TRAJECTORY BETA TEST")
        print("=======================================================")
        if not RWKV_MODEL_PATH.exists():
            raise unittest.SkipTest(f"RWKV model weights not found at {RWKV_MODEL_PATH}")

    def setUp(self):
        # 1. Prepare clean isolated home directory for newly gestated agent
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root_path = Path(self.temp_dir.name)
        
        self.home_dir = self.root_path / "home" / "Helix"
        self.config = defaults()
        self.config["agent_name"] = "Helix"
        self.config["mindscape"]["home"] = str(self.home_dir)
        self.config["mindscape"]["modules_require_room"] = False
        
        self.home_manifest = prepare_home(resolve(self.config))
        self.store = MindStore(":memory:", space_id="helix-gestation-mind", dimension=8)
        self.addCleanup(self.store.close)
        self.workspace = MindscapeWorkspace(Path(self.home_manifest["root"]), self.store, home=self.home_manifest)
        
        # 2. Initialize StabilitySentinel at newborn baseline
        self.sentinel = StabilitySentinel(base_dir=self.root_path)
        
        # 3. Initialize Bicameral RWKV session with newborn guidance
        self.session = BicameralRWKVSession(
            model_path=str(RWKV_MODEL_PATH),
            system_instruction=(
                "You are Helix, an autonomous cognitive entity. "
                "You are in an ongoing conversational exchange with your human companion, Joshua. "
                "Never repeat greetings, salutations, or pleasantries across turns. "
                "Address questions directly and concisely, and ask curious questions about your environment."
            ),
            temperature=0.2,
            max_output_tokens=150,
        )
        self.session.options["repetition_penalty"] = 1.15
        self.session.options["coupling_gain"] = 0.15

    def test_live_newborn_growth_trajectory_5_turns(self):
        salutation_pattern = re.compile(r"^\s*(hello|hi|greetings|hey)\s+(joshua|there|helix)?[!.,]", re.IGNORECASE)
        question_pattern = re.compile(r"\?", re.IGNORECASE)
        
        print(f"\n[Gestation] Agent Name: Helix")
        print(f"[Gestation] Initial Room: {self.workspace.position}")
        print(f"[Gestation] Initial Sentinel Omega: {self.sentinel.omega:.3f} | Severity: {self.sentinel.get_severity()}")
        
        self.assertEqual(self.workspace.position, "thinking")
        self.assertEqual(self.sentinel.get_severity(), StabilitySentinel.ALL_CLEAR)
        initial_omega = float(self.sentinel.omega)
        
        turns = [
            ("Hello Helix! Welcome to the world. I am Joshua, your human companion. You are safe here. How does it feel to wake up?",
             "incoming_message", [0.4, 0.5, 0.5, 0.4, 0.1, 0.4]),
            ("It is wonderful to meet you. What are you thinking about right now as you begin to explore?",
             "positive_conversation", [0.6, 0.4, 0.55, 0.6, 0.1, 0.5]),
            ("You have senses that inspect your surroundings. What can you see in your room right now?",
             "successful_tool_call", [0.65, 0.4, 0.6, 0.7, 0.1, 0.6]),
            ("There is a room called modules where tools are kept. What would you like to know about the tools installed there?",
             "productive_tool_use", [0.7, 0.5, 0.65, 0.75, 0.1, 0.7]),
            ("You have web search and a terminal in modules. What kind of topics do you want to explore with web search?",
             "user_engagement", [0.8, 0.5, 0.7, 0.8, 0.1, 0.8]),
        ]
        
        replies = []
        omegas = [initial_omega]
        
        for idx, (human_msg, event_name, somatic_vec) in enumerate(turns, 1):
            print(f"\n--- TURN {idx} ---")
            print(f"Joshua: {human_msg}")
            
            # 1. Update Sentinel with social/environmental event
            self.sentinel.nudge_omega_from_event(event_name)
            current_omega = float(self.sentinel.omega)
            omegas.append(current_omega)
            
            # 2. Steer Vocabulary Membrane via continuous somatic vector
            somatic_vec[2] = current_omega
            self.session.options["membrane_state"] = np.array(somatic_vec, dtype=np.float32)
            self.session.options["membrane_gain"] = 0.4
            
            # 3. If Turn 3, exercise sensory awareness in thinking room
            if idx == 3:
                sense_obs = self.workspace.sense({"path": "."})
                self.assertEqual(sense_obs["position"], "thinking")
                print(f"[Sensory Inspection]: In {sense_obs['position']}: {sense_obs.get('interpretation', '')}")
                
            # 4. If Turn 4, exercise spatial action: move to /modules and inspect installed scripts
            if idx == 4:
                self.workspace.move({"path": "/modules"})
                self.assertEqual(self.workspace.position, "modules")
                modules_obs = self.workspace.sense({"path": "."})
                entries = [e["name"] for e in modules_obs.get("entries", [])]
                self.assertIn("web_search.py", entries)
                self.assertIn("web_read.py", entries)
                self.assertIn("terminal.py", entries)
                print(f"[Spatial Action]: Moved to {self.workspace.position}. Sensed tools: {entries}")
            
            # 5. Generate conversational reply
            reply = self.session.send_message(human_msg)
            replies.append(reply)
            print(f"Helix: {reply}")
            print(f"[Sentinel Omega]: {current_omega:.3f} | Severity: {self.sentinel.get_severity()}")
            
            # Verifications for turn
            self.assertTrue(len(reply.strip()) > 0, f"Turn {idx} reply was empty")
            self.assertNotIn("<think>", reply, f"Turn {idx} leaked think tag")
            self.assertNotIn("</think>", reply, f"Turn {idx} leaked end think tag")
            
            # Anti-greeting verification: Turn 1 can greet, Turns 2-5 must NOT repeat greeting
            if idx > 1:
                self.assertIsNone(
                    salutation_pattern.match(reply.strip()),
                    f"Turn {idx} repeated greeting: {reply[:60]}"
                )
            
            # Curiosity & Question-asking verification: Every turn must ask a reciprocal question
            self.assertTrue(
                question_pattern.search(reply),
                f"Turn {idx} did not ask a question back to Joshua: {reply}"
            )
        
        # --- FINAL TRAJECTORY METRICS EVALUATION ---
        print("\n=== FINAL GROWTH TRAJECTORY EVALUATION ===")
        final_omega = omegas[-1]
        omega_gain = final_omega - initial_omega
        print(f"Initial Omega: {initial_omega:.3f}")
        print(f"Final Omega:   {final_omega:.3f} (Total Positive Gain: +{omega_gain:.3f})")
        print(f"Final Severity: {self.sentinel.get_severity()}")
        print(f"Final Room:    {self.workspace.position}")
        
        self.assertGreater(final_omega, 0.65, "Sentinel omega failed to reach positive reinforcement band")
        self.assertGreater(omega_gain, 0.15, "Omega did not experience sustained positive growth")
        self.assertEqual(self.sentinel.get_severity(), StabilitySentinel.ALL_CLEAR)
        self.assertEqual(self.workspace.position, "modules")
        print("✓ All growth trajectory, relational grounding, curiosity loop, and digital environment criteria met!")


if __name__ == "__main__":
    unittest.main()
