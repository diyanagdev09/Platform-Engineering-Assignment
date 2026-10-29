
import streamlit as st
from agent import research

st.set_page_config(
    page_title="AI Research Agent",
    page_icon="🔎",
    layout="wide"
)

# Header
st.title("🔎 AI Research Agent")
st.caption(
    "Research orchestration · Source discovery · "
    "Structured findings"
)

st.write(
    "Enter a research question to generate a research plan, "
    "search available sources, and organize the results."
)

st.divider()

# Research input
question = st.text_area(
    "Research question",
    placeholder=(
        "Example: Compare vector databases for RAG applications."
    ),
    height=100,
    key="research_question"
)

run_research = st.button(
    "Run research",
    type="primary",
    use_container_width=True
)

if run_research:
    if not question.strip():
        st.warning("Please enter a research question.")
    else:
        try:
            with st.spinner(
                "Planning research and collecting source results..."
            ):
                report = research(question.strip())

            if not isinstance(report, dict):
                st.error("The research agent returned an invalid report.")

            elif report.get("error"):
                st.error(report["error"])

            else:
                st.session_state["research_report"] = report

        except Exception as error:
            st.error(
                "The research run failed unexpectedly. "
                "Check the terminal logs for details."
            )
            print(f"Research interface error: {error}")

# Display the most recent report
report = st.session_state.get("research_report")

if report:
    st.divider()
    st.header("Research report")
    
    # Research tool health
    st.subheader("Research tool status")

    tool_status = report.get("tool_status", {})

    if not tool_status:
        st.caption(
            "Tool-level status is unavailable for this report."
        )
    else:
        status_columns = st.columns(len(tool_status))

        for column, (tool_name, status) in zip(
            status_columns, tool_status.items()
        ):
            with column:
                if status.get("ok"):
                    st.success(f"{tool_name}: Successful")
                else:
                    st.error(f"{tool_name}: Failed")

                    error_message = status.get("error")
                    if error_message:
                        st.caption(str(error_message))


    st.caption(f"Question: {report.get('question', 'Not provided')}")

    findings = report.get("key_findings", [])
    sources = report.get("sources_used", [])
    plan = report.get("plan", [])

    # Overview metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Findings collected", len(findings))

    with col2:
        st.metric("Sources listed", len(sources))

    with col3:
        st.metric(
            "Research status",
            "Results found" if findings else "No results"
        )

    # Short answer
    st.subheader("Short answer")
    st.write(
        report.get(
            "short_answer",
            "No summary was provided by the research agent."
        )
    )

    # Findings
    st.subheader("Key findings")

    if findings:
        for index, finding in enumerate(findings, start=1):
            title = finding.get("title", "Untitled finding")
            source_name = finding.get("source", "Unknown source")
            year = finding.get("year")
            url = finding.get("url")

            with st.container(border=True):
                st.markdown(f"**{index}. {title}**")

                details = source_name
                if year:
                    details += f" · {year}"

                st.caption(details)

                snippet = finding.get("snippet")
                if snippet:
                    st.write(snippet)

                if url:
                    st.markdown(f"[Open original source]({url})")

                metadata_rating = finding.get("metadata_rating")
                metadata_score = finding.get("metadata_score")

                if metadata_rating:
                    if metadata_score is not None:
                        st.caption(
                            f"Metadata completeness: {metadata_rating} "
                            f"({metadata_score}/4)"
                        )
                    else:
                        st.caption(
                            f"Metadata completeness: {metadata_rating}"
                        )

                quality_notes = finding.get("quality_notes", [])
                if quality_notes:
                    with st.expander("Metadata notes"):
                        for note in quality_notes:
                            st.write(f"- {note}")
    else:
        st.info(
            "No usable findings were retrieved. "
            "Check your connection or try a different question."
        )

    # Confidence
    st.subheader("Confidence")
    st.info(
        report.get(
            "confidence",
            "Confidence information is unavailable."
        )
    )

    # Limitations
    with st.expander("Limitations and assumptions", expanded=True):
        limitations = report.get("limitations", [])

        if limitations:
            for item in limitations:
                st.write(f"- {item}")
        else:
            st.write("No limitations were provided.")

    # Next steps
    with st.expander("Suggested next steps", expanded=True):
        next_steps = report.get("next_steps", [])

        if next_steps:
            for item in next_steps:
                st.write(f"- {item}")
        else:
            st.write("No next steps were provided.")

    # Research plan
    with st.expander("View research plan"):
        if plan:
            for index, step in enumerate(plan, start=1):
                st.write(f"{index}. {step}")
        else:
            st.write("No research plan was provided.")

    # Source list
    with st.expander("View complete source list"):
        if sources:
            for source in sources:
                title = source.get("title", "Untitled source")
                source_name = source.get("source", "Unknown source")
                url = source.get("url")
                year = source.get("year")

                st.markdown(f"**{title}**")

                details = source_name
                if year:
                    details += f" · {year}"

                st.caption(details)

                if url:
                    st.markdown(f"[Open source]({url})")

                st.divider()
        else:
            st.write("No sources were listed.")
