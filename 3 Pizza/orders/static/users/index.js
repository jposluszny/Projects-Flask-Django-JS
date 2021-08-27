document.addEventListener('DOMContentLoaded', () => {

  //Add item to cart when user clicks add
  document.querySelectorAll('.Dishes').forEach(function(item) {
    item.onclick = create_item;
  });

  //Add item to cart when user clicks add
  document.querySelectorAll('.Toppings').forEach(item =>  {
    item.onclick = create_item;
  });

   //Add item to cart from last session when user comes back
   var userName = document.querySelector('#userName').innerText;
   var userOrderList = userName + 'OrderList';

   // Add items to cart
   if (localStorage.getItem(userOrderList)){
    var list = JSON.parse(localStorage.getItem(userOrderList));

    for (const e of list){
    for (const i of document.querySelectorAll('.' + e[0])) {
      if (i.dataset.pk === e[1]){
        i.click();
          }
        }
      }
    }

    // Send order to server
    document.querySelector('#placeOrder').onclick = function(){
      // Count toppings and add message if client can order more
      var message = '';
      var x = countToppings();
      if (x > 0){
        message += 'You can order ' + x + ' more toppings. ';
      }

      var l = document.getElementsByTagName('li');
      // Check if client ordered steak's additions without steak
      for (i of l){
        if (i.innerText[0] === '+') {
          var flag = false;
          for (e of l){
            if (e.dataset.name.includes('Sub Steak + Cheese') ){
              flag = true;
              break;
            }
          }
        }
      }
        if (flag === false){
              message += 'You are trying to order steak\'s additions without steak. ';
              flag = true;
          }

      // Check if client ordered extra cheese without sub
      for (i of l){
        if (i.innerText.includes('Extra Cheese on any sub')) {
          var flag = false;
          for (e of l){
            if (e.dataset.name.slice(0, 3) === 'Sub' ){
              flag = true;
              break;
            }
          }
        }
      }
      if (flag === false){
            message += 'You are trying to order extra cheese without sub. ';
        }
      if (message != ''){
        message += 'Do you want to place the order anyway\?'
      }
      else{
         message += 'Do you really want to place the order?';
      }

      // Ask for order confirmation
      if (confirm(message)) {
              // Create new request to place order
              const request = new XMLHttpRequest();
              request.open('POST', '/cart');

              // Callback function for when request completes
              request.onload = () => {

                  // Read message from request
                 const data = request.responseText;

                  // Update the result div
                  if (data) {
                    document.querySelector('#info1').innerHTML = data;

                    // Clear cart if order placed successfully
                    if (data === "Your order has been placed."){
                        var list = document.querySelector('#order');
                        while (list.hasChildNodes()) {
                          list.removeChild(list.firstChild);
                          document.querySelector('#total').innerHTML = '0.00';

                          // Remove user's order list from local storage
                          var userName = document.querySelector('#userName').innerText;
                          var userOrderList = userName + 'OrderList';
                          localStorage.removeItem(userOrderList);
                        }
                    }
                  }
                  else {
                      document.querySelector('#info1').innerHTML = 'There was an error.';
                  }
              }

              // Send data to server to place order
              var userName = document.querySelector('#userName').innerText;
              var userOrderList = userName + 'OrderList';

              // Get organized data from local storage
              if (localStorage.getItem(userOrderList)){
                var orderList = localStorage.getItem(userOrderList);
              }

              // If nothing in the cart try to send empty list
              else {
                var orderList = JSON.stringify([]);
              }

              // Add data to send with request
              const data = new FormData();
              data.append('order', orderList);

              // Add a csrf-token to the request headers so that Django accepts the request
              var csrftoken = Cookies.get("csrftoken");
              request.setRequestHeader("X-CSRFToken", csrftoken);

              // Send data
              request.send(data);
              return false;
        }

      // Without confirmation don't do anything
      else {
        return false;
      }
    }
    });
  // Create item of cart with attributes and remove link
  function create_item() {
      var numOfToppings = parseInt(localStorage.getItem('numOfToppings'));
      numOfToppings += parseInt(this.dataset.toppings);

      localStorage.setItem('numOfToppings', numOfToppings);

      // Get value of order
      let total = parseFloat(document.querySelector('#total').innerHTML);

      // Add pizza's price to order
      total +=  parseFloat(this.dataset.price);

      // Display  sum of order
      document.querySelector('#total').innerHTML = total.toFixed(2);

      // Add attributes to order's items
      const li = document.createElement('li');
      li.innerHTML = this.dataset.name + ' ' +  this.dataset.price + ' $' ;
      li.setAttribute('data-type', this.dataset.type);
      li.setAttribute('data-pk', this.dataset.pk);
      li.setAttribute('data-toppings', this.dataset.toppings);
      li.setAttribute('data-name', this.dataset.name);

      // Add link to remove pizza from order.
      const remove = document.createElement('a');
      remove.innerHTML = ' <a href=""> del</a>';
      remove.value = this.dataset.price;

      // When remove button is clicked remove item and update total price
      remove.onclick = function() {
        let total = parseFloat(document.querySelector('#total').innerHTML);
        total -=  parseFloat(this.value);
        this.parentElement.remove();

        // Count number of toppings and remove it when necessary
        var x = countToppings();
        if (x < 0){
          while (x < 0){
            for (j of document.getElementsByTagName('li')){
              if (j.dataset.type === 'Toppings'){
                j.remove();
                x++;
                break;
              }
            }
          }
        }
        document.querySelector('#info1').innerHTML = '';
        document.querySelector('#total').innerHTML = total.toFixed(2);

        // Update orderlist
        createOrderList() ;
        return false;
        }

      // Append button to list
      li.append(remove);

      // Add item to cart if toppings and extra items are allowed
      var x = countToppings();
      if (this.dataset.type === 'Dishes'){
        document.querySelector('#order').append(li);
        document.querySelector('#info1').innerHTML = '';
        }
      else {
        if (x > 0){
          document.querySelector('#order').append(li);
          }
        else {
          document.querySelector('#info1').innerHTML = "You can't order toppings without pizza.";
          }
        }

      // Update orderlist
      createOrderList() ;
      return false;
                }

// Create order list and save to local storage
function createOrderList (){
  var userName = document.querySelector('#userName').innerText;
  var orderList = [];
  for (i of document.getElementsByTagName('li')){
    // If in the cart is special pizza add additionaly it's name
    if ((i.dataset.name === 'Special small') || (i.dataset.name === 'Special large')){
      orderList.push([i.dataset.type, i.dataset.pk, i.dataset.name]);
    }
    else {
      orderList.push([i.dataset.type, i.dataset.pk]);
    }
  }
  var userOrderList = userName + 'OrderList';
  localStorage.setItem(userOrderList, JSON.stringify(orderList));
}

function countToppings(){
  var x = 0;
  for (i of document.getElementsByTagName('li')){
    x += parseInt(i.dataset.toppings);
    }
  return x;
}
