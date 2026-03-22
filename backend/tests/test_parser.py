import unittest

from backend.services.resume_parser import parse_resume_text


SAMPLE_RESUME_TEXT = """
Rahul Sharma
rahul.sharma@example.com
+91 9876543210
BCA in Computer Science
3 years experience in Python and Flask development
Skills: Python, Flask, MySQL, REST API
AWS Certified Cloud Practitioner
"""


class ParserTests(unittest.TestCase):
    def test_parse_resume_text(self):
        parsed = parse_resume_text(SAMPLE_RESUME_TEXT)
        self.assertEqual(parsed["candidate_name"], "Rahul Sharma")
        self.assertEqual(parsed["email"], "rahul.sharma@example.com")
        self.assertIn("Python", parsed["skills"])
        self.assertGreaterEqual(parsed["experience_years"], 3)


if __name__ == "__main__":
    unittest.main()
