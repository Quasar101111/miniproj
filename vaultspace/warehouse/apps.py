from django.apps import AppConfig
from apscheduler.schedulers.background import BackgroundScheduler
import logging

logger = logging.getLogger(__name__)

class WarehouseConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'warehouse'

    def ready(self):
        # Start the scheduler in a separate method
        self.start_scheduler()

    def start_scheduler(self):
        from .jobs import send_lease_expiry_notifications_and_cleanup
        scheduler = BackgroundScheduler()
        
        # Pass the function reference without calling it
        scheduler.add_job(
            send_lease_expiry_notifications_and_cleanup,
            trigger='cron',
            # minute='*/2',  # This will run the job every 2 minutes
            hour=0,  # Set the hour you want the job to run (e.g., midnight)
            minute=0,
            id='lease_notification_job',
            replace_existing=True
        )

        # Start the scheduler
        try:
            scheduler.start()
            logger.info("Scheduler started successfully.")
        except Exception as e:
            logger.error(f"Failed to start scheduler: {e}")

        logger.info("Lease expiry notification job scheduled to run every 2 minutes.")

        # Remove the immediate test run
        # send_lease_expiry_notifications_and_cleanup()  # This line is removed
