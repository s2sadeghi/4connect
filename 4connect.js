export class Game {
    constructor(turn, color, websocket) {
        this.board = [
            [],
            [],
            [],
            [],
            [],
            [],
            []
        ];
        this.turn = turn;
        this.color = color;
        this.socket = websocket;
        this.board_elm = document.getElementById("board");
        this.board_elm.querySelectorAll("piece").forEach(elm => {elm.remove()});
        this.board_elm.querySelectorAll("div.line").forEach(elm => {elm.remove()});
        document.querySelectorAll("#board .col").forEach(col => {
            col.addEventListener("click", event => {
                this.sendMove(event.target.id[3]);
            });
        });
    }
    set_board(board) {
        this.board = board;
        for (let row = 0; row < board.length; row++){
            for (let col = 0; col < board[row].length; col++){
                let piece = document.createElement("piece");
                piece.classList.add(board[row][col] == 0 ? "red" : "blue");
                piece.style.transform = "translate("+row*100+"%, -"+100*col+"%"+")";
                this.board_elm.appendChild(piece);
            }
        }
        document.querySelector("body").classList = [this.turn+"-bg"];
        document.getElementById("turn").textContent = (this.turn == this.color) ? "Your Turn!" : this.turn+"'s Turn!";
    }
    play(color, col) {
        let row = this.board[col].length;
        this.board[col].push((color == "red") ? 0 : 1)
        let piece = document.createElement("piece");
        piece.classList.add(color);
        piece.style.transform = "translate("+col*100+"%, -"+610+"%"+")";
        this.board_elm.appendChild(piece);
        setTimeout(() => {
            piece.style.transform = "translate("+col*100+"%, -"+100*row+"%"+")";
        }, 250);
        this.turn = (this.turn == "red") ? "blue" : "red";
        document.querySelector("body").classList = [this.turn+"-bg"];
        document.getElementById("turn").textContent = (this.turn == this.color) ? "Your Turn!" : this.turn+"'s Turn!";
    }
    sendMove(col) {
        const event = {
            type: "play",
            color: this.color,
            col: col,
        };
        this.socket.send(JSON.stringify(event));
    }
    connect(data) {
        let row = data[0];
        let col = data[1];
        let typ = data[2];
        let line = document.createElement("div");
        if (typ == "row") {
            line.classList = ["line"];
            line.style.transform = 'translate('+(row*25)+'%, -'+(col*100)+'%)';
        } else if (typ == "col") {
            line.classList = ["line"];
            line.style.transform = 'translate('+(row*25-37.5)+'%, -'+(col*100+150)+'%) rotate(90deg)';
        } else if (typ == "inc") {
            line.classList = ["line inc"];
            line.style.transform = 'translate('+row*25+'%, -'+(col*100+150)+'%) rotate(-45deg)';
        } else if (typ == "dec") {
            line.classList = ["line dec"];
            line.style.transform = 'translate('+row*25+'%, '+(-col*100+150)+'%) rotate(45deg)';
        }
        this.board_elm.appendChild(line);
    }
}