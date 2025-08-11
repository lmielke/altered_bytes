"""
API entry point for info_app_hist_activities module.
"""

from altered.info_app_hist_activities import ActivityHistory, UserActivity

def main(*args, **kwargs):
    """
    Run the activity monitor in foreground.
    """
    user_activity = UserActivity()
    history = ActivityHistory(user_activity=user_activity)
    print("Monitoring started (PM2-controlled)... Ctrl+C to stop.")
    history.monitor_window_changes()
