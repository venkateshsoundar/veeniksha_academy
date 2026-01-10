const studentSelect = document.getElementById('student-select');
const warningBanner = document.getElementById('capacity-warning');

if (studentSelect && warningBanner) {
    const updateWarning = () => {
        const selectedCount = Array.from(studentSelect.selectedOptions).length;
        warningBanner.classList.toggle('hidden', selectedCount <= 2);
    };

    studentSelect.addEventListener('change', updateWarning);
    updateWarning();
}
