"""Exact accounting for the local RWKV conversation renderer.

The configured context value bounds the assembled input, not RWKV's recurrent
state or the length of a generated answer. Generation ends on a model boundary.
"""
from pathlib import Path
import hashlib


class RWKVTokenCounter:
    def __init__(self, encode, model_path):
        self.encode = encode
        path = Path(model_path).resolve()
        files = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                 for p in sorted(path.glob('*token*')) if p.is_file()}
        self.identity = 'rwkv-local:' + str(path)
        self.provenance = {'model': str(path), 'tokenizer_files': files,
                           'renderer': 'helix-rwkv-conversation-v1', 'exact': True}

    def count(self, text):
        return len(self.encode(text))

    @staticmethod
    def render_messages(messages):
        parts = []
        labels = {'system': 'System', 'user': 'User', 'assistant': 'Assistant'}
        for item in messages:
            if item['role'] not in labels or not isinstance(item['content'], str):
                raise ValueError('Unsupported RWKV message')
            if item['content']:
                parts.append(labels[item['role']] + ': ' + item['content'])
        return '\n\n'.join(parts) + '\nAssistant:'

    def count_messages(self, messages):
        return self.count(self.render_messages(messages))

    def check_request(self, messages, context_tokens):
        count = self.count_messages(messages)
        if count > context_tokens:
            raise ValueError(f'Complete RWKV input needs {count} tokens; configured input allowance is {context_tokens}; nothing was clipped')
        return {'prompt_tokens': count, 'context_tokens': context_tokens,
                'context_boundary': 'configured assembled input allowance; generation is recurrent',
                'token_counter': self.identity, 'input_truncated': False,
                'output_token_cap': None}
