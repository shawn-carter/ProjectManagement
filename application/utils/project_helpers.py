from datetime import date

def calculate_rag_status(project):
    # If the project is closed, always return Green (G)
    if project.project_status == 7:
        return 'G'
    
    # Continue with existing logic
    all_tasks = project.task_set.all()
    completed_tasks_count = all_tasks.filter(task_status=3).count()
    total_tasks_count = all_tasks.count()

    # If no tasks, default to Green if closed, else Amber
    if total_tasks_count == 0:
        return 'A' if project.project_status != 7 else 'G'

    # Calculate percentage of tasks completed
    percent_completed = (completed_tasks_count / total_tasks_count) * 100

    # Determine time remaining and RAG status
    display_start_date = project.display_start_date
    display_end_date = project.display_end_date
    if display_end_date and display_start_date:
        today = date.today()
        total_days = (display_end_date - display_start_date).days
        remaining_days = (display_end_date - today).days if today <= display_end_date else 0

        if percent_completed >= 100:
            return 'G'
        elif total_days > 0:
            progress_rate = percent_completed / 100
            remaining_rate = remaining_days / total_days

            if remaining_rate > 0.75:
                return 'G'
            elif 0.25 < remaining_rate <= 0.75:
                return 'A'
            else:
                return 'R'
        else:
            return 'R'

    return 'A'  # Default to Amber if dates are missing or not meaningful