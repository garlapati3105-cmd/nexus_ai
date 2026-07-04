import unittest
from app.ai.explainability.service import ExplainabilityService

class TestExplainabilityEngine(unittest.TestCase):
    
    def setUp(self):
        self.service = ExplainabilityService()

    def test_decision_logging_and_calculators(self):
        # 1. Test standard local stockout transfer scenario
        params = {
            "quantity": 10,
            "unit_price": 12.50,
            "procurement_price": 8.00,
            "estimated_freight_cost": 15.00,
            "is_stockout": True,
            "stock_ratio": 0.20,
            "has_prescription": True
        }
        
        record = self.service.log_decision(
            workflow_id="wf-111",
            agent_name="FinanceAI",
            action_taken="RECOMMEND_TRANSFER",
            parameters=params,
            reasoning="Redirecting order to Branch 2 offers lower freight offsets than external buying.",
            evidence=["Local Stock: 0", "Branch 2 Stock: 50"],
            knowledge_sources=["SOP Chapter 4: Inter-branch Transfer Protocols"]
        )
        
        # Verify Confidence Score
        self.assertLess(record.explanation.confidence_score, 0.85) # Reduced due to stock ratio < 0.5
        
        # Verify Business Impact Savings
        # Local checkout: 10 * 12.5 = 125
        # Optimization: 10 * 8.0 + 15.0 = 95
        # Savings: 125 - 95 = 30
        self.assertEqual(record.explanation.estimated_savings, 30.00)
        self.assertEqual(record.explanation.risk_level, "LOW")
        self.assertIn("Estimated savings: $30.00", record.explanation.business_impact)
        
        # Verify Alternative actions
        self.assertIn("Substitute with equivalent generic molecular formulation.", record.explanation.alternative_recommendations)
        
        # 2. Test timeline retrieval
        timeline = self.service.get_timeline("wf-111")
        self.assertEqual(len(timeline.history), 1)
        self.assertEqual(timeline.history[0].decision_id, record.decision_id)

if __name__ == "__main__":
    unittest.main()
