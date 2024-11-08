console.log("External JS Loaded!");

// Utility function to retrieve CSRF token
function getCsrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}

// Function to update the "assigned_to" dropdown based on selected skills
function updateAssetDropdown(skillIds, filterAssetsUrl) {
    const assetsDropdown = $('#id_assigned_to');
    const noAssetsWarning = $('#no-assets-warning');

    // Always clear the dropdown initially and add "Unassigned" as the default option
    assetsDropdown.empty();
    assetsDropdown.append($('<option>', { value: '', text: 'Unassigned' }));

    if (skillIds.length > 0) {
        $.ajax({
            headers: { "X-CSRFToken": getCsrfToken() },
            url: filterAssetsUrl,
            data: { 'skills[]': skillIds },
            success: function (data) {
                if (data.assets.length > 0) {
                    noAssetsWarning.addClass('d-none');
                    $.each(data.assets, function (index, asset) {
                        assetsDropdown.append($('<option>', {
                            value: asset.asset_id,
                            text: asset.name
                        }));
                    });

                    // Preserve the currently assigned asset if it is still valid
                    const currentAssigned = assetsDropdown.data('current-assigned');
                    if (currentAssigned && assetsDropdown.find(`option[value="${currentAssigned}"]`).length > 0) {
                        assetsDropdown.val(currentAssigned);
                    }
                } else {
                    // Show a warning message if no assets match the selected skills
                    noAssetsWarning.removeClass('d-none');
                    noAssetsWarning.html('No assets have the selected skills.');
                }
            },
            error: function () {
                alert('An error occurred while fetching assets. Please try again.');
            }
        });
    } else {
        // If no skills are selected, clear the warning
        noAssetsWarning.addClass('d-none');
    }
}

