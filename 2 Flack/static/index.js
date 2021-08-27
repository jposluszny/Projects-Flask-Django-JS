document.addEventListener('DOMContentLoaded', () => {
  //Set starting value of message displayed for new users
  if (localStorage.getItem('info')){
    var info = localStorage.getItem('info');
    }
  else {
    localStorage.setItem('info', 'Enter a name.');
    }

  //Ask for user's name
  if (!localStorage.getItem('name')){
    var name = prompt(localStorage.getItem('info'));
    if (!name){
        localStorage.setItem('info', 'You must enter a name.')
        location.reload();
    }
    else if (name.length < 1){
        localStorage.setItem('info', 'You must enter a name.')
        location.reload();
        }
    else {
        localStorage.setItem('name', name);

        // Open new request to check if name exists.
        var request1 = new XMLHttpRequest();
        request1.open('POST', '/name');
        request1.onload = () => {
          const data1 = JSON.parse(request1.responseText);
          name = localStorage.getItem('name');
          if (data1 === name){
            localStorage.setItem('name', name);
            location.reload();
            }
          else {
            localStorage.setItem('info', data1)
            localStorage.removeItem('name');
            location.reload();
            }
          }

        // Add  name to request data.
        const data_name = new FormData();
        data_name.append('name', name);

        // Send request.
        request1.send(data_name);
        }
      }

  // Get name, set channel and load posts
  var name = localStorage.getItem('name');
  if (localStorage.getItem('current_channel')){
    document.querySelector('#channels').value = localStorage.getItem('current_channel');
    load_posts();
    }

  // Connect to channel
  var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);

  socket.on('connect', (new_channel) => {
    // Submit new channel's name
   document.querySelector('#create').onclick = () => {
     // Get ew channel name
     var new_channel = document.querySelector('#new_channel').value;

     if (new_channel.length < 1){
       document.querySelector('#info').innerHTML = 'You must enter a name!';
     }
     else {

     // Open new request to check if channel exists.
     var request2 = new XMLHttpRequest();
     request2.open('POST', '/channel');

     // Add  name to request data.
     var data_channel = new FormData();
     data_channel.append('new_channel', new_channel);

     // Send request.
     request2.send(data_channel);

     request2.onload = () => {
       const data2 = JSON.parse(request2.responseText);
       // if response ok emit message that channel can be created
       if (data2 === 'ok'){
          socket.emit('create new channel', {'new_channel': new_channel});
       }
       // Else display message
       else {
          document.querySelector('#info').innerHTML = data2;
       }
     }
    }
   }
      // Add new channel
      socket.on('announce new channel', data => {
            const option = document.createElement('option');
            option.innerHTML = data.new_channel;
            document.querySelector('#channels').append(option);
            document.querySelector('#info').innerHTML = 'Channel has been created.';
      });
});

  // Change channel
  document.querySelector('#channels').onchange = load_posts;

  // Emit post
  socket.on('connect', () => {
    document.querySelector('#post').onclick = () => {
    on_channel = document.querySelector('#channels').value;
    const post = `${name} --> ${document.querySelector('#message').value} `;
    socket.emit('submit post', {'post': post, 'on_channel': on_channel});
    }
  });

  // When a new post is announced, add to the channel
  socket.on('announce post', data => {

    // Add only when the right channel is set
    if (document.querySelector('#channels').value === data.on_channel){
      add_post(data.post);
     }
  });

  // Leave channel
  document.querySelector('#leave_channel').onclick = () => {
    document.querySelector('#channels').value = "Choose channel";
    load_posts();
    }

  // Leave chat
  document.querySelector('#leave_chat').onclick = () => {
    localStorage.removeItem('name');
    localStorage.removeItem('info');
    localStorage.setItem('current_channel', "Choose channel");
    location.reload();
    }
  });

function load_posts() {
  var current_channel = document.querySelector('#channels').value;
  localStorage.setItem('current_channel', current_channel);
  if (current_channel === 'Choose channel'){
    document.querySelector('#info').innerHTML = 'Choose channel';
  }
  else{
    document.querySelector('#info').innerHTML = `Welcome on ${current_channel}.`;
  }

  // Clear posts of old channel
  var list = document.querySelector('#posts');
  while (list.hasChildNodes()) {
    list.removeChild(list.firstChild);
  }

  // Open new request to get new posts.
  var request = new XMLHttpRequest();
  request.open('POST', '/posts');
  request.onload = () => {
    const data = JSON.parse(request.responseText);
    if (data)
    {
      data.forEach(add_post);
    }

  }

  // Add channel's name to request data.
  const data = new FormData();
  data.append('current_channel', current_channel);

  // Send request.
  request.send(data);
  }

function add_post(contents) {
  // Create new post.
  const post = document.createElement('div');
  post.className = 'post';
  post.innerHTML = contents;

  // Add button to remove post.
  var user_name = localStorage.getItem('name');
  var author_name = contents.slice(0, user_name.length);
  if (user_name === author_name){
    const hide = document.createElement('button');
    hide.className = 'hide';
    hide.innerHTML = 'Hide';
    post.append(hide);

    // When hide button is clicked, hide post in your window.
    hide.onclick = function() {
      this.parentElement.remove();
      }
    }

  // Add post to DOM.
  document.querySelector('#posts').append(post);
};
