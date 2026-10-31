import unittest
from pdrf_benchmark import Event, pdrf, batch_only, make_events, evaluate
class TestPDRF(unittest.TestCase):
    def test_reproducibility(self): self.assertEqual(make_events(7),make_events(7))
    def test_evidence_gate(self):
        _,h=pdrf([Event(1,'address','new',False,False,1)]);self.assertFalse(h[0]['published'])
    def test_publication_failure(self):
        _,h=pdrf([Event(1,'address','new',True,True,1)]);self.assertEqual(h[0]['status'],'publication_exception')
    def test_success(self):
        d,h=pdrf([Event(1,'address','new',True,False,1)]);self.assertEqual(d[1],'new');self.assertTrue(h[0]['ack'])
    def test_stale(self):
        _,h=pdrf([Event(1,'stale','new',True,False,1)]);self.assertEqual(h[0]['status'],'needs_refresh')
    def test_trace(self):
        _,h=pdrf([Event(1,'network','x',True,False,1)]);self.assertTrue(h[0]['trace_complete'])
    def test_baseline_unsafe(self):
        _,h=batch_only([Event(1,'network','x',False,True,1)]);self.assertTrue(h[0]['published'])
    def test_zero_unauthorized(self):
        x=evaluate(1,100);self.assertEqual(x['pdrf']['unauthorized_publications'],0)
    def test_zero_unacknowledged_closed(self):
        x=evaluate(1,100);self.assertEqual(x['pdrf']['unacknowledged_closed'],0)
    def test_no_auto_stale(self):
        d,h=pdrf([Event(1,'stale','x',True,False,1)]);self.assertEqual(len(d),0)
if __name__=='__main__':unittest.main()
