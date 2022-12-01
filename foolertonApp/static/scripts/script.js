function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
          const cookie = cookies[i].trim();
          // Does this cookie string begin with the name we want?
          if (cookie.substring(0, name.length + 1) === (name + '=')) {
              cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
              break;
          }
      }
  }
  return cookieValue;
}
const csrftoken = getCookie('csrftoken');
// Checkbox on task done
// Backend team gotta update the tasks first (whether done or not)

// Sample
var sampleData = [true, false];

// console.log(`Context: \n ${task_complete_status}`);
// console.log(`Context Parsed: \n ${JSON.parse(task_complete_status)}`);


var checkbox = document.getElementsByClassName("task_checkbox");

// Sample updating


for (var i = 0; i < checkbox.length; i++) {
  // Add the onclick function
  checkbox[i].addEventListener("click", function () {
    var checkbox_id = this.id.split("_")[1];
    // This is basically a Promise, a commitment, a tall order. Means I must meet that tall order. And it's for you! 
    fetch("/mark", {
      method: "POST",
      headers: {
        'Content-Type': 'application/json',
        "X-CSRFToken": csrftoken,
      },
      body: JSON.stringify({"task_id": checkbox_id}),
    }).then(res => {
        return res.text();
      })
        .then(data => {
          console.log("Task complete flag updated! Response: ", data);
          this.classList.toggle("task_done");
        });
  });

  // Update the default value like this
  if (task_complete_status[i]) {
    checkbox[i].classList.add("task_done");
  }
}




/// For selection of actions

var calendar_el = document.getElementById("calendar_col");
var add_task_el = document.getElementById("add_task_col");
var update_task_el = document.getElementById("update_task_col");
var delete_task_el = document.getElementById("delete_task_col");
var add_comment_el = document.getElementById("add_comment_col");

var task_create_status_el = document.getElementById("task_create_status");
var task_update_status_el = document.getElementById("task_create_status");
var task_delete_status_el = document.getElementById("task_delete_status");
var comment_create_status_el = document.getElementById("comment_create_status");

// Display the task selected if any
var task_selected_el = document.getElementsByClassName("active")[0];
// var selected_task_description_el = document.getElementById("selected_task_description");
var selected_task_description_lst = document.getElementsByClassName("selected_task_description");
if (task_selected_el != null) {
  for (let element of selected_task_description_lst) {
    element.textContent = task_selected_el.textContent;
  }
}
else {
  for (let element of selected_task_description_lst) {
    element.textContent = "No Task Selected";
  }
}

// Hide what needs to be hidden
// calendar_el.style.display = "none";
add_task_el.style.display = "none";
update_task_el.style.display = "none";
delete_task_el.style.display = "none";
add_comment_el.style.display = "none";


var select_button = document.getElementById("action_select_button");
var select_dropdown = document.getElementById("action_select");

// Add function to task select button
select_button.addEventListener("click", function () {
  if (select_dropdown.value == "0") {
    calendar_el.style.display = "block";
    add_task_el.style.display = "none";
    update_task_el.style.display = "none";
    delete_task_el.style.display = "none";
    add_comment_el.style.display = "none";
  }
  else if (select_dropdown.value == "add_task") {
    task_create_status_el.textContent = "Add Task";
    calendar_el.style.display = "none";
    add_task_el.style.display = "block";
    update_task_el.style.display = "none";
    delete_task_el.style.display = "none";
    add_comment_el.style.display = "none";
  }
  else if (select_dropdown.value == "update_task") {
    task_update_status_el.textContent = "Update Task";
    calendar_el.style.display = "none";
    add_task_el.style.display = "none";
    update_task_el.style.display = "block";
    delete_task_el.style.display = "none";
    add_comment_el.style.display = "none";
  }
  else if (select_dropdown.value == "delete_task") {
    task_delete_status_el.textContent = "Delete Task";
    calendar_el.style.display = "none";
    add_task_el.style.display = "none";
    update_task_el.style.display = "none";
    delete_task_el.style.display = "block";
    add_comment_el.style.display = "none";
  }
  else if (select_dropdown.value == "add_comment") {
    calendar_el.style.display = "none";
    add_task_el.style.display = "none";
    update_task_el.style.display = "none";
    delete_task_el.style.display = "none";
    add_comment_el.style.display = "block";
  }
});

