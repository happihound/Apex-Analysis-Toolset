document.addEventListener('DOMContentLoaded', function () {
    var selectAllCheckbox = document.getElementById('selectAll');
    var checkboxes = document.querySelectorAll('input[type="checkbox"].section');
    var submit_endpoint1 = document.getElementById('submit-endpoint').textContent;
    var client_id = document.getElementById('client-id').textContent;
    console.log('Client ID:', client_id);
    selectAllCheckbox.addEventListener('change', function () {
        checkboxes.forEach(checkbox => checkbox.checked = selectAllCheckbox.checked);
    });

    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function () {
            var allChecked = Array.from(checkboxes).every(c => c.checked);
            selectAllCheckbox.checked = allChecked;
            selectAllCheckbox.indeterminate = !allChecked && Array.from(checkboxes).some(c => c.checked);
        });
    });

    var coll = document.getElementsByClassName("collapsible collapsible-extract");
    console.log('Number of collapsible-extract elements:', coll.length);
    for (var i = 0; i < coll.length; i++) {
        coll[i].addEventListener("click", function () {
            console.log('Collapsible button clicked (extract.js)');
            this.classList.toggle("active");
            var content = this.nextElementSibling;
            if (content.style.display === "block") {
                content.style.display = "none";
            } else {
                content.style.display = "block";
            }
        });
    }
});
