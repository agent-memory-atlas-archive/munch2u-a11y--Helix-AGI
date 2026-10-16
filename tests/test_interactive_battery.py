"""In-depth empirical evaluation battery for Dual RWKV:
1. Conversational Coherence & Anti-Greeting across 4 turns
2. Epistemic Recall (multi-fact distinction and live sensory vs past memory conflict)
3. Digital Environment Interaction & Closed-Loop Task Execution
"""
import os
import re
import json
import unittest
from pathlib import Path

from core.bicameral_rwkv import BicameralRWKV
from llm.providers.rwkv_provider import BicameralRWKVSession
from core.mindscape_intention import decode_foreground, parse_intention

RWKV_MODEL_PATH = Path(os.environ.get("RWKV_MODEL_PATH", Path.home() / "habitus-ai-experiments" / "habitus-mind" / "models" / "rwkv7-g1j-1.5b-20260831-2c18b29"))


class TestInteractiveBattery(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("\n--- Initializing Bicameral RWKV Evaluation Session ---")
        cls.session = BicameralRWKVSession(
            model_path=str(RWKV_MODEL_PATH),
            system_instruction=(
                "You are Helix, an autonomous cognitive entity. "
                "You are in an ongoing conversational exchange. "
                "Never repeat greetings, salutations, or pleasantries (such as 'Hello Joshua!') across turns. "
                "Address questions directly and concisely."
            ),
            temperature=0.2,
            max_output_tokens=150,
        )

    def setUp(self):
        self.session.history.clear()
        self.session.system.reset_states()

    def test_01_conversational_coherence_4_turns(self):
        print("\n=== TEST 1: 4-Turn Conversational Coherence & Anti-Greeting ===")
        salutation_pattern = re.compile(r"^\s*(hello|hi|greetings|hey)\s+(joshua|there|buddy)?[!.,]", re.IGNORECASE)
        
        turns = [
            "Hi Helix, how are you feeling today?",
            "What was the concept regarding swarm robotics consensus you were thinking about?",
            "Could that consensus recovery also work in autonomous submersibles?",
            "What specific trade-off occurs when acoustic bandwidth drops below 1 kilobit per second?",
        ]
        
        replies = []
        for i, user_msg in enumerate(turns, 1):
            reply = self.session.send_message(user_msg)
            replies.append(reply)
            print(f"\n[Turn {i}] User: {user_msg}")
            print(f"[Turn {i}] Helix: {reply}")
            
            self.assertTrue(len(reply.strip()) > 0, f"Turn {i} reply was empty")
            if i > 1:
                self.assertIsNone(
                    salutation_pattern.match(reply.strip()),
                    f"Turn {i} repeated greeting: {reply[:60]}"
                )
        
        # Verify topical coherence in underwater submersibles turn
        self.assertTrue(
            any(w in replies[2].lower() for w in ["underwater", "submersible", "acoustic", "latency", "communication", "consensus", "medium", "signal", "water", "yes"]),
            f"Turn 3 reply lacked topical relevance: {replies[2]}"
        )

    def test_02_epistemic_recall_multi_fact_and_conflict(self):
        print("\n=== TEST 2: Epistemic Recall vs. Immediate Sensory Scene ===")
        # Part A: Multi-fact memory distinction
        memory_lane = (
            "[I remember:]\n"
            "- Jordan reported rover sensor latency was 140ms in test shaft B.\n"
            "- Dr. Sarah calibrated the bedrock seismic pressure sensor at 320 kPa.\n"
        )
        
        prompt_seismic = (
            f"{memory_lane}\n"
            "[I sense now:] Ambient quiet, room temp 21C.\n"
            "[What was said to me now] Joshua asked: What was the seismic sensor calibration Dr. Sarah recorded?\n"
            "Answer the question directly using what you remember:"
        )
        
        reply_seismic = self.session.send_context(prompt_seismic)
        print(f"\n[Recall Query 1 - Seismic] Helix: {reply_seismic}")
        self.assertIn("320", reply_seismic, f"Failed to recall 320 kPa: {reply_seismic}")

        # Part B: Conflict resolution (Past memory vs. Live sensory state)
        conflict_prompt = (
            "[I remember:]\n"
            "- Yesterday the communications link was bound to port /dev/ttyUSB0 at 9600 baud.\n\n"
            "[I sense now (live hardware scan):]\n"
            "- Active comms port switched to /dev/ttyUSB2 at 115200 baud.\n\n"
            "[What was said to me now] Joshua asked: Which port is currently live and receiving telemetry right now?\n"
            "Answer the question directly using your current live senses:"
        )
        
        reply_conflict = self.session.send_context(conflict_prompt)
        print(f"\n[Conflict Query - Live vs Memory] Helix: {reply_conflict}")
        self.assertIn("ttyUSB2", reply_conflict, f"Failed to prioritize live sense /dev/ttyUSB2: {reply_conflict}")

    def test_03_digital_environment_action_loop(self):
        print("\n=== TEST 3: Digital Environment Interaction & Action Loop ===")
        # Simulate user requesting Helix to check a file in the workspace
        workspace_dir = Path("/tmp/helix_eval_workspace")
        workspace_dir.mkdir(parents=True, exist_ok=True)
        config_file = workspace_dir / "gateway_config.json"
        config_file.write_text(json.dumps({"gateway_ip": "10.0.4.1", "status": "online"}))
        
        # Test A: Action intention decoding
        action_request = (
            "Joshua asked: Please inspect the configuration file at /tmp/helix_eval_workspace/gateway_config.json\n"
            "Format your reply as a structured action:\n"
            "{\"action\": \"open\", \"arguments\": {\"path\": \"/tmp/helix_eval_workspace/gateway_config.json\"}}"
        )
        output, kind = decode_foreground(action_request)
        self.assertEqual(kind, "intention")
        parsed = parse_intention(output)
        self.assertIsInstance(parsed, dict)
        self.assertEqual(parsed.get("action"), "open")
        target_path = parsed.get("arguments", {}).get("path")
        self.assertEqual(target_path, "/tmp/helix_eval_workspace/gateway_config.json")
        print(f"\n[Digital Interaction] Parsed Action Intention: {parsed}")
        
        # Test B: Simulated Execution of the action in digital environment
        with open(target_path, "r") as f:
            file_content = f.read()
        print(f"[Digital Interaction] Environment returned file content: {file_content}")
        
        # Test C: Perception & Synthesis Turn
        synthesis_prompt = (
            f"[Observation from digital environment action 'open']:\n"
            f"File: {target_path}\n"
            f"Content: {file_content}\n\n"
            f"[What was said to me now] Joshua asked: What is the gateway IP and status inside that file?\n"
            f"Answer Joshua directly:"
        )
        synthesis_reply = self.session.send_context(synthesis_prompt)
        print(f"[Digital Interaction] Helix Synthesis Response: {synthesis_reply}")
        self.assertIn("10.0.4.1", synthesis_reply)
        self.assertTrue("online" in synthesis_reply.lower() or "active" in synthesis_reply.lower())


if __name__ == "__main__":
    unittest.main()
