import unittest
from types import SimpleNamespace

from backend.services.matching_service import (
    calculate_experience_score,
    calculate_skill_score,
    score_resume_against_job,
)


class MatchingTests(unittest.TestCase):
    def test_skill_score(self):
        score, matched, missing = calculate_skill_score(
            ["Python", "Flask", "MySQL"],
            ["Python", "MySQL"],
        )
        self.assertEqual(score, 66.67)
        self.assertEqual(matched, ["mysql", "python"])
        self.assertEqual(missing, ["flask"])

    def test_experience_score(self):
        self.assertEqual(calculate_experience_score(4, 2), 100.0)
        self.assertEqual(calculate_experience_score(1, 2), 50.0)

    def test_score_resume_against_job(self):
        resume = SimpleNamespace(
            skills="Python, Flask, MySQL",
            skill_list=["Python", "Flask", "MySQL"],
            education="BCA in Computer Science",
            experience_text="2 years experience in backend development",
            experience_years=2,
            raw_text="Python Flask MySQL REST API backend developer",
        )
        job = SimpleNamespace(
            title="Python Developer",
            description_text="Need Flask and MySQL experience",
            required_skills="Python, Flask, MySQL",
            required_skill_list=["Python", "Flask", "MySQL"],
            keywords="backend, api",
            qualifications="BCA, BTech",
            min_experience=2,
        )
        result = score_resume_against_job(resume, job)

        self.assertGreaterEqual(result["suitability_score"], 80)
        self.assertEqual(result["recommendation"], "Strong Match")


if __name__ == "__main__":
    unittest.main()
