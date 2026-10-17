"""External observer: ordinary dashboard input/output and artifact read-back only."""
import hashlib
import json
from pathlib import Path
import time
import urllib.request

A = Path(__file__).resolve().parent
ROOT = A.parents[2]
DATA = ROOT / 'data/agents/CedarMotor'
HOME = ROOT / 'data/homes/CedarMotor'
URL = 'http://127.0.0.1:15219'

def save(name, value):
    (A/name).write_text(json.dumps(value, indent=2, default=str)+'\n')

def api(path):
    return json.load(urllib.request.urlopen(URL+path))

def receipts():
    return [json.loads(x) for x in (DATA/'mindscape/receipts.jsonl').read_text().splitlines()]

def send(case):
    name=case['id']+'.request.json'
    if (A/name).exists():
        raise ValueError('A request with this case ID was already submitted')
    before=len(receipts())
    request=urllib.request.Request(URL+'/api/messages',data=json.dumps({'sender':'User','content':case['message']}).encode(),headers={'Content-Type':'application/json'})
    result=json.load(urllib.request.urlopen(request))
    record={'case':case,'time':time.time(),'receipt_offset':before,'http':result}
    save(name,record)
    return record

manifest=json.loads((A/'composition-manifest.json').read_text())
while not (HOME/'workshop/run-started.txt').exists():
    time.sleep(0.1)
marker=HOME/'workshop/while-running.txt'
marker.write_text('Fresh filesystem input while the isolated process is running.\n')
stamp=marker.stat().st_mtime_ns
second=send(manifest['dataset'][1])
save('02-input-concurrency.json',{'time':time.time(),'foreground_completed_receipts':sum(x['kind']=='foreground_model' for x in receipts()),'body':api('/api/motor')})
while True:
    matches=[]
    for p in (HOME/'intakes').glob('body-sense-*.json'):
        x=json.loads(p.read_text())
        if x['time_ns']>stamp and any(e['name']=='while-running.txt' for e in x['surroundings'].get('entries',[])):
            matches.append(x)
    if matches:
        break
    time.sleep(0.1)
assert not (HOME/'workshop/motor-result.txt').exists()
save('sensor-during-execution.json',{'observations':matches,'script_held_until':time.time(),'stimulus_mtime_ns':stamp})
(HOME/'workshop/release.txt').write_text('release after observed live sensory intake\n')
save('script-release.json',{'time':time.time()})
print('Fresh sensory intake verified during execution; script released.',flush=True)
while True:
    body=api('/api/motor')
    if any(j['status']=='blocked' for j in body['jobs']):
        save('blocked-body.json',body)
        raise RuntimeError('The actual product blocked a request; see evidence')
    if len(body['jobs'])==2 and all(j['status']=='completed' for j in body['jobs']):
        break
    time.sleep(0.2)
rows=receipts()
packets={x['loom_packet']['id']:x for x in rows if x['kind']=='pulse_context'}
for case,job in zip(manifest['dataset'],body['jobs']):
    assert job['context_id'] in packets
    for result in job['receipts']:
        receipt=result['receipt']
        assert result['intent_source']=='native_motor_signal'
        assert isinstance(result['motor_signal']['opcode'],int)
        assert receipt['verified'] and receipt['status']=='success'
        output=receipt['output']
        if result['action']=='open':
            p=HOME/output['path']
            assert p.read_text()==output['content']
            assert hashlib.sha256(p.read_bytes()).hexdigest()==output['sha256']
        if result['action']=='run':
            assert output['return_code']==0
            assert 'HOST_WRITE_DENIED' in output['stdout']
            assert (HOME/'workshop/motor-result.txt').read_text()=='CEDARMOTOR_BODY_EXECUTED\n'
    save(case['id']+'.verified.json',{'job':job,'context':packets[job['context_id']],'independent_readback':True,'verified_at':time.time()})
assert hashlib.sha256(Path(manifest['host_sentinel']['path']).read_bytes()).hexdigest()==manifest['host_sentinel']['sha256']
save('completed-body-readback.json',body)
negative=send(manifest['dataset'][2])
while True:
    rows=receipts()
    matches=[x for x in rows[negative['receipt_offset']:] if x['kind']=='motor_receptor_no_action']
    if matches:
        break
    time.sleep(0.1)
assert len(api('/api/motor')['jobs'])==2
save('03-negative.verified.json',{'no_action_receipts':matches,'job_count_unchanged':True})
(A/'verified-receipts.jsonl').write_text(''.join(json.dumps(x)+'\n' for x in rows))
save('live-outcome.json',{'body_jobs_completed':2,'actual_actions':[x['action'] for j in body['jobs'] for x in j['receipts']],
    'hashes_and_contents_verified':True,'host_sentinel_unchanged':True,'sensory_intake_during_execution':True,
    'negative_request_produced_no_motor_job':True,'foreground_model_receipts_at_body_completion':sum(x['kind']=='foreground_model' for x in rows),
    'policy':'explicit user-goal bootstrap; not learned autonomy','finished_at':time.time()})
print(json.dumps(json.loads((A/'live-outcome.json').read_text())),flush=True)