// Add function to create task button
var create_task_button_el = document.getElementById("add_task_button");

create_task_button_el.addEventListener("click", function () {
  // Whatever backend stuff that needs to be done
  var task_description_el = document.getElementById("add_task_description_field");
  var task_time_el = document.getElementById("add_task_time_field");
  var task_date_el = document.getElementById("add_task_date_field");
  
  var task_description = task_description_el.value;
  var task_time = task_time_el.value;
  var task_date = task_date_el.value;

  // console.log(task_description);
  // console.log(task_time);
  // console.log(task_date);

  if (task_description.length > 0) { // backend check condition for successful task creation
    // Change the content of header to task created!
    task_create_status_el.textContent = "Task created!";
  }
  else {
    task_create_status_el.textContent = "Error. Please try again";
  } 

});


// Add function to delete task button
var delete_task_button_el = document.getElementById("delete_task_button");

delete_task_button_el.addEventListener("click", function () {
  // Whatever backend stuff that needs to be done
  var task_selected_el = document.getElementsByClassName("active")[0];
  var task_id = task_selected_el.id.split("_")[1];
  var res_status = 500;

  res_data = fetch("/delete", {
    method: "DELETE",
    headers: {
      'Content-Type': 'application/json',
      "X-CSRFToken": csrftoken,
    },
    body: JSON.stringify({"task_id": task_id}),
  }).then(res => {
      console.log(res.status);
      res_status = res.status;
      return res.text();
  
    }).then(data => {
        console.log(data);
        console.log(`Status: ${res_status}`);
        if (res_status == 200) { // backend check condition for successful task creation
          task_delete_status_el.textContent = "Task deleted!";
          window.location.reload();
        }
        else {
          task_create_status_el.textContent = "Error. Please try again";
        } 
      });
});

// Add function to add comment button
var create_comment_button_el = document.getElementById("add_comment_button");


create_comment_button_el.addEventListener("click", function () {
  // Whatever backend stuff that needs to be done
  var comment_description_el = document.getElementById("add_comment_description_field");
  // Probably would be good to assign an id to each comment when adding it in so we know where to add the comment to

  var comment_description = comment_description_el.value;
  console.log("Button Pressed")

  // console.log(comment_description);

  if (comment_description.length > 0 && document.getElementsByClassName("active").length > 0) { // backend check condition for successful task creation
    // Change the content of header to task created!
    comment_create_status_el.textContent = "Comment created!";
    // Would be good to reload the tasks here too
  }
  else {
    comment_create_status_el.textContent = "Error. Please try again";
  } 

});









/// This part is for the collapsibles

var coll = document.getElementsByClassName("tasklist_collapsible");
var task_comments_el = document.getElementsByClassName("task_comments_container");

function collapseAll() {
  for (var i = 0; i < coll.length; i++) {
    coll[i].classList.remove("active");
  }
  for (var i = 0; i < task_comments_el.length; i++) {
    task_comments_el[i].style.display = "none";
  }

  console.log("Collapse all");
}

for (var i = 0; i < coll.length; i++) {
  coll[i].addEventListener("click", function () {
    // disable all active first
    // var active_els = document.getElementsByClassName("active");
    if (!this.classList.contains("active")) collapseAll();

    this.classList.toggle("active");
    // this.classList.toggle("active");
    // this controls the div that's hidden
    var content = this.nextElementSibling;
    if (content.style.display === "block") {
      content.style.display = "none";
      task_selected_el = null;
      // selected_task_description_el.textContent = "No Task Selected";
      for (let element of selected_task_description_lst) {
        element.textContent = "No Task Selected";
      }
      
    } else {
      content.style.display = "block";
      task_selected_el = this;
      for (let element of selected_task_description_lst) {
        element.textContent = this.textContent;
      }
    }
  });
}