let showAnswers = true;

function showHideAnswers() {
	showAnswers = !showAnswers;
	const el = document.getElementById('showhideanswersbox');
	if (showAnswers) {
		el.innerHTML = "With Answers";
	} else {
		el.innerHTML = "Without Answers";
	}
	let answers = document.getElementsByClassName('question_solution');
	let length = answers.length;
	let element = null;

	for (let i = 0; i < length; i++) {
		element = answers[i];
		if (showAnswers) {
			element.style.display = "block";
		} else {
			element.style.display = "none";
		}
	}
}

function setupAnswerBoxes(cls = "question_answer_box") {
	let aboxes = document.getElementsByClassName(cls);
	let length = aboxes.length;

	for (let i = 0; i < length; i++) {
		let box = aboxes[i];

		let container = document.createElement("div");
		container.setAttribute("class", "question_answer_box_container");
		container.setAttribute("id", (i + 1) + "_question_answer_box_container");

		let nBox = box.cloneNode(true);

		let submitButton = document.createElement("button");
		submitButton.setAttribute("class", "question_answer_box_submit");
		submitButton.setAttribute("id", (i + 1) + "_question_answer_box_submit");
		submitButton.innerHTML = "Submit";

		if (submitButton.addEventListener)
			submitButton.addEventListener("click",
				function () { submitFunction() },
				false);

		container.appendChild(nBox);
		container.appendChild(submitButton);

		box.parentNode.replaceChild(container, box);
	}
}

function setupAnswerEditors(cls = "question_answer_box") {
	let aboxes = document.getElementsByClassName(cls);
	let length = aboxes.length;

	for (let i = 0; i < length; i++) {
		let box = aboxes[i];
		//hint = box.innerHTML

		let toolbarOptions = ['bold', 'italic', 'underline', 'strike', 'image', 'link'];
		let options = {
			debug: 'log',
			modules: {
				toolbar: toolbarOptions
			},
			placeholder: "Show your work here ...",
			readOnly: false,
			theme: 'snow'
		};

		let edBox = document.createElement('div');
		edBox.setAttribute("id", "question_editor_box" + i );
		edBox.setAttribute("class", "question_editor_box" );
		box.appendChild(edBox);

		//let container = document.createElement('div');
		//container.setAttribute("id", "container_editor_" + i );
		//container.setAttribute("class", "container_editor" );
		//box.appendChild(container);

		const editor = new Quill(edBox, options);
		//box.appendChild(toolbar);

		// let inpBox = document.createElement('textarea');
		// inpBox.innerHTML = hint;
		console.log("created quill editor and container for question " + i);
		//box.parentNode.replaceChild(box, container);
	}
}

let client = null;
let webhookClient = null;

function setupDiscord() {
	client = new Discord.Client();
	const token = document.getElementById("discord-token").innerText.trim();
	const url = document.getElementById("discord-url").innerText.trim();

	webhookClient = new Discord.WebhookClient(url, token);
}

function setupExam() {
	showHideAnswers();
	setupAnswerBoxes();
	setupAnswerEditors();
	setupDiscord();
}

