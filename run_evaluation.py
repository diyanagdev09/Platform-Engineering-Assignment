import json
from datetime import datetime
from pathlib import Path

from agent import research


CASES_FILE = Path("evaluation_cases.json")
RESULTS_FILE = Path("evaluation_results.json")


def evaluate_case(case):
    question = case["question"]

    result = {
        "id": case["id"],
        "question": question,
        "test_type": case["test_type"],
        "expected_behavior": case["expected_behavior"],
        "status": "FAIL",
        "checks": [],
        "error": None
    }

    try:
        report = research(question)

        # Check 1: Empty questions should be rejected.
        if not question.strip():
            passed = (
                isinstance(report, dict)
                and "error" in report
            )
            result["checks"].append({
                "name": "Empty question rejected",
                "passed": passed
            })

        else:
            # Check 1: A structured report should be returned.
            required_fields = [
                "question",
                "short_answer",
                "key_findings",
                "sources_used",
                "confidence",
                "limitations",
                "next_steps"
            ]

            has_structure = all(
                field in report for field in required_fields
            )

            result["checks"].append({
                "name": "Structured report",
                "passed": has_structure
            })

            # Check 2: Findings and sources should be lists.
            valid_lists = (
                isinstance(report.get("key_findings"), list)
                and isinstance(report.get("sources_used"), list)
            )

            result["checks"].append({
                "name": "Findings and sources have valid format",
                "passed": valid_lists
            })

            # Check 3: Results should include source links.
            findings = report.get("key_findings", [])

            linked_findings = [
                item for item in findings
                if isinstance(item, dict)
                and isinstance(item.get("url"), str)
                and item["url"].startswith("https://")
            ]

            has_sources = len(linked_findings) > 0

            is_low_result_test = (
                case["test_type"] == "Low-result scenario"
            )

            result["checks"].append({
                "name": "At least one finding has an HTTPS link",
                "passed": has_sources or is_low_result_test
            })

            # A no-results case can still pass if the agent
            # reports the lack of results in a controlled way.
            if case["test_type"] == "Low-result scenario":
                no_results_handled = (
                    has_structure
                    and (
                        len(findings) == 0
                        or has_sources
                    )
                )

                result["checks"].append({
                    "name": "Low-result scenario handled",
                    "passed": no_results_handled
                })

        # Store a short summary, not the entire raw report.
        result["result_summary"] = report.get(
            "short_answer",
            report.get("error", "No summary returned")
        )

        result["finding_count"] = len(
            report.get("key_findings", [])
        )

        result["source_count"] = len(
            report.get("sources_used", [])
        )

        if all(check["passed"] for check in result["checks"]):
            result["status"] = "PASS"

    except Exception as error:
        result["error"] = str(error)

    return result


def main():
    with CASES_FILE.open("r", encoding="utf-8") as file:
        cases = json.load(file)

    results = []

    for case in cases:
        print(f"\nTesting case {case['id']}: {case['test_type']}")
        outcome = evaluate_case(case)
        results.append(outcome)

        print("Status:", outcome["status"])

        for check in outcome["checks"]:
            print(
                f"  {'PASS' if check['passed'] else 'FAIL'}"
                f" - {check['name']}"
            )

        if outcome["error"]:
            print("Error:", outcome["error"])

    summary = {
        "run_at": datetime.now().isoformat(timespec="seconds"),
        "total": len(results),
        "passed": sum(r["status"] == "PASS" for r in results),
        "failed": sum(r["status"] == "FAIL" for r in results),
        "results": results
    }

    with RESULTS_FILE.open("w", encoding="utf-8") as file:
        json.dump(summary, file, indent=2, ensure_ascii=False)

    print("\n=== EVALUATION SUMMARY ===")
    print(f"Total:  {summary['total']}")
    print(f"Passed: {summary['passed']}")
    print(f"Failed: {summary['failed']}")
    print(f"Saved results to: {RESULTS_FILE}")


if __name__ == "__main__":
    main()
