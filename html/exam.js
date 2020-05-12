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
		hint = box.innerHTML
		var inpBox = document.createElement('textarea');
		inpBox.innerHTML = hint;
		box.parentNode.replaceChild(box, inpBox);
	}
}

function setupAnswerEditors(cls = "answer_editor") {
	var aboxes = document.getElementsByClassName(cls);
	var length = aboxes.length;

	for (var i = 0; i < length; i++) {
		var box = aboxes[i];
		hint = box.innerHTML
		var options = {
			debug: 'info',
			modules: {
			  toolbar: '#editor_toolbar_' + i
			},
			placeholder: "Enter your answer here ...",
			readOnly: false,
			//theme: 'snow'
		  };
		var container = document.createElement('div');
		container.setAttribute("id", "container_editor_" + i );
		container.setAttribute("class", "container_editor" );
		
		var toolbar = document.createElement('div');
		toolbar.setAttribute("id", "editor_toolbar" + i );
		toolbar.setAttribute("class", "editor_toolbar" );
		
		var editor = new Quill(box, options);
		editor.setAttribute("id", "editor_" + i);
		editor.setAttribute("class", "editor" + i);
		
		container.appendChild(toolbar);
		container.appendChild(editor);
		
		// var inpBox = document.createElement('textarea');
		// inpBox.innerHTML = hint;
		console.log("created quill editor and container for question " + i);
		box.parentNode.replaceChild(box, container);
	}
}



function setupExam() {
	showHideAnswers();
	setupAnswerEditors();
}

var CLIPBOARD = new CLIPBOARD_CLASS("my_canvas", true);

/**
 * image pasting into canvas
 * 
 * @param {string} canvas_id - canvas id
 * @param {boolean} autoresize - if canvas will be resized
 */
function CLIPBOARD_CLASS(canvas_id, autoresize) {
	var _self = this;
	var canvas = document.getElementById(canvas_id);
	var ctx = document.getElementById(canvas_id).getContext("2d");

	//handlers
	document.addEventListener('paste', function (e) { _self.paste_auto(e); }, false);

	//on paste
	this.paste_auto = function (e) {
		if (e.clipboardData) {
			var items = e.clipboardData.items;
			if (!items) return;

			//access data directly
			var is_image = false;
			for (var i = 0; i < items.length; i++) {
				if (items[i].type.indexOf("image") !== -1) {
					//image
					var blob = items[i].getAsFile();
					var URLObj = window.URL || window.webkitURL;
					var source = URLObj.createObjectURL(blob);
					this.paste_createImage(source);
					is_image = true;
				}
			}
			if (is_image == true) {
				e.preventDefault();
			}
		}
	};
	//draw pasted image to canvas
	this.paste_createImage = function (source) {
		var pastedImage = new Image();
		pastedImage.onload = function () {
			if (autoresize == true) {
				//resize
				canvas.width = pastedImage.width;
				canvas.height = pastedImage.height;
			}
			else {
				//clear canvas
				ctx.clearRect(0, 0, canvas.width, canvas.height);
			}
			ctx.drawImage(pastedImage, 0, 0);
		};
		pastedImage.src = source;
	};
}