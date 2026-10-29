
import unittest
from unittest.mock import patch

from agent import research


class ResearchAgentTests(unittest.TestCase):

    def test_empty_question(self):
        """The agent should reject an empty question."""

        report = research("   ")

        self.assertIn("error", report)

    @patch("agent.search_openalex")
    @patch("agent.search_wikipedia")
    def test_combines_both_sources(self, mock_wikipedia, mock_openalex):
        """The agent should combine results from both tools."""

        mock_wikipedia.return_value = [
            {
                "title": "Vector databases",
                "snippet": "Store and search vector embeddings.",
                "source": "Wikipedia",
                "url": "https://example.com/vector"
            }
        ]

        mock_openalex.return_value = [
            {
                "title": "Research on vector search",
                "year": 2025,
                "source": "OpenAlex",
                "url": "https://example.com/research"
            }
        ]

        report = research("Compare vector databases")

        self.assertEqual(len(report["key_findings"]), 2)
        self.assertEqual(len(report["sources_used"]), 2)
        self.assertIn("limitations", report)
        self.assertIn("confidence", report)

    @patch("agent.search_openalex")
    @patch("agent.search_wikipedia")
    def test_one_tool_fails(self, mock_wikipedia, mock_openalex):
        """The agent should continue if one tool fails."""

        mock_wikipedia.return_value = {
            "error": "Search service unavailable"
        }

        mock_openalex.return_value = [
            {
                "title": "Example research",
                "year": 2025,
                "source": "OpenAlex",
                "url": "https://example.com/research"
            }
        ]

        report = research("Research AI agents")

        self.assertEqual(len(report["key_findings"]), 1)
        self.assertEqual(
            report["key_findings"][0]["source"],
            "OpenAlex"
        )

    @patch("agent.search_openalex")
    @patch("agent.search_wikipedia")
    def test_both_tools_fail(self, mock_wikipedia, mock_openalex):
        """The agent should return a controlled failure report."""

        mock_wikipedia.return_value = {
            "error": "Wikipedia unavailable"
        }

        mock_openalex.return_value = {
            "error": "OpenAlex unavailable"
        }

        report = research("Research AI agents")

        self.assertEqual(
            report["short_answer"],
            "Research could not be completed."
        )
        self.assertEqual(report["confidence"], "Low")
        self.assertEqual(report["key_findings"], [])

    
    def test_duplicate_findings_are_removed(self):
        """Duplicate results should appear only once."""

        from agent import filter_findings

        findings = [
            {
                "title": "Vector databases",
                "source": "Wikipedia",
                "url": "https://example.com/vector"
            },
            {
                "title": "Vector databases",
                "source": "Wikipedia",
                "url": "https://example.com/vector"
            },
            {
                "title": "Another result",
                "source": "OpenAlex",
                "url": "https://example.com/another"
            }
        ]

        result = filter_findings(findings)

        self.assertEqual(len(result), 2)

if __name__ == "__main__":
    unittest.main(verbosity=2)
