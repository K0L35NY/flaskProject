document.addEventListener("DOMContentLoaded", function () {

    const exerciseCheckboxes = document.querySelectorAll(".exercise");
    const readCheckboxes = document.querySelectorAll(".read");
    const meditateCheckboxes = document.querySelectorAll(".meditate");

    //changes for checkboxes
    exerciseCheckboxes.forEach((checkbox) => {
        checkbox.addEventListener("change", updateProgress);
    });
    readCheckboxes.forEach((checkbox) => {
        checkbox.addEventListener("change", updateProgress);
    });
    meditateCheckboxes.forEach((checkbox) => {
        checkbox.addEventListener("change", updateProgress);
    });

    //progress upgrade
    function updateProgress() {

        const exerciseProgress = calculateProgress(exerciseCheckboxes);
        const readProgress = calculateProgress(readCheckboxes);
        const meditateProgress = calculateProgress(meditateCheckboxes);


        document.querySelector(".exercise-progress").textContent = `${exerciseProgress}%`;
        document.querySelector(".read-progress").textContent = `${readProgress}%`;
        document.querySelector(".meditate-progress").textContent = `${meditateProgress}%`;
    }

    //calculating progress
    function calculateProgress(checkboxes) {
        const total = checkboxes.length;
        const checked = Array.from(checkboxes).filter((checkbox) => checkbox.checked).length;
        const progress = (checked / total) * 100;
        return progress.toFixed(0);
    }


    updateProgress();
});