function initializeTaskForm(projectStartDate, projectEndDate, filterAssetsUrl, getTaskDatesUrl) {
    let prereqTaskEndDate = null;

    // Function to retrieve selected skills from the form
    function getSelectedSkills() {
        const selectedSkills = [];
        $('#div_id_skills_required input[type="checkbox"]:checked').each(function () {
            selectedSkills.push($(this).val());
        });
        return selectedSkills;
    }

    // Function to handle the prerequisite task change and update planned start date
    function updateDatesFromPrereqTask(taskId) {
        if (taskId) {
            $.ajax({
                headers: { "X-CSRFToken": getCsrfToken() },
                url: getTaskDatesUrl,
                data: { 'task_id': taskId },
                success: function (data) {
                    if (data.end_date) {
                        $('#id_planned_start_date').val(data.end_date);
                        updateDateFields(data.end_date);
                        prereqTaskEndDate = new Date(data.end_date);
                        sessionStorage.setItem('prereq_task_end_date', prereqTaskEndDate); // Save end date to sessionStorage
                        $('#date-warning').addClass('d-none');
                    }
                },
                error: function () {
                    alert('An error occurred while fetching task details. Please try again.');
                }
            });
        }
    }

    // Function to update the min attributes of planned end date and due date fields
    function updateDateFields(plannedStartDate) {
        if (plannedStartDate) {
            $('#id_planned_end_date').attr('min', plannedStartDate);
            $('#id_due_date').attr('min', plannedStartDate);

            // Set default planned end date and due date to start date + 7 days if not set
            if (!$('#id_planned_end_date').val()) {
                const defaultEndDate = new Date(plannedStartDate);
                defaultEndDate.setDate(defaultEndDate.getDate() + 7);
                $('#id_planned_end_date').val(defaultEndDate.toISOString().split('T')[0]);
            }

            if (!$('#id_due_date').val()) {
                const defaultDueDate = new Date(plannedStartDate);
                defaultDueDate.setDate(defaultDueDate.getDate() + 7);
                $('#id_due_date').val(defaultDueDate.toISOString().split('T')[0]);
            }
        }
        validateDates();
    }

    // Function to validate dates and provide warnings if necessary
    function validateDates() {
        const plannedStartDate = $('#id_planned_start_date').val() ? new Date($('#id_planned_start_date').val()) : null;
        const plannedEndDate = $('#id_planned_end_date').val() ? new Date($('#id_planned_end_date').val()) : null;
        const warningDiv = $('#date-warning');
        const dependDiv = $('#dependency-warning');

        let warningMessage = '';
        let dependMessage = '';

        const projectStart = new Date(projectStartDate);
        const projectEnd = new Date(projectEndDate);

        // Retrieve prerequisite task end date from sessionStorage if not already set
        if (!prereqTaskEndDate) {
            const savedPrereqEndDate = sessionStorage.getItem('prereq_task_end_date');
            if (savedPrereqEndDate) {
                prereqTaskEndDate = new Date(savedPrereqEndDate);
            }
        }

        // Check if both prerequisite task end date and planned start date are valid
        if (prereqTaskEndDate && plannedStartDate) {
            console.log(prereqTaskEndDate, plannedStartDate);
            // Validate against the prerequisite task's end date
            if (plannedStartDate < prereqTaskEndDate) {
                warningMessage += 'Warning! The planned start date is earlier than the prerequisite task\'s end date. Please adjust.<br>';
            }
        }

        // Ensure planned end date is not earlier than start date
        if (plannedStartDate && plannedEndDate && plannedEndDate < plannedStartDate) {
            warningMessage += 'Warning! The planned end date cannot be before the planned start date. Please adjust.<br>';
        }

        // Validate against the project start and end dates
        if (plannedStartDate) {
            if (plannedStartDate < projectStart) {
                warningMessage += 'Warning! The planned start date is before the project\'s start date. Please adjust.<br>';
            }
            if (plannedStartDate > projectEnd) {
                warningMessage += 'Warning! The planned start date is after the project\'s end date. This will be saved only if you are sure.<br>';
            }
        }

        if (plannedEndDate && plannedEndDate > projectEnd) {
            warningMessage += 'Warning! The planned end date is beyond the project\'s end date. Please double-check if this is correct.<br>';
        }

        // Access parent tasks from the global variable and build dependency message
        if (window.parentTasks && window.parentTasks.length > 0) {
            dependMessage += '<strong>Dependent Tasks:</strong><br>';
            window.parentTasks.forEach(task => {
                const taskName = task.task_name;
                const taskUrl = `/projects/${task.project_id}/tasks/${task.id}/`;
                const prereqTaskStartDate = new Date(task.display_start_date).toDateString();
                const prereqTaskEndDate = new Date(task.display_end_date).toDateString();

                dependMessage += `- <a href="${taskUrl}">${taskName}</a>: Planned Start: ${prereqTaskStartDate}, Planned End: ${prereqTaskEndDate}<br>`;

                // Warn if dependent task starts before the current task ends
                if (plannedEndDate && new Date(task.display_start_date) < plannedEndDate) {
                    warningMessage += `Warning! Dependent task "${taskName}" is currently planned to start before the end date of this task. Please ensure dependent tasks are updated.<br>`;
                }
            });
        }

        // Display warnings if any
        if (warningMessage) {
            warningDiv.removeClass('d-none').html(warningMessage);
        } else {
            warningDiv.addClass('d-none').empty();
        }

        if (dependMessage) {
            dependDiv.removeClass('d-none').html(dependMessage);
        } else {
            dependDiv.addClass('d-none').empty();
        }
    }

    // Restore prerequisite task end date from sessionStorage if available
    const savedPrereqEndDate = sessionStorage.getItem('prereq_task_end_date');
    if (savedPrereqEndDate) {
        prereqTaskEndDate = new Date(savedPrereqEndDate);
    }

    // Validate dates initially to ensure all validations are applied correctly
    validateDates();

    // Event listeners
    $('#div_id_skills_required input[type="checkbox"]').on('change', function () {
        const selectedSkills = getSelectedSkills();
        updateAssetDropdown(selectedSkills, filterAssetsUrl);
    });

    $('#id_prereq_task').on('change', function () {
        const prereqTaskId = $(this).val();
        updateDatesFromPrereqTask(prereqTaskId);
    });

    $('#id_planned_start_date').on('change', function () {
        const plannedStartDate = $(this).val();
        updateDateFields(plannedStartDate);
    });

    $('#id_planned_end_date, #id_actual_end_date').on('change', function () {
        validateDates();
    });
}