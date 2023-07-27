// Get the globally required HTML elements:
const modal = new bootstrap.Modal(document.getElementById('modal'));
const modalLabel = document.getElementById('modal-label');
const modalBody = document.getElementById('modal-body');

const submitButton = document.getElementById('submit-button');

const downloadButton = document.getElementById('download-button');
const downloadIcon = document.getElementById('download-icon');

const editButton = document.getElementById('edit-button');
const editIcon = document.getElementById('edit-icon');

let isValidInput = false;

// Check hash to show buttons if history back:
displayButtons(window.location.hash);


/**
 * Check if the user input is valid and update the loading status and buttons.
 * 
 * @return True if input is valid, false if not
 */
function checkInput() {
  const file = document.getElementById('file-input').files[0];
  const youtubeUrl = document.getElementById("youtube-input").value;

  const outputFormat = document.getElementById('output-format-dropdown').value;
  const activeTab = document.getElementsByClassName("tab-pane my-3 active")[0].id;

  const regex = /^((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube\.com|youtu.be))(\/(?:[\w\-]+\?v=|embed\/|v\/)?)([\w\-]+)(\S+)?$/;

  // Check if input is valid:
  if (activeTab == "file-tab" && file && file.type.startsWith('audio/') && (outputFormat === "mp4" || outputFormat === "mkv")) {
    displayModalContent("Information", "Es wurde keine Video-Datei ausgewählt.");
    return false;

  } else if (activeTab == "file-tab" && !file) {
    displayModalContent("Information", "Es wurde keine Datei ausgewählt.");
    return false;

  } else if (activeTab == "url-tab" && !regex.test(youtubeUrl)) {
    displayModalContent("Information", "Es wurde kein gültiger YouTube-Link eingefügt.");
    return false;

  } else {
    // Handle loading status and buttons:
    restartStatusUpdate();
    submitButton.setAttribute('disabled', 'disabled');

    downloadButton.classList.add('d-none');
    downloadIcon.classList.add('d-none');

    editButton.classList.add('d-none');
    editIcon.classList.add('d-none');

    isValidInput = true;
    return true;
  }
}


/**
 * Display the modal with a given content.
 * 
 * @param {String} labelContent The Content of the modal header.
 * @param {String} bodyContent The Content of the modal body.
 */
function displayModalContent(labelContent, bodyContent) {
  modalLabel.innerHTML = labelContent;
  modalBody.innerHTML = bodyContent;
  modal.show();
}


/**
 * Restore buttons and status display with information of hash.
 * @param {String} hash Hash of the url.
 */
function displayButtons(hash) {
  if (hash.includes("show-buttons")) {
    const params = hash.split("&");
    hours = parseInt(params[1]);
    minutes = parseInt(params[2]);
    seconds = parseInt(params[3]);
    updateDisplay();
    stopStatusUpdate();
    
    downloadButton.classList.remove('d-none');
    downloadIcon.classList.remove('d-none');

    editButton.classList.remove('d-none');
    editIcon.classList.remove('d-none');
  }
}


const form = document.querySelector('form');
// Event listener to control submit event.
form.addEventListener('submit', evt => {
  if (isValidInput) {
    // Prepare http request:
    evt.preventDefault();

    const activeTab = document.getElementsByClassName("tab-pane my-3 active")[0].id;
    const formData = new FormData(evt.target);
    const xhr = new XMLHttpRequest();

    formData.append("json", JSON.stringify({ "active_tab": activeTab }));
  
    xhr.open('POST', "/submit");
    xhr.onload = function () {
      if (xhr.status === 200) {
        // Handle loading status and buttons:
        stopStatusUpdate();
        submitButton.removeAttribute('disabled');
        
        downloadButton.classList.remove('d-none');
        downloadIcon.classList.remove('d-none');

        editButton.classList.remove('d-none');
        editIcon.classList.remove('d-none');

        // Set hash to ensure history back shows buttons:
        history.pushState(null, null, '#show-buttons&' + hours+ '&' + minutes + '&' + seconds);

        // Display message in modal:
        const response = JSON.parse(xhr.responseText);
        const message = response.message;
        if (message != 'success') {
          displayModalContent("Information", message);
        }
      }
      else if (xhr.status === 500) {
        clearStatus();
        submitButton.removeAttribute('disabled');

        // Display error message in modal:
        const response = JSON.parse(xhr.responseText);
        const message = response.message;
        displayModalContent("Server-Fehler", message);
      }
    };
    xhr.send(formData);
    isValidInput = false;
  }
});