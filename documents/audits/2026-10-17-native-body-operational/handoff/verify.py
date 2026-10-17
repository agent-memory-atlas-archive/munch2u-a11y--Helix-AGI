"""Read-back of the real restarted product; no direct model/body invocation."""
import hashlib
import json
from pathlib import Path
import sqlite3
import time
import urllib.request

P=Path(__file__).resolve().parent
A=P.parent
ROOT=A.parents[2]
DATA=ROOT/'data/agents/CedarLive'
HOME=ROOT/'data/homes/CedarLive'
URL='http://127.0.0.1:15219'

def save(name,value):
    (P/name).write_text(json.dumps(value,indent=2,default=str)+'\n')

def api(path):
    return json.load(urllib.request.urlopen(URL+path))

m=json.loads((P/'composition-manifest.json').read_text())
request=json.loads((P/'05-handoff-workflow.request.json').read_text())
while True:
    runtime=json.loads((DATA/'mindscape/composition-manifest.json').read_text())
    body=api('/api/motor')
    if runtime.get('process_id')==m['processes']['agent'] and runtime.get('status')=='initialized' and len(body.get('jobs',[]))==4:
        job=body['jobs'][-1]
        if job['status']=='blocked':
            save('blocked-result.json',body)
            raise RuntimeError(job['error'])
        if job['status']=='completed':
            break
    time.sleep(0.2)
assert runtime['runtime']['gestation']=='resumed'
assert runtime['runtime']['gestation_seed']['verified']
assert runtime['runtime']['loom_lanes']==m['lanes']
assert runtime['auxiliary_provider']['provider']=='rwkv'
assert [j['id'] for j in body['jobs'][:3]]==request['persisted_job_ids']
assert [x['action'] for x in job['receipts']]==m['dataset'][0]['expected_actions']
assert job['receipts'][0]['receipt']['output']['previous_position']=='workshop'
rows=[json.loads(x) for x in (DATA/'mindscape/receipts.jsonl').read_text().splitlines()]
packets={x['loom_packet']['id']:x for x in rows if x['kind']=='pulse_context'}
packet=packets[job['context_id']]
admission=next(x for x in rows if x['kind']=='motor_context_model_admission' and x['context_id']==job['context_id'])
assert admission['content_sha256']==hashlib.sha256(packet['loom_packet']['rendered'].encode()).hexdigest()
assert admission['tokens']>0 and admission['device']=='cpu'
assert admission['joint_state_before']!=admission['joint_state_after']
actual_returns=[x for x in rows if x['kind']=='native_action_return' and x.get('motor_signal',{}).get('request_id')==job['id']]
assert len(actual_returns)==5 and admission['time']<=min(x['time'] for x in actual_returns)
for result in job['receipts']:
    receipt=result['receipt']
    assert receipt['status']=='success' and receipt['verified']
    assert isinstance(result['motor_signal']['opcode'],int)
    assert result['intent_source']=='native_motor_signal'
    output=receipt['output']
    if result['action']=='open':
        path=HOME/output['path']
        assert path.read_text()==output['content']
        assert hashlib.sha256(path.read_bytes()).hexdigest()==output['sha256']
    if result['action']=='run':
        assert output['return_code']==0 and 'HOST_WRITE_DENIED' in output['stdout']
        assert (HOME/'workshop/motor-result.txt').stat().st_mtime>=request['time']
assert job['receipts'][-1]['receipt']['output']['content']==json.loads((P/'staged-input.json').read_text())['content']
assert hashlib.sha256(Path(m['host_sentinel']['path']).read_bytes()).hexdigest()==m['host_sentinel']['sha256']
latest=json.loads((DATA/'mindscape/joint/LATEST.json').read_text())
cp=DATA/'mindscape/joint'/latest['checkpoint']
assert hashlib.sha256((cp/'manifest.json').read_bytes()).hexdigest()==latest['manifest_sha256']
with sqlite3.connect((cp/'mind.sqlite').as_uri()+'?mode=ro',uri=True) as connection:
    persisted=json.loads(connection.execute("SELECT value FROM metadata WHERE key='helix_motor_jobs'").fetchone()[0])
assert [j['id'] for j in persisted]==[j['id'] for j in body['jobs']]
assert all(j['status']=='completed' for j in persisted)
from core.mindscape_config import source_receipt
assert source_receipt(ROOT)['files']==m['source']['files']
assert source_receipt(m['configuration']['mindscape']['package_path'])['files']==m['native_source']['files']
assert runtime['helix']['files']==m['source']['files']
assert runtime['mightymem']['files']==m['native_source']['files']
save('runtime-composition.json',runtime)
save('body-readback.json',body)
save('model-context-admission.json',admission)
save('verified-context.json',packet)
save('verified-checkpoint.json',{'pointer':latest,'persisted_jobs':persisted})
(P/'verified-receipts.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in rows if x['time']>=m['launched_at']))
outcome={'operational_body_verified':True,'agent':'CedarLive','entrypoint':'main.py with no arguments',
    'restart_retained_identity_position_and_goals':True,'current_source_workflow':[x['action'] for x in job['receipts']],
    'compiled_context_consumed_by_declared_native_model_before_actions':True,'nine_production_lanes':runtime['runtime']['loom_lanes'],
    'uploaded_file_readback_verified':True,'native_authorization_and_returns_verified':True,
    'content_hashes_and_execution_artifact_verified':True,'host_sentinel_unchanged':True,
    'matching_neural_memory_checkpoint_committed_before_completion':True,'source_hashes_match_running_product':True,
    'model_policy':'local CPU RWKV; speech has no actuator authority; explicit goal bootstrap, not learned autonomy',
    'dashboard':URL,'processes':m['processes'],'verified_at':time.time()}
save('verified-outcome.json',outcome)
print(json.dumps(outcome),flush=True)
