// Countdown timer in JavaScript
function startTimer(duration, display) {
//   let reloadTime = localStorage.getItem("currentTime");

//   if(reloadTime !== null){
//     console.log("I am not empty")
//     let reloadMinutes = Number(reloadTime[0] + reloadTime[1]);
//     let reloadSeconds = Number(reloadTime[3] + reloadTime[4]);

//     let reloadTimer = reloadMinutes * 60 + reloadSeconds

//     var timer = reloadTimer, minutes, seconds;
//   } else{
//     console.log("I am empty")
//   }

	var timer = duration, minutes, seconds;
  var timerInterval = setInterval(function () { // Store the interval in a variable

      minutes = parseInt(timer / 60, 10);
      seconds = parseInt(timer % 60, 10);
      
      minutes = minutes < 10 ? "0" + minutes : minutes;
      seconds = seconds < 10 ? "0" + seconds : seconds;
      
      display.textContent = minutes + ":" + seconds;
    
      if (--timer < 0) {
          // Make an AJAX request when the timer reaches zero
          fetch('/timer_finished', { 
              method: 'POST',
              headers: {
                  'Content-Type': 'application/json'
              }
          }).then(response => {
              if (response.ok) {
                  return response.json();
              } else {
                  throw new Error('Network response was not ok.');
              }
          })
          .then(data => {
              console.log(data.notification);
              var url = document.getElementById('timer').getAttribute('data-url');
              window.location.href = url;
              localStorage.removeItem('currentTime')
          }).catch(error => {
              console.error('There was a problem with the fetch operation: ' + error.message);
          });

          // Clear the interval to stop the timer
          clearInterval(timerInterval);
      }
  }, 1000);
}

// Start the timer
var exam_time = document.getElementById('countWrite').getAttribute('data-url');
var spendingTime = 60 * exam_time, // Time in minutes
display = document.querySelector('#timer');
startTimer(spendingTime, display);