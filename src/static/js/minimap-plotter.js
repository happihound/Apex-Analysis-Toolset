document.addEventListener("DOMContentLoaded", function () {
    const mapRadios = document.querySelectorAll('input[name="map"]');
    const ratioRadios = document.querySelectorAll('input[name="ratio"]');
    const mapImage = document.getElementById('mapImage');

    const updateImage = () => {
        const selectedMap = document.querySelector('input[name="map"]:checked');
        const selectedRatio = document.querySelector('input[name="ratio"]:checked');
        if (selectedMap && selectedRatio) {
            const mapValue = selectedMap.value;
            const ratioValue = selectedRatio.value.replace(':', 'by');
            const imagePath = `static/images/maps/${ratioValue}/${mapValue}${ratioValue}.jpg`;
            mapImage.src = imagePath;
            mapImage.alt = `${mapValue} - ${ratioValue}`;
            // Update data-ratio attributes for selected map
            mapRadios.forEach(radio => {
                radio.dataset.ratio = ratioValue;
            });
        }
    };

    mapRadios.forEach(radio => {
        radio.addEventListener('change', updateImage);
    });

    ratioRadios.forEach(radio => {
        radio.addEventListener('change', updateImage);
    });
});
