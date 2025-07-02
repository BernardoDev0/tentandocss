import json, sys, os, pprint
fn='Trace.json'
with open(fn, 'r', encoding='utf8') as f:
    data=json.load(f)
print('Total events:', len(data.get('traceEvents', [])))
# Filter LCP events
lcps=[e for e in data['traceEvents'] if 'LargestContentfulPaint' in e.get('name','')]
print('LCP events:', len(lcps))
lcps_sorted=sorted(lcps, key=lambda e: e.get('ts',0))
for e in lcps_sorted[:5]:
    print('Early LCP', e['ts'], e['args']['data'])
for e in lcps_sorted[-5:]:
    print('Late LCP', e['ts'], e['args']['data']) 