// The ordered sequence of keys:
const sequence = { 'index': 'Index', 'start': 'Start', 'end': 'Ende', 'speaker': 'Sprecher:in', 'text': 'Text', 'color': 'Farbe', 'size': 'Schriftgröße', 'align': 'Ausrichtung' };
const options = ['Alle'];


/**
 * Manage the table creation.
 * @param {Object} jsonData The json data for building the table.
 */
function buildTable(jsonData) {
    const table = document.getElementById('table');

    // Get sorted keys:
    const keys = Object.keys(sequence);
    let sortedKeys = Object.keys(jsonData[0]).sort(function (a, b) {
        return keys.indexOf(a) - keys.indexOf(b);
    });

    // Generate table:
    generateTableHead(table, sortedKeys);
    generateTableBody(table, sortedKeys, jsonData);
}


/**
 * Generate the table head.
 * @param {HTMLElement} table The html table element.
 * @param {String[]} sortedKeys The order of the table columns.
 */
function generateTableHead(table, sortedKeys) {
    const tableHead = table.tHead;
    const row = tableHead.insertRow();

    // Create master checkbox:
    let th = document.createElement("th");
    const checkbox = document.createElement("input");

    checkbox.type = 'checkbox';
    checkbox.id = 'master-checkbox';
    checkbox.setAttribute("onchange", "toggleCheckboxes(this)");
    checkbox.classList.add("form-check-input");

    th.appendChild(checkbox);
    row.appendChild(th);

    // Create table header:
    for (const key of sortedKeys) {
        th = document.createElement("th");
        const text = document.createTextNode(sequence[key]);

        th.style = "text-align: center;";
        th.appendChild(text);
        row.appendChild(th);
    }
}


/**
 * Generate the table body.
 * @param {HTMLElement} table The html table element.
 * @param {String[]} sortedKeys The order of the table columns.
 * @param {Object} data The json data containing table row information.
 */
function generateTableBody(table, sortedKeys, data) {
    const tableBody = table.getElementsByTagName('tbody')[0];

    // Loop through json rows:
    for (const i in data) {
        const element = data[i];
        const row = tableBody.insertRow();
        createCheckboxCell(row);

        // Create table cells for json row:
        for (const key of sortedKeys) {
            switch (key) {
                case "index":
                    createIndexCell(row, element[key], i);
                    break;
                case "start":
                case "end":
                    const pattern = getPattern(element[key]);
                    createTimestampCell(row, element[key], key, i, pattern);
                    break;
                case "speaker":
                    createSpeakerCell(row, element[key], i);
                    if (!options.includes(element[key])) { options.push(element[key]); }
                    break;
                case "text":
                    createTextCell(row, element[key], i);
                    break;
                case "color":
                    createColorCell(row, element[key], i);
                    break;
                case "size":
                    createSizeCell(row, element[key], i);
                    break;
                case "align":
                    createAlignCell(row, element[key], i);
                    break;
            }
        }
    }
    // Handle checkbox dropdown:
    createDropdown(options);
    if (options.length === 1) {
        dropdown.classList.add("d-none");
        document.getElementById("checkbox-info").classList.add("d-none");
    }
}


const dropdown = document.getElementById("checkbox-dropdown");
/**
 * Create checkbox dropdown.
 * @param {String[]} options The checkbox dropdown options.
 */
function createDropdown(options) {
    dropdown.replaceChildren();
    for (const value of options) {
        const option = document.createElement("option");
        option.innerHTML = value;
        dropdown.appendChild(option);
    }
}


/**
 * Create a table cell that contains a checkbox.
 * @param {HTMLTableRowElement} row The html table row element.
 */
function createCheckboxCell(row) {
    const cell = row.insertCell();
    cell.classList.add("align-middle");
    const checkbox = document.createElement("input");

    // Set attributes:
    checkbox.type = 'checkbox';
    checkbox.id = 'checkbox-' + (row.rowIndex - 1);
    checkbox.classList.add("form-check-input", "sub-checkbox");

    cell.appendChild(checkbox);
}


