let optionAlphabets = ['A', 'B', 'C', 'D', 'E', 'F', 'G'];

const executeUpdate = (myData, questIndex, btn) => {
  fetch('/navigation',
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: myData,
    })
    .then(resp => resp.json())
    .then(data => {
      // INCREASING THE QUESTION INDEX FOR PASSING TO THE SERVER AND CHECKING ON THE CURRENT BUTTON
      if (btn.value == "Next") {
        questIndex++;
        questNum = questIndex + 1

        console.log(data.number_of_quest);
        console.log(questNum);
        if (questNum >= 2) {
          document.querySelector('#previousButtton').style.display = 'block';
        }
        if (questNum === data.number_of_quest) {

          document.querySelector('#nextButtton').style.display = 'none';
        }
      } else if (btn.value == "Previous") {
        questNum = questIndex
        questIndex--;
        if (questNum === 1) {
          document.querySelector('#previousButtton').style.display = 'none';
          document.querySelector('#nextButtton').style.display = 'block';
        }
        if (questNum < data.number_of_quest) {
          document.querySelector('#nextButtton').style.display = 'block';
        }
      } else {
        let questNum = Number(btn.value)
        if (questNum >= 2) {
          $('#previousButtton').show();
        }
        if (questNum === data.number_of_quest) {
          $('#nextButtton').hide();
        }

        if (questNum === 1) {
          $('#previousButtton').hide();
          $('#nextButtton').show();
        }
        if (questNum < data.number_of_quest) {
          $('#nextButtton').show();
        }
      }

      // UPDATING QUESTIONS
      let quest = data.question[0];
      document.querySelector('#Question').textContent = quest;

      // UPDATING OPTIONS
      let options = data.question[1];
      let index = 0;
      options.forEach(option => {
        let optionId = '#inputOption' + String(index + 1);
        $(optionId).val(option).next('label').text('[' + optionAlphabets[index] + ']  ' + option);
        index++;
      });

      // 
      var displayNumber = options.length;
      console.log(displayNumber)
      i = 0;
      document.querySelectorAll('.quiz-option').forEach((option) => {
        i++
        if (i <= displayNumber) {
          option.style.display = 'block';
        }
        else {
          option.style.display = 'none';
        }
      })

      // UPDATING QUESTION NUMBER AND QUESTION INSTRUCTION
      var questNum = questIndex + 1;
      document.querySelector('#Quest_number').textContent = (`Question ${questNum}`);
      document.querySelector('#Quest_inst').textContent = (data.question[4]);

      document.querySelectorAll('input[type=radio]').forEach(function (option) {
        if (option.value == data.show_selected) {
          option.checked = true;
        } else {
          option.checked = false;
        }
      })

      // CALLING MATHJAX TO UPDATE LATEX FORMATS
      MathJax.typeset();
    })
    .catch(error => console.log(error.message)
    )
};

let btns = document.querySelectorAll('button');

btns.forEach(btn => {
  btn.addEventListener('click', (e) => {
    let questIndex = document.querySelector("#Quest_number").textContent;
    let questList = questIndex.split(' ')
    questIndex = questList[1] - 1
    let selectedOpt;
    try {
      selectedOpt = document.querySelector('input[name="opt"]:checked').value;
      console.log(selectedOpt);
    } catch {
      selectedOpt = document.querySelector('input[name="opt"]:checked');
      console.log(selectedOpt);
    }

    let myData = JSON.stringify({ "quest_index": questIndex, "selected_opt": selectedOpt, currentBtn: btn.value });
    switch (btn.value) {
      case 'Next':
        executeUpdate(myData, questIndex, btn);
        // console.log(questIndex);
        break;
      case 'Previous':
        executeUpdate(myData, questIndex, btn)
        // console.log(questIndex);

        break;

      default:
        questIndex = Number(btn.value - 1);
        // console.log(`Question index is: ${questIndex}`);
        executeUpdate(myData, questIndex, btn)

        break;
    }
  })
})


let emptList = []
function remQuest() {
  let capturedTime = document.getElementById('timer').innerText;
  let questIndex = document.querySelector("#Quest_number").textContent;
  let questList = questIndex.split(' ')
  questIndex = questList[1] - 1

  let selectedOpt = $('input[name="opt"]:checked').val();
  $.ajax({
    url: "/remaining_questions",
    type: "GET",
    data: { "rem_quest": "remaining", selected_opt: selectedOpt, question_index: questIndex, captured_time: capturedTime },
    success: function (response) {
      var remaining = response.remQuest
      questIndex = String(questIndex + 1)
      let clickedBtn = $("#" + questIndex + "btn")
      clickedBtn.addClass("greenClass")

      if (remaining > 0) {
        $('#remQuest').text(`REMAINING QUESTIONS: ${remaining}`)
      } else if (remaining == 0) {
        $('#remQuest').text(`ALL QUESTIONS ANSWERED`)
      }
    }
  })
}

window.addEventListener('beforeunload', function (event) {
  let captured_time = document.getElementById('timer').innerText;
  let username = $(".userImage").attr("data-username");
  let questionNumber = document.querySelector("#Quest_number").innerText;
  $.ajax({
    url: "/cbt_session",
    type: "POST",
    data: { leave_time: captured_time, username: username, question_number: questionNumber }
  });
});

function ok() {
  document.querySelector(".confirm-box").style.display = "none";
  document.querySelector(".generalDiv").style.opacity = 1;
  // location.reload();
}

function confirmSelect() {
  $.ajax({
    url: "/ok_submit",
    type: "POST",
    success: function (response) {
      window.location.href = "/";
      localStorage.clear();
    }
  })
}

function reveal() {
  $.ajax({
    url: "/submit",
    type: "POST",
    success: function (response) {
      console.log(response)
      $(".confirm-box").show();
      $("#confirm-p").text(response.confirm);
      document.querySelector(".generalDiv").style.opacity = 0.1;
      document.querySelector(".confirm-box").style.opacity = 1;
    }
  })
}