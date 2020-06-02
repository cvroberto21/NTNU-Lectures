var showAnswers = true;

function showHideAnswers() {
	showAnswers = !showAnswers;
	el = document.getElementById('showhideanswersbox');
	if (showAnswers) {
		el.innerHTML = "With Answers";
	} else {
		el.innerHTML = "Without Answers";
	}
	var answers = document.getElementsByClassName('question_solution');
	var length = answers.length;
	var element = null;

	for (var i = 0; i < length; i++) {
		element = answers[i];
		if (showAnswers) {
			element.style.display = "block";
		} else {
			element.style.display = "none";
		}
	}
}

function setupAnswerBoxes(cls = "question_answer_box") {
	var aboxes = document.getElementsByClassName(cls);
	var length = aboxes.length;

	for (var i = 0; i < length; i++) {
		var box = aboxes[i];

        var container = document.createElement("div");
        container.setAttribute("class", "question_answer_box_container");
        container.setAttribute("id", ( i + 1 ) + "_question_answer_box_container" );

        var nBox = box.cloneNode( true );

		var submitButton = document.createElement("button");
        submitButton.setAttribute("class", "question_answer_box_submit");
        submitButton.setAttribute("id", (i + 1) + "_question_answer_box_submit" );
        submitButton.innerHTML = "Submit";
        
        if (submitButton.addEventListener)
            submitButton.addEventListener("click", 
                function() { submitFunction( ) }, 
                false );

        container.appendChild( nBox );
        container.appendChild( submitButton );

		box.parentNode.replaceChild( container, box );
	}
}

function setupAnswerEditors(cls = "answer_editor") {
	var aboxes = document.getElementsByClassName(cls);
	var length = aboxes.length;

	for (var i = 0; i < length; i++) {
		var box = aboxes[i];
        hint = box.innerHTML
        var toolbarOptions = ['bold', 'italic', 'underline', 'strike', 'image', 'link'];
		var options = {
			debug: 'log',
			modules: {
			  toolbar: toolbarOptions
			},
			placeholder: "Enter your answer here ...",
			readOnly: false,
			theme: 'snow'
        };

        // var toolbar = document.createElement('div');
        // toolbar.setAttribute("id", "editor_toolbar_" + i );
        // toolbar.setAttribute("class", "editor_toolbar" );
        // box.append(toolbar);

		//var container = document.createElement('div');
		//container.setAttribute("id", "container_editor_" + i );
		//container.setAttribute("class", "container_editor" );
		//box.appendChild(container);
		
        var editor = new Quill(box, options );
		//box.appendChild(toolbar);
		
		// var inpBox = document.createElement('textarea');
		// inpBox.innerHTML = hint;
		console.log("created quill editor and container for question " + i);
		//box.parentNode.replaceChild(box, container);
	}
}

function setupExam() {
	showHideAnswers();
    setupAnswerBoxes();
	setupAnswerEditors();
}

function submitFunction( event ) {
    event = event || window.event; // IE
    var target = event.target || event.srcElement; // IE
    var tid = target.id;

    q = target.parentNode;

    alert("Submitted" + q.id + q.innerText );
}
