console.log("Custom JS Loaded!");

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

// Function to initialize the task form
function initializeTaskForm(projectStartDate, projectEndDate, filterAssetsUrl, getTaskDatesUrl) {
    let dependentTaskEndDate = null;

    // Function to retrieve selected skills from the form
    function getSelectedSkills() {
        const selectedSkills = [];
        $('#div_id_skills_required input[type="checkbox"]:checked').each(function () {
            selectedSkills.push($(this).val());
        });
        return selectedSkills;
    }

    // Function to handle the dependent task change and update planned start date
    function updateDatesFromDependentTask(taskId) {
        if (taskId) {
            $.ajax({
                headers: { "X-CSRFToken": getCsrfToken() },
                url: getTaskDatesUrl,
                data: { 'task_id': taskId },
                success: function (data) {
                    if (data.end_date) {
                        $('#id_planned_start_date').val(data.end_date);
                        updateDateFields(data.end_date);
                        dependentTaskEndDate = new Date(data.end_date);
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
        }
        validateDates();
    }

    // Function to validate dates and provide warnings if necessary
    function validateDates() {
        const plannedStartDate = $('#id_planned_start_date').val() ? new Date($('#id_planned_start_date').val()) : null;
        const plannedEndDate = $('#id_planned_end_date').val() ? new Date($('#id_planned_end_date').val()) : null;
        const warningDiv = $('#date-warning');
        let warningMessage = '';

        const projectStart = new Date(projectStartDate);
        const projectEnd = new Date(projectEndDate);

        if (dependentTaskEndDate && plannedStartDate && plannedStartDate < dependentTaskEndDate) {
            warningMessage += 'Warning! The planned start date is earlier than the dependent task\'s end date. Please adjust.<br>';
        }

        if (plannedStartDate && plannedEndDate && plannedEndDate < plannedStartDate) {
            warningMessage += 'Warning! The planned end date cannot be before the planned start date. Please adjust.<br>';
        }

        if (plannedStartDate && (plannedStartDate < projectStart || plannedStartDate > projectEnd)) {
            warningMessage += 'Warning! The planned start date is outside of the project\'s date range. This will be saved only if you are sure.<br>';
        }

        if (plannedEndDate && plannedEndDate > projectEnd) {
            warningMessage += 'Warning! The planned end date is beyond the project\'s end date. Please double-check if this is correct.<br>';
        }

        if (warningMessage) {
            warningDiv.removeClass('d-none');
            warningDiv.html(warningMessage);
        } else {
            warningDiv.addClass('d-none');
        }
    }

    // Event listeners
    $('#div_id_skills_required input[type="checkbox"]').on('change', function () {
        const selectedSkills = getSelectedSkills();
        updateAssetDropdown(selectedSkills, filterAssetsUrl);
    });

    $('#id_dependant_task').on('change', function () {
        const dependentTaskId = $(this).val();
        updateDatesFromDependentTask(dependentTaskId);
    });

    $('#id_planned_start_date').on('change', function () {
        const plannedStartDate = $(this).val();
        updateDateFields(plannedStartDate);
    });

    $('#id_planned_end_date, #id_actual_end_date').on('change', function () {
        validateDates();
    });

    // Initial setup
    const initialPlannedStartDate = $('#id_planned_start_date').val();
    updateDateFields(initialPlannedStartDate);
    validateDates();
}
