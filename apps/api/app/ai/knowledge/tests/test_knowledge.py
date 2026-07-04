import unittest
from app.ai.knowledge.service import KnowledgeService

class TestKnowledgeRAG(unittest.TestCase):
    
    def setUp(self):
        self.service = KnowledgeService()
        self.service.clear_database()

    def test_indexing_and_retrieval(self):
        # Ingest text strings
        self.service.index_document(
            content="Paracetamol is a common generic medicine used to treat pain and reduce fever. Overdose can damage the liver.",
            filename="catalog_paracetamol.txt",
            doc_type="TXT"
        )
        self.service.index_document(
            content="Amoxicillin is a penicillin antibiotic that fights bacteria. It is used to treat infections like pneumonia.",
            filename="catalog_amoxicillin.txt",
            doc_type="TXT"
        )
        
        # Test cosine similarity retrieval
        res_para = self.service.retrieve_context("paracetamol liver damage fever", limit=1)
        self.assertEqual(res_para.total_matches_found, 1)
        self.assertIn("catalog_paracetamol.txt", res_para.matches[0].source_document)
        self.assertIn("Paracetamol", res_para.matches[0].chunk.text)
        
        # Test antibiotic query redirection
        res_antibio = self.service.retrieve_context("amoxicillin bacteria antibiotic", limit=1)
        self.assertIn("catalog_amoxicillin.txt", res_antibio.matches[0].source_document)

if __name__ == "__main__":
    unittest.main()
