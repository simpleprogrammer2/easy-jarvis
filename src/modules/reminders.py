import subprocess
import logging

logger = logging.getLogger("Reminders")


def get_apple_reminders():
    """Fetches active reminders (name and due date) from macOS Reminders app using AppleScript."""
    script = """
    tell application "Reminders"
        set resultList to {}
        try
            set theList to default list
            repeat with aReminder in (reminders of theList whose completed is false)
                set reminderName to (name of aReminder)
                set dueDate to (due date of aReminder)
                if dueDate is missing value then
                    set end of resultList to reminderName
                else
                    -- Format date and time
                    set end of resultList to (reminderName & " (Due: " & (short date string of dueDate) & " " & (time string of dueDate) & ")")
                end if
            end repeat
            set AppleScript's text item delimiters to "\\n"
            return resultList as string
        on error
            return "Error: Could not access Reminders"
        end try
    end tell
    """
    try:
        result = subprocess.run(
            ["osascript", "-e", script], capture_output=True, text=True, check=True
        )
        reminders_str = result.stdout.strip()
        if not reminders_str:
            return []
        if reminders_str == "Error: Could not access Reminders":
            return ["Error: Could not access Reminders"]
        return reminders_str.split("\n")
    except Exception as e:
        logger.error(f"Failed to fetch reminders: {e}")
        return ["Error accessing Reminders."]
