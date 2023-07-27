let hours = 0;
let minutes = 0;
let seconds = 0;
let dots = 0;
let timer;

// Get required HTML Elements:
const loadingSymbol = document.getElementById('loading-symbol');
const checkCircle = document.getElementById('check-circle');

const statusDisplay = document.getElementById('status-display');
const timerDisplay = document.getElementById('timer-display');


/**
 * Start timer and display loading symbol.
 */
function startStatusUpdate() {
  dots = 1;
  statusDisplay.style = "width: 14ch;";
  timer = setInterval(incrementTimer, 1000);

  checkCircle.classList.add('d-none');
  loadingSymbol.classList.remove('d-none');
}


/**
 * Reset and start status update again.
 */
function restartStatusUpdate() {
  resetStatusUpdate();
  startStatusUpdate();
}


/**
 * Stop timer and display check circle.
 */
function stopStatusUpdate() {
  clearInterval(timer);
  dots = 0;

  statusDisplay.textContent = "Fertig!";
  statusDisplay.style = "width: 7ch;";

  loadingSymbol.classList.add('d-none');
  checkCircle.classList.remove('d-none');
}


/**
 * Reset timer and remove any displayed icons.
 */
function resetStatusUpdate() {
  hours = 0;
  minutes = 0;
  seconds = 0;
  updateDisplay();

  loadingSymbol.classList.add('d-none');
  checkCircle.classList.add('d-none');
}


/**
 * Stop status update and clear displayed content.
 */
function clearStatus() {
  stopStatusUpdate();
  timerDisplay.innerHTML = "";
  statusDisplay.innerHTML = "";
  checkCircle.classList.add('d-none');
}


/**
 * Increment time and update timer display.
 */
function incrementTimer() {
  seconds++;
  if (seconds >= 60) {
    seconds = 0;
    minutes++;
    if (minutes >= 60) {
      minutes = 0;
      hours++;
    }
  }
  updateDisplay();
}


/**
 * Update timer diplay.
 */
function updateDisplay() {
  // Format time:
  let formattedHours = formatTime(hours);
  let formattedMinutes = formatTime(minutes);
  let formattedSeconds = formatTime(seconds);
  
  // Update displayed text:
  statusDisplay.textContent = 'Erstelle Datei' + '.'.repeat(dots);

  // Update displayed time:
  if (hours > 0) {
    timerDisplay.textContent = '(' + formattedHours + ':' + formattedMinutes + ':' + formattedSeconds + ')';
  } else {
    timerDisplay.textContent = '(' + formattedMinutes + ':' + formattedSeconds + ')';
  }

  // Update number of dots to be displayed next time:
  if (dots >= 3) {
    dots = 0;
  } else {
    dots++;
  }
}


/**
 * Add a zero at the front if time is single-digit.
 * @param {Number} time The time number.
 * @returns The double-digit time string.
 */
function formatTime(time) {
  return time < 10 ? '0' + time : time;
}