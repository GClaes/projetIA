window.onload = function() {
    document.getElementById("my_button").addEventListener("click", () => {
        main();
    });
    this.initBoard();
}
async function main() {
    const response = await jsonRPC("/game/move", {game_id: "1", player_id: "42", move: [1, 0]});
    let board = document.getElementById("board");
    updateBoard(response.board, board);
}

function initBoard(){
  let basicBoard = [[3,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,4]];
  this.updateBoard(basicBoard, document.getElementById("board"));
}

function updateBoard(boardContent, board){
  let table = document.querySelector("table");
  table.textContent="";
  generateTable(table, boardContent);
}

function generateTable(table, data) {
  for (let element of data) {
    let row = table.insertRow();
    for (key in element) {
      let cell = row.insertCell();
      let content = document.createTextNode(element[key]);
      
      if(element[key] == 1){
        cell.className = "couleur1"
      }
      else if (element[key] == 2){
        cell.className = "couleur2"
      }
      else if(element[key] == 3){
        cell.className="pos1"
        element[key] = 1
      }
      else if(element[key] == 4){
        cell.className="pos2"
        element[key] = 2
      }
      else{
        cell.className="couleur3"
      }
      
      cell.appendChild(content);
    }
  }
}


function jsonRPC(url, data) {
    return new Promise(function (resolve, reject) {
      let xhr = new XMLHttpRequest();
      xhr.open("POST", url);
      xhr.setRequestHeader("Content-type", "application/json");
      const csrftoken = document.querySelector("[name=csrfmiddlewaretoken]")
        .value;
      xhr.setRequestHeader("X-CSRFToken", csrftoken);
      xhr.onload = function () {
        if (this.status >= 200 && this.status < 300) {
          resolve(JSON.parse(xhr.response));
        } else {
          reject({
            status: this.status,
            statusText: xhr.statusText,
          });
        }
      };
      xhr.onerror = function () {
        reject({
          status: this.status,
          statusText: xhr.statusText,
        });
      };
      xhr.send(JSON.stringify(data));
    });
}