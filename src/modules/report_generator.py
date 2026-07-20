import markdown


def generate_morning_report():
    # Retrieve build status and night's work data from database
    build_status = get_build_status_from_db()
    nights_work = get_nights_work_from_db()

    # Format report content
    report_content = (
        "# Morning Report\n\n"
        + "\n".join([f"# {night}" for night in nights_work])
        + "\n\nBuild Status: "
        + build_status
    )

    # Save report to file
    with open("MORNING_REPORT.md", "w") as f:
        f.write(markdown.markdown(report_content))


def get_build_status_from_db():
    """Stub for retrieving build status from the database."""
    return "Unknown"


def get_nights_work_from_db():
    """Stub for retrieving night's work items from the database."""
    return ["No work items recorded"]
