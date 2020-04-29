var showAnswers = true;

function showHideAnswers( ) {
    showAnswers = ! showAnswers;
    el = document.getElementById('showhideanswersbox');
    if ( showAnswers ) {
       el.innerHTML = "With Answers";
    } else {
       el.innerHTML = "Without Answers";
    }
    var answers = document.getElementsByClassName('question_solution');
    var length = answers.length;
    var element = null;
    for (var i = 0; i < length; i++) {
       element = answers[i];
       if ( showAnswers ) {
          element.style.display = "block";
       } else {
          element.style.display = "none";
       }
    }
 }

 function setupExam() {
    showHideAnswers()
 }
