import {Game} from "./4connect.js";
let game;

function showMessage(messasge) {
  window.setTimeout(() => window.alert(message), 5);
}

function listenMessages(websocket) {
  websocket.addEventListener("message", ({ data }) => {
    const event = JSON.parse(data);
    switch (event.type) {
      case "init":
        game = new Game(event.turn, event.color, websocket);
        document.querySelector("body").classList = [game.turn+"-bg"];
        document.getElementById("turn").textContent = (game.turn == game.color) ? "Your Turn!" : game.turn+"'s Turn!";
        localStorage.setItem("game_id", event.game_id);
        localStorage.setItem("secret", event.secret);
        if (event.connected) {
          game.connect(event.connected);
        }
        break;
      case "play":
        game.play(event.color, event.col);
        break;
      case "board":
        localStorage.setItem("game_id", event.game_id);
        localStorage.setItem("secret", event.secret);
        game = new Game(event.turn, event.color, websocket);
        game.turn = event.turn;
        game.set_board(event.board);
        if (event.connected) {
          game.connect(event.connected);
        }
        if (event.winner != "") {
          setTimeout(()=> {
            let res_elm = document.createElement("div");
            res_elm.id = "result";
            let winner = (event.winner != "draw") ? event.winner.toUpperCase()+"<br>Wins!" : "Draw!";
            res_elm.innerHTML = '<div><h1 class="'+event.winner+'">'+winner+'</h1><button id="newgame">New Game</button></div>'
            document.querySelector("body").appendChild(res_elm);
            document.getElementById("newgame").addEventListener("click", newgame);
          });
        }
        break;
      case "result":
        if (event.connected) {
          game.connect(event.connected);
        }
        setTimeout(()=> {
          let res_elm = document.createElement("div");
          res_elm.id = "result";
          res_elm.innerHTML = '<div><h1 class="'+event.winner+'">'+((event.winner != "draw") ? event.winner.toUpperCase()+"<br>Wins!" : "Draw!")+'</h1><button id="newgame">New Game</button></div>'
          document.querySelector("body").appendChild(res_elm);
          document.getElementById("newgame").addEventListener("click", newgame);
        }, 1000);
        break;
      case "error":
        if (event.message == "invalid secret.") {
          localStorage.removeItem("game_id");
          localStorage.removeItem("secret");
        }
        break;
      default:
        throw new Error(`Unsupported event type: ${event.type}.`);
    }
  });
}

function newgame() {
  try {
    document.getElementById("result").remove();
  } catch {
    console.log('.......');
  };
  localStorage.removeItem("game_id");
  localStorage.removeItem("secret");
  let websocket = new WebSocket("ws://"+window.location.hostname+":8001/");
  websocket.addEventListener("open", () => {
      let event = {
          type: "init", 
      };
      websocket.send(JSON.stringify(event));
  });
  listenMessages(websocket);
}

window.addEventListener("DOMContentLoaded", () => {
    let websocket = new WebSocket("ws://"+window.location.hostname+":8001/");
    websocket.addEventListener("open", () => {
        let event = {
            type: "init", 
        };
        if (localStorage.getItem("game_id") != null && localStorage.getItem("game_id") != "") {
            event.game_id = localStorage.getItem("game_id");
            event.secret = localStorage.getItem("secret");
        }
        websocket.send(JSON.stringify(event));
    });
    listenMessages(websocket);
});