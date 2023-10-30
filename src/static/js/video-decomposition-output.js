document.addEventListener('DOMContentLoaded', function () {
    console.log('Results Page Loaded');

    // Retrieve the selected options from the embedded script tag
    const optionsDataElement = document.getElementById('options-data');
    if (optionsDataElement) {
        const selectedOptions = JSON.parse(optionsDataElement.textContent);
        const optionsList = document.getElementById('optionsList');
        selectedOptions.forEach(option => {
            const li = document.createElement('li');
            const formattedOption = option.replace(/_/g, ' ').replace(/^\w/, c => c.toUpperCase());
            li.textContent = formattedOption;
            optionsList.appendChild(li);
        });
    }
});