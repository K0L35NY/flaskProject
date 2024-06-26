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
    // habit goal color coding
    let colors = {
        1: '#D1BDFF',
        2: '#E2CBF7',
        3: '#D6F6FF',
        4: '##B3F5BC',
        5: '#F9FFB5',
        6: '#FCAE7C',
        7: '#FA9189'
    };

    // Get all .goal-days elements
    let elements = document.querySelectorAll('.goal-days');

    elements.forEach(element => {
        // Extract the number from the element's text content
        let habitGoalDays = parseInt(element.textContent.trim().split(' ')[0]);

        // Set the background color based on the habit.goal_days value
        element.style.backgroundColor = colors[habitGoalDays];
    });
    updateProgress();

});

    function toggleDarkMode() {
        const body = document.body;
        body.classList.toggle('dark-mode');

        // Save preference in localStorage
        localStorage.setItem('darkMode', body.classList.contains('dark-mode'));
    }

    // Load user preference on page load
    document.addEventListener('DOMContentLoaded', () => {
        if (localStorage.getItem('darkMode') === 'true') {
            document.body.classList.add('dark-mode');
        }
});

    window.onload = function() {
        // Initially hide the to-do container
        document.getElementById('to-do-container').style.display = 'none';

        // Get all elements with class="day"
        var days = document.getElementsByClassName('day');

        // Attach a click event handler to each day
        for (var i = 0; i < days.length; i++) {
            days[i].addEventListener('click', function() {
                // Hide the calendar
                document.getElementById('calendar').style.display = 'none';
                // Show the to-do container
                document.getElementById('to-do-container').style.display = 'block';
            });
        }
};

    document.getElementById('back-button').addEventListener('click', function() {
        // Show the calendar
        document.getElementById('calendar').style.display = 'block';
        // Hide the to-do container
        document.getElementById('to-do-container').style.display = 'none';
});
