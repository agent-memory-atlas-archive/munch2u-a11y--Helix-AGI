"""Use native Helix embeddings and native Habitus recall in Context Loom."""
from dataclasses import asdict
import numpy as np


class SemanticBridge:
    def __init__(self, encoder):
        self.encoder = encoder
        self.identity = self.space_id = encoder.identity

    def embed(self, text):
        vector = np.asarray(self.encoder.encode_document(text), dtype=float)
        norm = np.linalg.norm(vector)
        if not np.isfinite(vector).all() or norm <= 0:
            raise RuntimeError("Mindscape embedding failed; zero-vector fallback is forbidden")
        return (vector / norm).tolist()


class HabitusLane:
    name = "habitus_graph"

    def __init__(self, mind, *, on_recall=None):
        self.mind = mind
        self.trace = None
        self.paths = ()
        self.on_recall = on_recall

    def nominate(self, context):
        from context_loom.retrieval import candidate_for
        result = self.mind.recall(context.query, include_current_input=False)
        self.trace = asdict(result.packet)
        self.paths = self.trace.get("y_paths", ())
        if self.on_recall is not None:
            self.on_recall(self.paths)
        eligible = {record.id: record for record in context.records}
        # Native selection already has an order. Encode only that within-lane
        # rank; a constant score would tie every record and sort by its ID.
        return [candidate_for(eligible[rid], lane=self.name, score=1.0 / rank,
                              reason=f"native Habitus recall: {result.packet.trace_hash}")
                for rank, rid in enumerate(result.packet.selected_record_ids, 1) if rid in eligible]


def topical_paths(paths):
    """Adapt native serialized traversal fields without inventing empty topics."""
    adapted = []
    for path in paths:
        target = path.get("target_node_id") or path.get("target_concept_id") or path.get("target")
        nodes = path.get("path_node_ids") or path.get("path_nodes") or path.get("nodes")
        if not isinstance(target, str) or not target.strip():
            raise ValueError("Native traversal has no target identity")
        if nodes is None:
            nodes = [target]
        if not nodes or any(not isinstance(node, str) or not node.strip() for node in nodes):
            raise ValueError("Native traversal contains an empty path node")
        adapted.append({**path, "target_concept_id": target,
                        "target_concept_name": path.get("target_concept_name") or target,
                        "path_nodes": list(nodes)})
    return adapted
