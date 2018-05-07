function menuBarToggler() {
  var menuBar = document.getElementById('myTopnav');
  if (menuBar.className === 'topnav') {
    menuBar.className += ' responsive';
  } else {
    menuBar.className = 'topnav';
  }
}

function messageBarHider(number) {
  var messageBar = document.getElementById('message' + number);
  messageBar.style.animation = 'fadeout 0.5s';
  setTimeout(function () { messageBar.style.display = 'none'; }, 500);
}

function gameMenuToggler(id) {
  var gameMenus = document.getElementsByClassName('game-list-menu');
  for (var i = 0; i < gameMenus.length; i++) {
    if (i === id) {
      continue;
    }
    var openMenu = gameMenus[i];
    if (openMenu.classList.contains('game-list-menu-show')) {
      openMenu.classList.remove('game-list-menu-show');
    }
  }
  document.getElementById('gamemenu' + id).classList.toggle('game-list-menu-show');
}