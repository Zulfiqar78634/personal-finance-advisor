"""Deterministic mock finance tools. Money is integer INR paise."""
import re
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
DATA={
 '2026-09':[('Employer',6000000,'income'),('Landlord',1500000,'expense'),('Grocery',500000,'expense'),('Restaurant',460000,'expense'),('Shopping',600000,'expense'),('Metro',300000,'expense'),('Electricity',250000,'expense'),('Cinema',200000,'expense')],
 '2026-10':[('Employer',6000000,'income'),('Landlord',1500000,'expense'),('Grocery',600000,'expense'),('Restaurant',600000,'expense'),('Shopping',800000,'expense'),('Metro',350000,'expense'),('Electricity',250000,'expense'),('Cinema',380000,'expense')]}
CATEGORY={'Landlord':'Housing','Grocery':'Food','Restaurant':'Food','Shopping':'Shopping','Metro':'Travel','Electricity':'Bills','Cinema':'Entertainment'}
PROFILE={'goal':1500000,'protected':['Housing','Bills'],'budgets':{'Housing':1500000,'Food':1000000,'Shopping':600000,'Travel':400000,'Bills':300000,'Entertainment':400000}}
def validate_month(month):
 if not isinstance(month,str) or not re.fullmatch(r'\d{4}-\d{2}',month): raise ValueError('Use YYYY-MM')
 date.fromisoformat(month+'-01'); return month
def previous(month):
 d=date.fromisoformat(validate_month(month)+'-01')
 return f'{d.year-1:04d}-12' if d.month==1 else f'{d.year:04d}-{d.month-1:02d}'
def money(n): return f'INR {Decimal(n)/100:,.2f}'
def percent(delta,base):
 return str((Decimal(delta)*100/Decimal(base)).quantize(Decimal('0.01'),rounding=ROUND_HALF_UP)) if base else None
def summary(month,data=None):
 validate_month(month); data=DATA if data is None else data
 if month not in data: return {'status':'no_data','month':month}
 income=0; categories={}
 for merchant,n,kind in data[month]:
  if type(n) is not int or n<0: raise ValueError('Nonnegative integer paise required')
  if kind=='income': income+=n
  elif kind=='expense':
   cat=CATEGORY.get(merchant,'Other'); categories[cat]=categories.get(cat,0)+n
  else: raise ValueError('Unsupported transaction type')
 expenses=sum(categories.values())
 return {'status':'ok','month':month,'unit':'INR paise','income':income,'expenses':expenses,'cash_flow':income-expenses,'categories':categories}
def compare(month,data=None):
 a=summary(month,data); b=summary(previous(month),data)
 if a['status']!='ok' or b['status']!='ok': return {'status':'insufficient_data'}
 changes={}
 for cat in sorted(set(a['categories'])|set(b['categories'])):
  old=b['categories'].get(cat,0); new=a['categories'].get(cat,0)
  changes[cat]={'previous':old,'current':new,'delta':new-old,'percent':percent(new-old,old)}
 return {'status':'ok','changes':changes}
def breakdown(month,category):
 validate_month(month)
 if month not in DATA: return {'status':'no_data','month':month}
 if category not in set(CATEGORY.values())|{'Other'}: raise ValueError('Unknown category')
 merchants={}
 for merchant,n,kind in DATA[month]:
  if kind=='expense' and CATEGORY.get(merchant,'Other')==category: merchants[merchant]=merchants.get(merchant,0)+n
 return {'status':'ok','category':category,'merchants':merchants}
def recommend(analysis,profile=None,category=None):
 profile=PROFILE if profile is None else profile; s=analysis['summary']
 if s['status']!='ok': return {}
 actions=[]
 for cat,n in s['categories'].items():
  if category and cat!=category: continue
  cap=profile['budgets'].get(cat)
  if cap is not None and n>cap and cat not in profile['protected']: actions.append({'category':cat,'cap':cap,'reduction':n-cap})
 reduction=sum(a['reduction'] for a in actions)
 return {'actions':actions,'potential_reduction':reduction,'scenario_cash_flow':s['cash_flow']+reduction,'goal_gap':max(0,profile['goal']-s['cash_flow'])}
