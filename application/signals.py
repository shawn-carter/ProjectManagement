from django.db.models.signals import post_migrate
from django.dispatch import receiver
from application.models import TaskStatus, ProjectStatus, Skill, DayOfWeek  # Import models
import logging

# Set up logging to see which functions are executed
logger = logging.getLogger(__name__)

# Ensure the signals are executed once
signal_executed = {'status': False, 'skills': False, 'days': False}


@receiver(post_migrate)
def create_default_data(sender, **kwargs):
    if signal_executed['status']:
        logger.info("Default Task and Project Statuses creation skipped because it has already been executed.")
        return

    # Create default Task Statuses
    task_statuses = [
        {'status_id': 1, 'status_name': 'Unassigned', 'description': 'Task not assigned yet'},
        {'status_id': 2, 'status_name': 'Assigned', 'description': 'Task has been assigned'},
        {'status_id': 3, 'status_name': 'Completed', 'description': 'Task is completed'}
    ]

    for status in task_statuses:
        TaskStatus.objects.get_or_create(status_id=status['status_id'], defaults=status)

    # Create default Project Statuses
    project_statuses = [
        {'status_id': 1, 'status_name': 'New', 'description': 'Newly created project'},
        {'status_id': 2, 'status_name': 'Awaiting Closure', 'description': 'Awaiting final closure'},
        {'status_id': 3, 'status_name': 'In Progress', 'description': 'Currently being worked on'},
        {'status_id': 4, 'status_name': 'On Hold', 'description': 'Project is on hold'},
        {'status_id': 5, 'status_name': 'Scoping', 'description': 'Project is being scoped out'},
        {'status_id': 6, 'status_name': 'Responded', 'description': 'Response is complete'},
        {'status_id': 7, 'status_name': 'Closed', 'description': 'Project is closed'}
    ]

    for status in project_statuses:
        ProjectStatus.objects.get_or_create(status_id=status['status_id'], defaults=status)

    signal_executed['status'] = True
    logger.info("Default Task and Project Statuses created successfully.")


@receiver(post_migrate)
def create_default_skills(sender, **kwargs):
    if signal_executed['skills']:
        logger.info("Default Skills creation skipped because it has already been executed.")
        return

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

    signal_executed['skills'] = True
    logger.info("Default Skills created successfully.")


@receiver(post_migrate)
def create_default_days(sender, **kwargs):
    if signal_executed['days']:
        logger.info("Default Days creation skipped because it has already been executed.")
        return

    # Define the default days of the week
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

    signal_executed['days'] = True
    logger.info("Default Days created successfully.")
