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
                fetchAndUpdateProgress(habitId);
            })
            .catch(error => {
                console.error('Error updating checkbox state:', error);
            });
    }

    function fetchAndUpdateProgress(habitId) {
        // Fetch updated habit data for the specific habit
        fetch(`/get_habit_data?habit_id=${habitId}`)
            .then(response => response.json())
            .then(habitData => {
                // Update the progress element
                const progressElement = document.querySelector(`.habit-${habitId}-progress`);
                progressElement.textContent = `${habitData.progress}%`;
            })
            .catch(error => {
                console.error('Error fetching habit data:', error);
            });
    }

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

    fetchAndUpdateProgress();  // Initial update when the page loads
});
