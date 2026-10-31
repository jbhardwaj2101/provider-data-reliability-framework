"""Deterministic synthetic event benchmark for directory correction maintenance.
Not an evaluation of real-world directory accuracy.
"""
from dataclasses import dataclass
import json, random, statistics, argparse
from pathlib import Path

@dataclass(frozen=True)
class Event:
    case_id: int
    kind: str
    new_value: str
    evidence: bool
    downstream_failure: bool
    t: int

KINDS=('address','affiliation','phone','network','stale')

def make_events(seed=42, n=1000):
    r=random.Random(seed)
    events=[]
    for i in range(n):
        kind=r.choice(KINDS)
        events.append(Event(i,kind,f'{kind}-{i}',r.random()<.8,r.random()<.12,i))
    return events

def batch_only(events):
    """Baseline: accepts every incoming change, writes without evidence gate or acknowledgement tracking."""
    directory={}; history=[]
    for e in events:
        directory[e.case_id]=e.new_value
        history.append({'id':e.case_id,'published':True,'authorized':e.evidence,'ack':not e.downstream_failure,
                        'tracked_failure':False,'trace_complete':False,'status':'closed'})
    return directory,history

def pdrf(events):
    """Rules: no publish before evidence; publication needs ack; failure stays open; stale cases flagged."""
    directory={}; history=[]
    for e in events:
        h={'id':e.case_id,'kind':e.kind,'source':'synthetic-event-generator','t':e.t,
           'evidence':e.evidence,'status':'detected','published':False,
           'authorized':False,'ack':False,'tracked_failure':False,'trace_complete':True}
        if e.kind=='stale':
            h['status']='needs_refresh'
        elif not e.evidence:
            h['status']='awaiting_verification'
        else:
            h['authorized']=True
            h['status']='approved'
            if e.downstream_failure:
                h['status']='publication_exception'; h['tracked_failure']=True
            else:
                directory[e.case_id]=e.new_value
                h['published']=True; h['ack']=True; h['status']='closed'
        history.append(h)
    return directory,history

def metrics(history):
    n=len(history)
    return {'events':n,'published':sum(h['published'] for h in history),
      'unauthorized_publications':sum(h['published'] and not h['authorized'] for h in history),
      'unacknowledged_closed':sum(h['status']=='closed' and not h['ack'] for h in history),
      'tracked_failures':sum(h['tracked_failure'] for h in history),
      'complete_traces':sum(h['trace_complete'] for h in history),
      'open_cases':sum(h['status']!='closed' for h in history)}

def evaluate(seed=42,n=1000):
    events=make_events(seed,n)
    b=batch_only(events)[1]; p=pdrf(events)[1]
    return {'seed':seed,'baseline':metrics(b),'pdrf':metrics(p),
      'input':{'events':n,'missing_evidence':sum(not e.evidence for e in events),
               'publication_failures':sum(e.downstream_failure for e in events),
               'stale_events':sum(e.kind=='stale' for e in events)}}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--output',default='results'); a=ap.parse_args()
    out=Path(a.output);out.mkdir(parents=True,exist_ok=True)
    trials=[evaluate(s) for s in range(100)]
    (out/'trials.json').write_text(json.dumps(trials,indent=2))
    def summary(which,key):
        vals=[t[which][key]/t[which]['events'] for t in trials]
        return {'mean':round(statistics.mean(vals),4),'sd':round(statistics.stdev(vals),4),
                'min':round(min(vals),4),'max':round(max(vals),4)}
    result={'design':'100 synthetic replications; 1000 independent events per replication; seeded RNG',
            'baseline':{k:summary('baseline',k) for k in ('unauthorized_publications','unacknowledged_closed','complete_traces','open_cases')},
            'pdrf':{k:summary('pdrf',k) for k in ('unauthorized_publications','unacknowledged_closed','complete_traces','open_cases')},
            'example_seed42':evaluate(42)}
    (out/'summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if __name__=='__main__': main()
