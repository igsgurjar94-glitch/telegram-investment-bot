import datetime
import logging

def get_current_time():
    """Returns current date and time as string"""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def format_message(text):
    """Format message with timestamp"""
    return f"📅 {get_current_time()}\n\n{text}"

def is_valid_number(text):
    """Check if text is a valid number"""
    try:
        float(text)
        return True
    except ValueError:
        return False
