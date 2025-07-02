import json, sys
fn='Trace.json'
print('Loading', fn)
with open(fn,'r',encoding='utf8') as f:
    data=json.load(f)
print('Total events:', len(data.get('traceEvents', [])))
# filter LCP
lcps=[e for e in data['traceEvents'] if 'LargestContentfulPaint' in e.get('name','')]
print('LCP events:', len(lcps))
if not lcps:
    print('No LCP events found')
    sys.exit()
# sort by ts
lcps=sorted(lcps,key=lambda e:e.get('ts',0))
print('First 10 LCP events:')
for e in lcps[:10]:
    info=e.get('args',{}).get('data',{})
    print('ts',e['ts'],'dur',e.get('dur'),info)
print('\nLast LCP event (likely final):')
info=lcps[-1].get('args',{}).get('data',{})
print(info) 