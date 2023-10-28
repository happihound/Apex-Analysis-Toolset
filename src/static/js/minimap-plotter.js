document.addEventListener("DOMContentLoaded", function () {
    const mapRadios = document.querySelectorAll('input[name="map"]');
    const ratioRadios = document.querySelectorAll('input[name="ratio"]');
    const mapImage = document.getElementById('mapImage');
    var ratio_status = document.getElementById('ratio_status');
    var map_status = document.getElementById('map_status');

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
        if (selectedMap) {
            map_status.innerText = `Map: ${selectedMap.value}`;
        }
        if (selectedRatio) {
            ratio_status.innerText = `Ratio: ${selectedRatio.value}`;
        }
    };

    mapRadios.forEach(radio => {
        radio.addEventListener('change', updateImage);
    });

    ratioRadios.forEach(radio => {
        radio.addEventListener('change', updateImage);
    });
});
