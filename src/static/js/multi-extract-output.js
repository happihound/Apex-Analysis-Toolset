document.addEventListener('DOMContentLoaded', function () {
    console.log('Results Page Loaded');

    // Retrieve the selected options from the embedded script tag
    var optionsDataElement = document.getElementById('options-data');
    if (optionsDataElement) {
        var selectedOptions = JSON.parse(optionsDataElement.textContent);
        var optionsList = document.getElementById('optionsList');
        selectedOptions.forEach(option => {
            var li = document.createElement('li');
            var formattedOption = option.replace(/_/g, ' ').replace(/^\w/, c => c.toUpperCase());
            li.textContent = formattedOption;
            optionsList.appendChild(li);
        });
    }
});