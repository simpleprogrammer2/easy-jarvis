def generate_morning_report():
    import datetime
    import markdown
    
    # Retrieve build status and night's work data from database
    build_status = get_build_status_from_db()
    nights_work = get_nights_work_from_db()
    
    # Format report content
    report_content = '# Morning Report
' + '
'.join([f'# {night}' for night in nights_work]) + '

Build Status: ' + build_status
    
    # Save report to file
    with open('MORNING_REPORT.md', 'w') as f:
        f.write(markdown.markdown(report_content))