/**
 * Create a table cell that contains an input field.
 * @param {HTMLTableRowElement} row The html table row element.
 * @param {String} value The value of the input field.
 * @returns The created input field.
 */
function createCell(row, value) {
    const cell = row.insertCell();
    const input = document.createElement("input");

    // Set attributes:
    input.type = 'text';
    input.setAttribute("value", value);
    input.placeholder = value;
    input.setAttribute("oninput", "updateValues(this)");

    cell.appendChild(input);

    return input;
}



/**
 * Create a table cell of the type "index".
 * @param {HTMLTableRowElement} row The html table row element.
 * @param {String} value The value of the input field.
 * @param {Number} i The row index.
 */
function createIndexCell(row, value, i) {
    const input = createCell(row, value);

    // Set custom attributes:
    input.classList.add("form-control", "index-column");
    input.name = 'index-' + i;
    input.setAttribute('disabled', 'disabled');
}


/**
 * Create a table cell of the type "timestamp".
 * @param {HTMLTableRowElement} row The html table row element.
 * @param {String} value The value of the input field.
 * @param {Number} i The row index.
 * @param {String} pattern The pattern of the input field.
 */
function createTimestampCell(row, value, key, i, pattern) {
    const input = createCell(row, value);

    // Set custom attributes:
    input.classList.add("form-control", "time-column");
    input.name = key + '-' + i;
    input.pattern = pattern;
    input.setAttribute('required', 'required');
}


/**
 * Create a table cell of the type "speaker".
 * @param {HTMLTableRowElement} row The html table row element.
 * @param {String} value The value of the input field.
 * @param {Number} i The row index.
 */
function createSpeakerCell(row, value, i) {
    const input = createCell(row, value);

    // Set custom attributes:
    input.classList.add("form-control", "speaker-column");
    input.name = 'speaker-' + i;
    input.setAttribute("onchange", "updateSpeakerOptions()");
}


/**
 * Create a table cell of the type "text".
 * @param {HTMLTableRowElement} row The html table row element.
 * @param {String} value The value of the input field.
 * @param {Number} i The row index.
 */
function createTextCell(row, value, i) {
    const input = createCell(row, value);

    // Set custom attributes:
    input.classList.add("form-control", "text-column");
    input.name = 'text-' + i;
}


/**
 * Create a table cell of the type "color".
 * @param {HTMLTableRowElement} row The html table row element.
 * @param {String} value The value of the input field.
 * @param {Number} i The row index.
 */
function createColorCell(row, value, i) {
    const input = createCell(row, value);

    // Set custom attributes:
    input.type = 'color';
    input.classList.add("form-control", "form-control-color");
    input.name = "color-" + i;
    input.setAttribute('required', 'required');
}


/**
 * Create a table cell of the type "size".
 * @param {HTMLTableRowElement} row The html table row element.
 * @param {String} value The value of the input field.
 * @param {Number} i The row index.
 */
function createSizeCell(row, value, i) {
    const input = createCell(row, value);

    // Set custom attributes:
    input.type = 'number';
    input.classList.add("form-control", "size-column");
    input.name = "size-" + i;
    input.min = 10;
    input.max = 100;
    input.setAttribute('required', 'required');
}


/**
 * Create a table cell of the type "align".
 * @param {HTMLTableRowElement} row The html table row element.
 * @param {String} value The selected value of the dropdown.
 * @param {Number} i The row index.
 */
function createAlignCell(row, value, i) {
    const cell = row.insertCell();
    const select = document.createElement("select");

    // Set attributes:
    select.classList.add("form-select");
    select.name = "align-" + i;
    select.setAttribute("onchange", "updateValues(this)")

    // Add options to dropdown:
    const aligns = { "2": "unten", "5": "mittig", "8": "oben" };
    for (const key in aligns) {
        const option = document.createElement("option");
        option.textContent = aligns[key];
        option.value = key;

        // Set selected value:
        if (key === value) {
            option.setAttribute('selected', 'selected');
        }
        select.appendChild(option);
    }

    cell.appendChild(select);
}


