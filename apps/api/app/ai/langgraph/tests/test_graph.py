import unittest
from app.ai.langgraph.graphs import workflow_graph

class TestLangGraphCompilation(unittest.TestCase):
    
    def test_workflow_graph_compiles(self):
        """Verify stategraph compiles and contains correct configurations."""
        self.assertIsNotNone(workflow_graph)
        # Verify starting nodes and transitions are registered
        self.assertIn("sales", workflow_graph.nodes)
        self.assertIn("inventory", workflow_graph.nodes)
        self.assertIn("finance", workflow_graph.nodes)

if __name__ == "__main__":
    unittest.main()

