from django.db.models.signals import post_migrate
from django.dispatch import receiver
from application.models import Skill, DayOfWeek  # Import models
import logging

# Set up logging to see which functions are executed
logger = logging.getLogger(__name__)

@receiver(post_migrate)
def create_default_data(sender, **kwargs):
    # Ensure this is only executed for your application
    if sender.name != "application":
        return

    # Create Default Skills
    skills = [
        (1, "DHCP Configuration"),
        (2, "Firewall Configuration"),
        (3, "Firmstep Forms"),
        (4, "Network Commissioning"),
        (5, "Network Configuration"),
        (6, "Network Decommissioning"),
        (7, "Programming (.NET)"),
        (8, "Programming (Django)"),
        (9, "Programming (PHP)"),
        (10, "Project Management"),
        (11, "Server Commissioning"),
        (12, "Server Configuration"),
        (13, "Server Decommissioning"),
        (14, "Software Installation"),
        (15, "Software Testing"),
        (16, "SQL Database Administration"),
        (17, "SQL Database Commissioning"),
        (18, "SQL Database Decommissioning"),
        (19, "WAN Configuration"),
    ]

    for skill_id, skill_name in skills:
        try:
            # Check if the skill exists based on `skill_id` or `skill_name`
            existing_skill = Skill.objects.filter(skill_id=skill_id).first()
            if existing_skill:
                logger.info(f"Skill ID '{skill_id}' already exists, skipping.")
                continue

            # If not found, proceed to create the skill
            Skill.objects.create(skill_id=skill_id, skill_name=skill_name)
            logger.info(f"Skill '{skill_name}' added successfully.")

        except Exception as e:
            logger.error(f"Error creating skill '{skill_name}': {e}")

    logger.info("Default Skills created successfully.")

    # Create Default Days
    days_of_week = [
        {'day_name': 'Monday', 'abbreviation': 'Mon'},
        {'day_name': 'Tuesday', 'abbreviation': 'Tue'},
        {'day_name': 'Wednesday', 'abbreviation': 'Wed'},
        {'day_name': 'Thursday', 'abbreviation': 'Thu'},
        {'day_name': 'Friday', 'abbreviation': 'Fri'},
    ]

    for day in days_of_week:
        try:
            # Check if a day with the given `day_name` already exists
            if DayOfWeek.objects.filter(day_name=day['day_name']).exists():
                logger.info(f"Day '{day['day_name']}' already exists, skipping.")
                continue

            # Create the day if not exists
            DayOfWeek.objects.create(day_name=day['day_name'], abbreviation=day['abbreviation'])
            logger.info(f"Day '{day['day_name']}' added successfully.")

        except Exception as e:
            logger.error(f"Error creating day '{day['day_name']}': {e}")

    logger.info("Default Days created successfully.")