/**
 * Find out the timestamp format and create pattern attribute value.
 * @param {String} timestamp The given timestamp.
 * @returns A html pattern string for the given timestamp.
 */
function getPattern(timestamp) {
    return timestamp.replace(/\d+/g, function (match) { return "\\d{" + match.length + "}"; }).replace(".", "\\.");
}


/**
 * Toggle checkboxes depending on dropdown select.
 * @param {HTMLElement} masterCheckbox The master checkbox.
 */
function toggleCheckboxes(masterCheckbox) {
    const subCheckboxes = document.getElementsByClassName("sub-checkbox");

    // Loop through rows:
    for (const subCheckbox of subCheckboxes) {
        const rowIndex = subCheckbox.parentElement.parentElement.rowIndex;
        const input = document.getElementsByName("speaker-" + (rowIndex - 1))[0];

        // Update checkbox:
        if (dropdown.value === "Alle" || dropdown.value === input.value.trim()) {
            subCheckbox.checked = masterCheckbox.checked;
        }
    }
}


/**
 * Update input filed values depending on selected rows.
 * @param {HTMLInputElement} thisInput The current input field.
 */
function updateValues(thisInput) {
    const thisCheckbox = document.getElementById("checkbox-" + thisInput.name.split("-")[1]);

    if (thisCheckbox.checked) {
        const otherInputs = document.querySelectorAll(thisInput.tagName + '[name^=' + thisInput.name.split("-")[0] + ']');

        // Loop through all other input fields and update value if checkbox is also checked:
        for (const otherInput of otherInputs) {
            const otherCheckbox = document.getElementById("checkbox-" + otherInput.name.split("-")[1]);

            if (otherInput !== thisInput && otherCheckbox.checked) {
                otherInput.value = thisInput.value;
            }
        }
    }
}


/**
 * Update the options of dropdown if a speaker was renamed.
 */
function updateSpeakerOptions() {
    const options = ['Alle'];
    const speakerInputs = document.querySelectorAll("input[name^=speaker]");

    for (const input of speakerInputs) {
        if (!options.includes(input.value)) {
            options.push(input.value);
        }
    }
    createDropdown(options);
}


const modal = new bootstrap.Modal(document.getElementById('modal'));
const modalLabel = document.getElementById('modal-label');
const modalBody = document.getElementById('modal-body');
/**
 * Display button-specific content in modal.
 * @param {Boolean} reset Whether it is the reset button or the cancel button.
 */
function displayModal(reset) {
    const button = document.getElementById('okay-button');
    if (reset) {
        modalLabel.innerHTML = "Zurücksetzen";
        modalBody.innerHTML = "Alle Felder werden zurückgesetzt. Fortfahren?";
        button.setAttribute("onclick", "reset()");
    } else {
        modalLabel.innerHTML = "Abbrechen";
        modalBody.innerHTML = "Alle Eingaben werden verworfen. Fortfahren?";
        button.setAttribute("onclick", "cancel()");
    }
    modal.show();
}

function cancel() {
    history.back();
}

function reset() {
    form.reset();
    createDropdown(options);
}


const form = document.querySelector('form');
// Event listener to control submit event.
form.addEventListener('submit', evt => {
    evt.preventDefault();

    if (form.checkValidity()) {
        restartStatusUpdate();
        document.getElementById('submit-button').setAttribute('disabled', 'disabled');

        // Prepare http request:
        const formData = new FormData(evt.target);
        const xhr = new XMLHttpRequest();

        xhr.onload = function () {
            if (xhr.status === 200) {
                history.back();
                stopStatusUpdate();
            }
        }
        xhr.open('POST', "/save");
        xhr.send(formData);
    }
});