def alerts(analysis,profile=None,category=None):
 profile=PROFILE if profile is None else profile; s=analysis['summary']; result=[]
 if s['status']!='ok': return result
 for cat,n in s['categories'].items():
  if category and cat!=category: continue
  cap=profile['budgets'].get(cat)
  if cap is not None and ((cap==0 and n>0) or (cap>0 and n*100>=cap*90)):
   result.append({'type':'budget','category':cat,'spent':n,'budget':cap,'severity':'high' if n>cap else 'warning'})
 c=analysis['comparison']
 if c['status']=='ok':
  for cat,v in c['changes'].items():
   if category and cat!=category: continue
   if v['previous']>0 and v['delta']*100>=v['previous']*25: result.append({'type':'increase','category':cat,'percent':v['percent']})
 return result
def largest(comparison,metric='percentage'):
 if comparison['status']!='ok': return None
 values=[(cat,v) for cat,v in comparison['changes'].items() if v['delta']>0 and (metric=='amount' or v['previous']>0)]
 return max(values,key=lambda x:x[1]['delta'] if metric=='amount' else Decimal(x[1]['delta'])/x[1]['previous']) if values else None
def render(s):
 plan=s['plan']
 if plan['action']=='clarify': return plan.get('clarification') or 'Please clarify your spending or savings question.'
 a=s['analysis']; total=a['summary']
 if total['status']!='ok': return f"No data for {total['month']}. Missing data is not zero spending."
 out=[f"Period: {total['month']} (complete mock dataset)."]
 focus=plan.get('focus','overview'); cat=plan.get('category'); comp=a['comparison']
 if focus=='category' and cat:
  out.append(f"{cat} spending: {money(total['categories'].get(cat,0))}.")
  if comp['status']=='ok' and cat in comp['changes']:
   v=comp['changes'][cat]; out.append(f"Change: {money(v['delta'])}; percentage: {v['percent'] if v['percent'] is not None else 'undefined (zero baseline)' }.")
  elif comp['status']!='ok': out.append('Prior-month comparison unavailable.')
 elif focus=='largest_increase':
  metric=plan.get('metric','percentage'); found=largest(comp,metric)
  if found:
   name,v=found; label=money(v['delta']) if metric=='amount' else v['percent']+'%'; out.append(f'Largest {metric} increase: {name}, {label}.')
  else: out.append('No comparable positive increase, or insufficient historical data.')
 elif focus=='income': out.append(f"Income: {money(total['income'])}.")
 elif focus=='cash_flow': out.append(f"Net cash flow: {money(total['cash_flow'])}.")
 else:
  out.extend([f"Income: {money(total['income'])}.",f"Expenses: {money(total['expenses'])}.",f"Net cash flow: {money(total['cash_flow'])}."])
  out.extend(f'{name}: {money(n)}.' for name,n in sorted(total['categories'].items()))
  if comp['status']=='ok':
   out.extend(f"{name} change: {v['percent']+'%' if v['percent'] is not None else 'undefined (zero baseline)'}." for name,v in comp['changes'].items())
  else: out.append('Prior-month comparison unavailable.')
 for detail in a.get('drilldowns',[]):
  if detail['status']=='ok': out.append('Tool-selected merchant breakdown: '+detail['category']+'; '+', '.join(f'{k}: {money(v)}' for k,v in detail['merchants'].items()))
 r=s.get('recommendations',{})
 if r:
  out.append(f"Savings goal: {money(PROFILE['goal'])}; gap versus cash flow: {money(r['goal_gap'])}.")
  for action in r['actions']: out.append(f"Consider a {action['category']} cap of {money(action['cap'])}; potential reduction {money(action['reduction'])}.")
  if not r['actions']: out.append('No reduction to configured non-protected budgets identified in this scope.')
  out.append(f"Potential reduction: {money(r['potential_reduction'])}; scenario cash flow: {money(r['scenario_cash_flow'])}, assuming unchanged income and other spending. Not guaranteed savings.")
 for alert in s.get('alerts',[]): out.append('Review alert: '+json_text(alert))
 if s.get('degraded'): out.append('Notice: deterministic completion was used; inspect trace for details.')
 out.append('Mock financial education. Cash flow is not balance or confirmed savings. Increases do not prove fraud.')
 return '\n'.join(out)
def json_text(value):
 import json
 return json.dumps(value)
def demo():
 a={'summary':summary('2026-10'),'comparison':compare('2026-10'),'drilldowns':[breakdown('2026-10','Food')]}
 return render({'plan':{'action':'review','focus':'overview'},'analysis':a,'recommendations':recommend(a),'alerts':alerts(a)})