function submitFunction(event) {
	event = event || window.event; // IE
	let target = event.target || event.srcElement; // IE
	let tid = target.id;

	q = target.parentNode;

	const nameField = document.getElementById("nameField");
	const studentIdField = document.getElementById("studentIdField");

	if ((nameField !== null) && (studentIdField !== null)) {
		const name = nameField.value;
		const studentId = studentIdField.value;

		console.log("log" + name + "," + studentId);

		if ((name !== "") && (studentId !== "")) {
			//alert("Submitted" + name + "," + studentId + ":" + q.id + q.innerText );
			console.log(q.innerHTML);

			const title = "Q_" + q.id + ":" + name + ":" + studentId;
			// const enc = new TextEncoder("utf-8");
			// const buf = enc.encode(q.outerHTML).buffer;
			var submission = `
				Name: ${name}
				StudentId: ${studentId}
				Question: ${q.id}
			`

			let edBoxes = document.getElementsByClassName( "question_editor_box" );
			let length = edBoxes.length;

			for (let i = 0; i < length; i++) {
				let box = edBoxes[i];
				submission = submission + "\n" + "<h1>" + "<p>" + "Question " + (i+1) + "</h1>" + "\n";
				let qab = box.parentNode;
				submission = submission + "<h2>" + "*** Inputs" + "</h2>" + "\n";
				let qinputs = qab.getElementsByTagName( "input");
				// The last element is the quill editor input field
				for( let j = 0; j < qinputs.length - 1; j++ ) {
					let inText = "\n" + qinputs[j].value + "\n";
					submission = submission + `Input ${j}=${inText}` + "\n";
				}
				submission = submission + "<h2>" + "*** End of Inputs" + "</h2>"+ "\n";
				submission = submission + "<h2>" + "*** Editor" + "</h2>" + "\n";
				submission = submission + box.innerHTML;
				submission = submission + "<h2>" + "*** End of Editor" + "</h2>" + "\n";
				submission = submission + "\n" + "<h1>" + "End of Question" + (i+1) + "</h1>" + "\n";
			}

			let blob = new Blob([ submission ], { type: "text/html" });

			// let file = new File([blob], "Q_" + q.id + ".html", { type: "text/html" });
			// console.log("file " + file);W

			// let url = URL.createObjectURL(file);
			// console.log("url " + url);
			let content = new Discord.MessageAttachment( blob, studentId + "_submit" + q.id + ".html", { "data": q.innerHTML} );
			//let content = new Discord.MessageAttachment( blob.stream(), "Q_" + q.id + ".html" );
			//let content = new Discord.MessageAttachment( blob.stream() , "Q_" + q.id + ".html");
			//console.log("content", content);

			webhookClient.send( name + ":" + studentId + ":" + "question_" + q.id, content)
				.then(message => alert(`Question ${q.id} submitted`) )
				.catch(console.error);

			// let fr = new FileReader();
			// fr.onload = function(evt){
			//     //evt.target.result + "<br><a href="+URL.createObjectURL(file)+" download=" + file.name + ">Download " + file.name + "</a><br>type: "+file.type+"<br>last modified: "+ file.lastModifiedDate
			//     webhookClient.send('Webhook test', {
			//         username: 'Examination Bot',
			//         files: [ url ],
			//     })
			//     .then( message => alert( `Question ${q.id} submitted`))
			//     .catch(console.error);
			// }
			// fr.readAsText( file );

			// console.log("Stream" + stream );
			// const readable = ReadableStream.from( [ q.outerHTML ] );
			// // let embed = new Discord.MessageEmbed()
			//     .setTitle(title)
			//     .attachFiles( [ content ] )
			//     .setColor('#0099ff');
			//     // .addField("answer", q.innerHTML ); # must be 1024 or less in length


		} else {
			alert("Missing Name and/or Student ID");
		}
	}
}

let CLIPBOARD = new CLIPBOARD_CLASS("my_canvas", true);

/**
 * image pasting into canvas
 * 
 * @param {string} canvas_id - canvas id
 * @param {boolean} autoresize - if canvas will be resized
 */
function CLIPBOARD_CLASS(canvas_id, autoresize) {
	const _self = this;
	const canvas = document.getElementById(canvas_id);
	const ctx = document.getElementById(canvas_id).getContext("2d");

	//handlers
	document.addEventListener('paste', function (e) { _self.paste_auto(e); }, false);

	//on paste
	this.paste_auto = function (e) {
		if (e.clipboardData) {
			let items = e.clipboardData.items;
			if (!items) return;

			//access data directly
			let is_image = false;
			for (let i = 0; i < items.length; i++) {
				if (items[i].type.indexOf("image") !== -1) {
					//image
					let blob = items[i].getAsFile();
					let URLObj = window.URL || window.webkitURL;
					let source = URLObj.createObjectURL(blob);
					let.paste_createImage(source);
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
		let pastedImage = new Image();
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
