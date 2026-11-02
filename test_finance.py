import copy
import unittest
from finance import summary,compare,percent,previous,PROFILE,recommend,alerts,largest,breakdown,render
class Tests(unittest.TestCase):
 def setUp(self): self.a={'summary':summary('2026-10'),'comparison':compare('2026-10')}
 def test_totals(self): self.assertEqual((self.a['summary']['expenses'],self.a['summary']['cash_flow']),(4480000,1520000))
 def test_growth(self): self.assertEqual(self.a['comparison']['changes']['Food']['percent'],'25.00')
 def test_missing(self): self.assertEqual(summary('2026-08')['status'],'no_data')
 def test_missing_comparison(self): self.assertEqual(compare('2026-09')['status'],'insufficient_data')
 def test_invalid_month(self):
  for m in ['2026-13','2026-1',None]:
   with self.assertRaises(ValueError): summary(m)
 def test_amount(self):
  for n in [-1,1.5,True]:
   with self.assertRaises(ValueError): summary('2026-10',{'2026-10':[('X',n,'expense')]})
 def test_year(self): self.assertEqual(previous('2026-01'),'2025-12')
 def test_zero_baseline(self): self.assertIsNone(percent(10,0))
 def test_scenario(self): self.assertEqual(recommend(self.a)['scenario_cash_flow'],1920000)
 def test_scope(self): self.assertEqual(recommend(self.a,category='Food')['potential_reduction'],200000)
 def test_protected(self):
  p=copy.deepcopy(PROFILE); p['budgets']['Housing']=0
  self.assertNotIn('Housing',[a['category'] for a in recommend(self.a,p)['actions']])
 def test_zero_budget(self):
  p=copy.deepcopy(PROFILE); p['budgets']['Food']=0
  self.assertTrue(any(a['category']=='Food' and a['type']=='budget' for a in alerts(self.a,p)))
 def test_percent_rank(self): self.assertEqual(largest(self.a['comparison'])[0],'Entertainment')
 def test_amount_rank(self): self.assertEqual(largest(self.a['comparison'],'amount')[0],'Food')
 def test_no_increase(self):
  c=copy.deepcopy(self.a['comparison'])
  for v in c['changes'].values(): v['delta']=-100
  self.assertIsNone(largest(c))
 def test_breakdown(self): self.assertEqual(breakdown('2026-10','Food')['merchants'],{'Grocery':600000,'Restaurant':600000})
 def test_category_response(self):
  text=render({'plan':{'action':'spending','focus':'category','category':'Food'},'analysis':self.a})
  self.assertIn('INR 12,000.00',text); self.assertNotIn('Housing:',text)
 def test_degraded(self): self.assertIn('deterministic completion',render({'plan':{'action':'spending'},'analysis':self.a,'degraded':True}))
if __name__=='__main__': unittest.main()
