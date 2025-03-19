let optionAlphabets = ['A', 'B', 'C', 'D', 'E', 'F', 'G'];

const executeUpdate = () => {

};

$('#nextButtton').click(function() {
  let questIndex = document.querySelector("#Quest_number").textContent;
  let questList = questIndex.split(' ')
  questIndex = questList[1] - 1
  let selectedOpt = $('input[name="opt"]:checked').val();
  // var isBtnCreated = false;
  $.ajax({
    url: '/load_questions',
    type: 'GET',
    data: {quest_index: questIndex, selected_opt:selectedOpt},
    success: function(response) {
      if (response.question){
        // console.log(response.question)
        questIndex ++;
        var questNum = questIndex +1;
        let quest = response.question[0];
        $('#Question').text(quest);
        let options = response.question[1];

        let index = 0;

        options.forEach(option => {
          let optionId = '#inputOption' + String(index + 1);
          $(optionId).val(option).next('label').text('[' + optionAlphabets[index] + ']  ' + option);
          index ++;
          console.log(option)
        });

        var displayNumber = options.length;
        console.log(displayNumber)
        i = 0;
        document.querySelectorAll('.quiz-option').forEach((option) => {
          i ++
          if( i <= displayNumber){
            option.style.display = 'block';
          }
          else{
            option.style.display = 'none';
          }
        })

        $('#Quest_number').text(`Question ${questNum}`)
        $('#Quest_inst').text(response.question[4])

        $('input[type=radio]').prop('name="opt"');

        $('input[type=radio]').each(function() {
          if ($(this).val() == response.show_selected) {
            $(this).prop('checked', true)
          }else{
            $(this).prop('checked', false)
          }
        })

        if (questNum >= 2) {
          $('#previousButtton').show();
        }
        if (questNum === response.number_of_quest ){
          $('#nextButtton').hide();
        }
          
      } else if(questNum < 2){
        $('#Question').text(response.message);
      }
      MathJax.typeset();
    }
  });
})


$('#previousButtton').click(function () {
  let questIndex = document.querySelector("#Quest_number").textContent;
  let questList = questIndex.split(' ')
  questIndex = questList[1] - 1
  let selectedOpt = $('input[name="opt"]:checked').val();
  $.ajax({
    url: '/load_pquestions',
    type: 'GET',
    data: {quest_index: questIndex, selected_opt: selectedOpt},
    success: function(response) {
      if (response.question){
        console.log(response.show_selected)
        questIndex --;
        var questNum = questIndex + 1;
        $('#Question').text(response.question[0]);
        let options = response.question[1];
        
        index = 0;
        options.forEach(option => {
          optionId = '#inputOption' + String(index + 1)
          $(optionId).val(option).next('label').text('[' + optionAlphabets[index] + ']  ' + option);
          index ++
        });

        var displayNumber = options.length;
        console.log(displayNumber)
        i = 0;
        document.querySelectorAll('.quiz-option').forEach((option) => {
          i ++
          if( i <= displayNumber){
            option.style.display = 'block';
          }
          else{
            option.style.display = 'none';
          }
        })

        $('#Quest_number').text(`Question ${questNum}`)
        $('#Quest_inst').text(response.question[4])

        $('input[type=radio]').each(function() {
          if ($(this).val() == response.show_selected) {
            $(this).prop('checked', true)
          }else{
            $(this).prop('checked', false)
          }
        })

        if (questNum === 1) {
          $('#previousButtton').hide();
          $('#nextButtton').show();
        }
        if (questNum < response.number_of_quest){
          $('#nextButtton').show();
        }
        MathJax.typeset();
      }
    }
  })
})

let emptList = []
function remQuest() {
  let capturedTime = document.getElementById('timer').innerText;
  let questIndex = document.querySelector("#Quest_number").textContent;
  let questList = questIndex.split(' ')
  questIndex = questList[1] - 1
  
  // console.log(questIndex);
  let selectedOpt = $('input[name="opt"]:checked').val();
  $.ajax({
    url: "/remaining_questions",
    type: "GET",
    data: {"rem_quest": "remaining", selected_opt:selectedOpt, question_index: questIndex, captured_time: capturedTime},
    success: function (response) {
      var remaining = response.remQuest
      questIndex = String(questIndex + 1)
      let clickedBtn = $("#"+ questIndex + "btn")
      clickedBtn.addClass("greenClass")
      
      if (remaining > 0){
        $('#remQuest').text(`REMAINING QUESTIONS: ${remaining}`)
      }else if (remaining == 0) {
        $('#remQuest').text(`ALL QUESTIONS ANSWERED`)
      }
    }
  })
}

// let captured_time = ''
window.addEventListener('beforeunload', function (event) {
  let captured_time = document.getElementById('timer').innerText;
  let username = $(".userImage").attr("data-username");
  let questionNumber = document.querySelector("#Quest_number").innerText;
  $.ajax({
    url:"/cbt_session",
    type:"POST",
    data:{leave_time: captured_time, username: username, question_number: questionNumber}
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
    success: function(response){
      window.location.href = "/";
      localStorage.clear();
    }
  })
}

function reveal() {
  $.ajax({
    url: "/submit",
    type: "POST",
    success: function(response) {
      console.log(response)
      $(".confirm-box").show();
      $("#confirm-p").text(response.confirm);
      document.querySelector(".generalDiv").style.opacity = 0.1;
      document.querySelector(".confirm-box").style.opacity = 1;
    }
  })
}

$(function(){
  let btnClass = $(".nav-btn");
  btnClass.on("click", function(){
    let btnNumber = $(this).attr("data-number")
    $.ajax({
      url: "/random_navigation",
      type: "GET",
      success: function(response){
        let question = response.user_questions[btnNumber]
        console.log(question)

        $('#Question').text(question[0]);
        let options = question[1];
        
        index = 0;
        options.forEach(option => {
          optionId = '#inputOption' + String(index + 1)
          $(optionId).val(option).next('label').text('[' + optionAlphabets[index] + ']  ' + option);
          index ++
        });

        var displayNumber = options.length;
        console.log(displayNumber)
        i = 0;
        document.querySelectorAll('.quiz-option').forEach((option) => {
          i ++
          if( i <= displayNumber){
            option.style.display = 'block';
          }
          else{
            option.style.display = 'none';
          }
        })

        $('#Quest_number').text(`Question ${Number(btnNumber) + 1}`)
        $('#Quest_inst').text(question[4])

        $('input[type=radio]').prop('name="opt"');
        let show_selected = question[3]
        $('input[type=radio]').each(function() {
          if ($(this).val() == show_selected) {
            $(this).prop('checked', true)
          }else{
            $(this).prop('checked', false)
          }
        })

        let questNum = Number(btnNumber) + 1
        if (questNum >= 2) {
          $('#previousButtton').show();
        }
        if (questNum === response.user_questions.length) {
          $('#nextButtton').hide();
        }

        if (questNum === 1) {
          $('#previousButtton').hide();
          $('#nextButtton').show();
        }
        if (questNum < response.user_questions.length){
          $('#nextButtton').show();
        }
        MathJax.typeset();
      }
    })
  })
})