document.addEventListener("DOMContentLoaded", function () {

    const checkboxes = document.querySelectorAll(".habit-tracker input[type='checkbox']");
    checkboxes.forEach((checkbox) => {
        checkbox.addEventListener("change", updateCheckboxState);
    });

    function updateCheckboxState(event) {
        const habitId = event.target.dataset.habitId;
        const dayIndex = event.target.dataset.dayIndex;
        const isChecked = event.target.checked;

        const url = `/update_checkbox_state?habit_id=${habitId}&day_index=${dayIndex}&checked=${isChecked.toString()}`;

        fetch(url)
            .then(response => response.json())
            .then(data => {
                console.log(data);
                // After updating the server, fetch updated habit data and update progress
                console.log('checkbox state updated')
                updateProgress(habitId);
            })
            .catch(error => {
                console.error('Error updating checkbox state:', error);
            });
    }

    function updateProgress(habitId) {
        const checkboxes = document.querySelectorAll(`input[data-habit-id='${habitId}']`);
        const totalCheckboxes = checkboxes.length;
        const checkedCheckboxes = Array.from(checkboxes).filter(checkbox => checkbox.checked);
        const numChecked = checkedCheckboxes.length;
        const progress = (numChecked / totalCheckboxes) * 100;
        const progressElement = document.querySelector(`.habit-${habitId}-progress`);
        progressElement.textContent = `${progress.toFixed(0)}%`;
    }

    // Get all unique habit IDs from the checkboxes
    const habitIds = Array.from(new Set(Array.from(checkboxes).map(checkbox => checkbox.dataset.habitId)));

    // Call updateProgress for each habit ID
    habitIds.forEach(habitId => updateProgress(habitId));

    var addHabitButton = document.querySelector(".addHabitButton");
    var habitModal = document.getElementById("addHabitModal");

    addHabitButton.addEventListener("click", function () {
        habitModal.style.display = "block";
    });

    var closeModalButton = habitModal.querySelector(".close");
    closeModalButton.addEventListener("click", function () {
        habitModal.style.display = "none";
    });

    window.addEventListener("click", function (event) {
        if (event.target === habitModal) {
            habitModal.style.display = "none";
        }
    });

    updateProgress();

});
