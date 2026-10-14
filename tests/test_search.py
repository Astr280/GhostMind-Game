import unittest
from algorithms import astar,bfs,greedy_best_first

class SearchTests(unittest.TestCase):
    def setUp(self): self.walls={(2,0),(2,1),(2,2)}; self.walk=lambda p: 0<=p[0]<6 and 0<=p[1]<5 and p not in self.walls
    def test_astar_shortest_path(self):
        r=astar((0,0),(5,0),self.walk); self.assertTrue(r.found); self.assertEqual(len(r.path)-1,11)
    def test_bfs_shortest_and_valid(self):
        r=bfs((0,0),(5,0),self.walk); self.assertTrue(r.found); self.assertEqual(len(r.path)-1,11); self.assertTrue(all(self.walk(p) for p in r.path))
    def test_greedy_valid(self):
        r=greedy_best_first((0,0),(5,0),self.walk); self.assertTrue(r.found); self.assertTrue(all(self.walk(p) for p in r.path))
    def test_unreachable_and_same(self):
        blocked=lambda p: p==(0,0)
        self.assertFalse(astar((0,0),(1,0),blocked).found)
        self.assertEqual(bfs((1,1),(1,1),lambda p: True).path,[(1,1)])
if __name__=='__main__': unittest.main()
