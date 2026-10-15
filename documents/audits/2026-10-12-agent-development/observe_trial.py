"""Read-only evidence capture; interactions use the normal dashboard API."""
import argparse
import hashlib
import json
import time
import urllib.request
from pathlib import Path

AUDIT = Path(__file__).resolve().parent
ROOT = AUDIT.parents[2]
DATA = ROOT / "data/agents/Aster"
HOME = ROOT / "data/homes/Aster"
URL = "http://127.0.0.1:15053/api/messages"


def read_receipts():
    return [json.loads(line) for line in (DATA / "mindscape/receipts.jsonl").read_text().splitlines()]


def home_state():
    return {str(p.relative_to(HOME)): {"sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
                                       "bytes": p.stat().st_size}
            for p in HOME.rglob("*") if p.is_file() and not p.is_symlink()}


def save(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def send(case, content):
    if (AUDIT / f"{case}.request.json").exists():
        raise ValueError("Case already submitted; choose an explicit new attempt identifier")
    record = {"case": case, "sender": "User", "content": content,
              "submitted_at": time.time(), "receipt_offset": len(read_receipts()),
              "home_before": home_state()}
    request = urllib.request.Request(URL, data=json.dumps({"sender": "User", "content": content}).encode(),
                                     headers={"Content-Type": "application/json"})
    record["http_response"] = json.load(urllib.request.urlopen(request))
    save(AUDIT / f"{case}.request.json", record)
    with (AUDIT / "interactions.jsonl").open("a") as stream:
        stream.write(json.dumps(record) + "\n")
    print({"case": case, "submission": record["http_response"]})


def snapshot(case):
    request = json.loads((AUDIT / f"{case}.request.json").read_text())
    receipts = read_receipts()[request["receipt_offset"]:]
    (AUDIT / f"{case}.receipts.jsonl").write_text("".join(json.dumps(r) + "\n" for r in receipts))
    outbound = json.load(urllib.request.urlopen(URL + "/outbound"))
    messages = [r for r in outbound["messages"] if r["timestamp"] >= request["submitted_at"]]
    save(AUDIT / f"{case}.outbound.json", messages)
    save(AUDIT / f"{case}.home-after.json", home_state())
    for receipt in receipts:
        kind = receipt["kind"]
        if kind == "foreground_return":
            print({"pulse": receipt["helix_pulse"], "kind": kind,
                   "delivered": receipt["external_outcome_verified"], "content": receipt["thought"]})
        elif kind == "native_action_return":
            print(receipt)
        elif kind == "failed":
            print(receipt)
        elif kind == "foreground_model":
            r = receipt["provider_receipt"]
            print({"pulse": receipt["helix_pulse"], "model": receipt["model"],
                   "tokens": r.get("evaluated_prompt_tokens"), "done_reason": r.get("done_reason")})
    print({"receipts": len(receipts), "messages": messages})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("send", "snapshot"))
    parser.add_argument("case")
    parser.add_argument("--content")
    args = parser.parse_args()
    if args.operation == "send":
        send(args.case, args.content)
    else:
        snapshot(args.case)
