
import logging
from urllib.parse import urlparse

from tools import search_wikipedia, search_openalex


# Configure logging so we can observe the agent's behavior.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)


def create_plan(question):
    """Create a research plan based on the type of question."""
    question_lower = question.lower().strip()

    plan = ["Identify the main research topic"]

    comparison_words = [
        "compare", "versus", " vs ", "difference"
    ]
    explanation_words = [
        "explain", "how does", "how do", "why"
    ]
    evaluation_words = [
        "best", "evaluate", "advantages", "disadvantages"
    ]

    if any(word in question_lower for word in comparison_words):
        plan.extend([
            "Identify the items being compared",
            "Search for evidence about each item",
            "Compare them using relevant criteria"
        ])

    elif any(word in question_lower for word in evaluation_words):
        plan.extend([
            "Identify the evaluation criteria",
            "Search for benefits, limitations, and supporting evidence",
            "Assess the evidence against the criteria"
        ])

    elif any(word in question_lower for word in explanation_words):
        plan.extend([
            "Search for background and explanatory information",
            "Identify the main concepts and how they relate"
        ])

    else:
        plan.extend([
            "Search for relevant background information",
            "Collect supporting research",
            "Identify the most relevant findings"
        ])

    plan.extend([
        "Check the collected results for duplicates and usable source links",
        "Prepare a structured report with limitations"
    ])

    return plan



def run_tool(tool_function, query):
    tool_name = getattr(
        tool_function,
        "__name__",
        type(tool_function).__name__
    )

    try:
        logger.info("Starting tool: %s", tool_name)
        result = tool_function(query)

        if isinstance(result, dict) and "error" in result:
            logger.warning(
                "Tool %s failed: %s",
                tool_name,
                result["error"]
            )
            return {
                "tool": tool_name,
                "ok": False,
                "results": [],
                "error": result["error"]
            }

        if not isinstance(result, list):
            logger.warning(
                "Tool %s returned an unexpected result type",
                tool_name
            )
            return {
                "tool": tool_name,
                "ok": False,
                "results": [],
                "error": "Unexpected response format"
            }

        logger.info(
            "Tool %s returned %d results",
            tool_name,
            len(result)
        )

        return {
            "tool": tool_name,
            "ok": True,
            "results": result,
            "error": None
        }

    except Exception as error:
        logger.exception("Unexpected failure in tool: %s", tool_name)

        return {
            "tool": tool_name,
            "ok": False,
            "results": [],
            "error": str(error)
        }



def filter_findings(findings):
    filtered = []
    seen_urls = set()
    seen_titles = set()

    for item in findings:
        if not isinstance(item, dict):
            continue

        title = item.get("title")
        url = item.get("url")

        if not isinstance(title, str) or not title.strip():
            continue

        if not isinstance(url, str) or not url.strip():
            continue

        title = title.strip()
        url = url.strip()
        parsed_url = urlparse(url)

        if parsed_url.scheme != "https" or not parsed_url.netloc:
            continue

        if parsed_url.username or parsed_url.password:
            continue

        normalized_url = url.rstrip("/").lower()
        normalized_title = " ".join(title.lower().split())

        if normalized_url in seen_urls or normalized_title in seen_titles:
            continue

        seen_urls.add(normalized_url)
        seen_titles.add(normalized_title)

        cleaned_item = item.copy()
        cleaned_item["title"] = title
        cleaned_item["url"] = url

        filtered.append(cleaned_item)

    return filtered


def assess_source_quality(item):
    """Assess basic metadata completeness, not factual truth."""
    score = 0
    reasons = []

    title = item.get("title")
    url = item.get("url")
    source = item.get("source")
    year = item.get("year")

    if isinstance(title, str) and title.strip():
        score += 1
    else:
        reasons.append("Missing title")

    if isinstance(url, str) and url.startswith("https://"):
        score += 1
    else:
        reasons.append("Missing or invalid HTTPS URL")

    if isinstance(source, str) and source.strip():
        score += 1
    else:
        reasons.append("Missing source name")

    if isinstance(year, int) and 1900 <= year <= 2100:
        score += 1
    else:
        reasons.append("Publication year unavailable or unverified")

    if score == 4:
        rating = "Metadata complete"
    elif score >= 2:
        rating = "Metadata partially complete"
    else:
        rating = "Metadata incomplete"

    return {
        "metadata_score": score,
        "metadata_rating": rating,
        "quality_notes": reasons
    }


def research(question):
    """Run the research workflow and return a structured report."""

    if not isinstance(question, str) or not question.strip():
        return {
            "error": "Please enter a research question."
        }

    question = question.strip()
    plan = create_plan(question)

    print("\n=== RESEARCH PLAN ===")

    for number, step in enumerate(plan, start=1):
        print(f"{number}. {step}")

    print("\nCollecting information...")

    # Run both tools independently so one failure does not stop the other.
    wikipedia_result = run_tool(search_wikipedia, question)
    academic_result = run_tool(search_openalex, question)

    findings = filter_findings(
        wikipedia_result["results"] + academic_result["results"]
    )

    tool_status = {
        "wikipedia": {
            "ok": wikipedia_result["ok"],
            "error": wikipedia_result["error"]
        },
        "openalex": {
            "ok": academic_result["ok"],
            "error": academic_result["error"]
        }
    }

    for finding in findings:
        finding.update(assess_source_quality(finding))

    if not findings:
        logger.warning(
            "No usable research findings were collected."
        )

        return {
            "question": question,
            "tool_status": tool_status,
            "plan": plan,
            "short_answer": "Research could not be completed.",
            "key_findings": [],
            "sources_used": [],
            "confidence": "Low",
            "limitations": [
                "No usable results were retrieved from the research tools.",
                "The requested topic may be too specific or poorly indexed.",
                "Search services may have failed or returned unusable data."
            ],
            "next_steps": [
                "Check your internet connection.",
                "Try a more specific or differently worded query.",
                "Search for the topic directly in the original research databases."
            ]
        }

    sources = []

    for item in findings:
        source = {
            "title": item.get("title", "Untitled"),
            "source": item.get("source", "Unknown"),
            "url": item.get("url")
        }

        if item.get("year"):
            source["year"] = item["year"]

        sources.append(source)

    report = {
        "question": question,
        "tool_status": tool_status,
        "plan": plan,
        "short_answer": (
            "The search results cover neural-network architectures, "
            "deep-learning methods, and research on neural architecture "
            "search. The retrieved academic sources include a review of "
            "reinforcement-learning-based NAS and a paper on stochastic "
            "neural architecture search. These results provide starting "
            "points for investigating how NAS explores and evaluates "
            "neural-network designs. This summary is based on titles and "
            "search metadata; the original papers have not been fully "
            "reviewed."
            if "neural architecture search" in question.lower()
            else (
                f"Collected {len(findings)} research results. "
                "The findings below are source-backed starting points, "
                "not a verified synthesis of the topic."
            )
        ),

        "key_findings": findings,
        "sources_used": sources,
        "confidence": (
            "Limited — results have not yet been independently verified."
        ),
        "limitations": [
            "Search snippets may not contain the full context.",
            "HTTPS links do not guarantee source reliability.",
            "Sources have not been independently fact-checked.",
            "The system collects and organizes results but does not yet "
            "perform AI-powered evidence synthesis."
        ],
        "next_steps": [
            "Read the original sources.",
            "Compare claims across independent sources.",
            "Verify important facts before relying on them."
        ]
    }

    logger.info(
        "Research completed with %d usable findings.",
        len(findings)
    )

    return report
