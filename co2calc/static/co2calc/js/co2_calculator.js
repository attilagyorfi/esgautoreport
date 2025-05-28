// co2calc/static/co2calc/js/co2_calculator.js
document.addEventListener('DOMContentLoaded', function() {
    console.log('co2_calculator.js (AJAX for FK auto-select dropdown - Calculate button removed) loaded');

    const activityTypeSelect = document.getElementById('id_activity_type');
    const unitSelect = document.getElementById('id_unit');
    const periodYearSelect = document.getElementById('id_period_year');
    const emissionFactorSelect = document.getElementById('id_emission_factor'); // Ez a <select> elem

    // A calculated_co2e mező readonly, az értékét a szerver adja mentés után.
    // const calculatedCo2eDisplay = document.querySelector('.field-calculated_co2e .readonly'); 

    let factorInfoDisplay = null;
    if (emissionFactorSelect && emissionFactorSelect.parentNode) {
        factorInfoDisplay = document.createElement('span');
        factorInfoDisplay.id = 'id_factor_info_display';
        factorInfoDisplay.style.marginLeft = '10px';
        factorInfoDisplay.style.fontSize = '0.9em';
        factorInfoDisplay.style.color = '#555';
        factorInfoDisplay.style.display = 'block'; // Hogy új sorba kerüljön
        if (emissionFactorSelect.nextSibling) {
            emissionFactorSelect.parentNode.insertBefore(factorInfoDisplay, emissionFactorSelect.nextSibling);
        } else {
            emissionFactorSelect.parentNode.appendChild(factorInfoDisplay);
        }
    }

    // Az error span törlésére szolgáló függvény megmaradhat, ha máshol hasznos
    function clearError(input) {
        if (input && input.parentNode) {
            const span = input.parentNode.querySelector('.input-error-message');
            if (span) span.textContent = '';
        }
    }

    async function fetchAndSetEmissionFactor() {
        if (!activityTypeSelect || !unitSelect || !periodYearSelect || !emissionFactorSelect) {
            if (factorInfoDisplay) factorInfoDisplay.textContent = 'Űrlap elem hiba a JS-ben a faktor kereséséhez.';
            return;
        }

        const activityTypeId = activityTypeSelect.value;
        const unit = unitSelect.value;
        const periodYear = periodYearSelect.value;

        if (factorInfoDisplay) factorInfoDisplay.textContent = 'Faktor keresése...';
        emissionFactorSelect.value = ""; // Üresre állítjuk a legördülőt (a "----" opciót választja ki)
        // clearError(emissionFactorSelect); // Erre már nincs szükség itt, mert a calculateAndUpdate-ből jött a hiba

        if (activityTypeId && unit && periodYear) {
            const url = `/co2calculator/ajax/get-emission-factor/?activity_type_id=<span class="math-inline">\{encodeURIComponent\(activityTypeId\)\}&unit\=</span>{encodeURIComponent(unit)}&period_year=${encodeURIComponent(periodYear)}`;

            try {
                const response = await fetch(url);
                const data = await response.json();
                console.log('AJAX response data for factor select:', data);

                if (!response.ok) {
                    console.error('Hiba a faktor lekérdezésekor (szerver válasz):', response.status, data.error);
                    if (factorInfoDisplay) factorInfoDisplay.textContent = data.error || `Faktor keresése sikertelen (${response.status}).`;
                    return;
                }

                if (data.factor_id) {
                    emissionFactorSelect.value = data.factor_id; 
                    if (emissionFactorSelect.value === String(data.factor_id)) {
                        console.log('Option successfully selected in dropdown for factor_id:', data.factor_id);
                        if (factorInfoDisplay) {
                             factorInfoDisplay.textContent = `Automatikus faktor javaslat: ${parseFloat(data.factor_value).toFixed(6)} <span class="math-inline">\{data\.emission\_unit\_numerator\}/</span>{data.unit_of_activity} (Forrás: ${data.factor_source || 'N/A'}, Év: ${data.factor_year || 'N/A'}). Mentéskor ez kerül felhasználásra, ha nem választasz mást.`;
                        }
                    } else {
                        console.warn('Failed to select option in dropdown for auto-factor. Factor ID from AJAX:', data.factor_id, 'Dropdown current value:', emissionFactorSelect.value);
                        if (factorInfoDisplay) factorInfoDisplay.textContent = 'Automatikus faktor talált, de nem sikerült kiválasztani. Válasszon manuálisan, vagy hagyja üresen.';
                    }
                } else {
                    emissionFactorSelect.value = ""; 
                    if (factorInfoDisplay) factorInfoDisplay.textContent = 'Nincs automatikus faktor találat. Válasszon egy faktort a listából, vagy hagyja üresen, és a rendszer mentéskor próbál keresni (ha tud).';
                    console.log('No factor_id returned, dropdown set to empty.');
                }
            } catch (error) {
                console.error('Hiba az AJAX kérés során (faktor keresés):', error);
                if (factorInfoDisplay) factorInfoDisplay.textContent = 'Hiba a faktor lekérdezése közben (klienshiba).';
            }
        } else {
            if (factorInfoDisplay) factorInfoDisplay.textContent = 'Kérjük, adja meg a Tevékenység Típusát, Mértékegységet és Évet a javasolt faktor kereséséhez.';
        }
    }

    // Eseményfigyelők az automatikus faktor kiválasztáshoz
    if (activityTypeSelect) activityTypeSelect.addEventListener('change', fetchAndSetEmissionFactor);
    if (unitSelect) unitSelect.addEventListener('change', fetchAndSetEmissionFactor);
    if (periodYearSelect) periodYearSelect.addEventListener('change', fetchAndSetEmissionFactor);

    // A calculateAndUpdate függvény és a Számítás gomb létrehozása TELJESEN ELTÁVOLÍTVA
});