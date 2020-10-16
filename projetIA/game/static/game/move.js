window.onload = function() {
    document.getElementById("bdown").addEventListener("click", () => {
        main([1,0]); //l'axe X et l'axe Y sont inversés car génération de table selon un tableau à 2d
    });
    document.getElementById("bleft").addEventListener("click", () => {
      main([0,-1]);
    });
    document.getElementById("bright").addEventListener("click", () => {
        main([0,1]);
    });
    document.getElementById("bup").addEventListener("click", () => {
      main([-1,0]);
    });

    let pos = [[0,0], [7,7]]
    this.initBoard(pos);
}
async function main(movement) {
    const response = await jsonRPC("/game/move", {game_id: "1", player_id: "42", move: movement});
    console.log(response);
    let pos = [];
    for(player of response.players){
      pos[pos.length] = player.position;
    }
    updateBoard(response.board, pos);
}

function initBoard(pos){
  let basicBoard = [[1,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,2]];

  this.updateBoard(basicBoard, pos);
}

function updateBoard(boardContent, pos){

  let table = document.querySelector("table");
  table.textContent="";
  generateTable(table, boardContent, pos);
}

function generateTable(table, data, pos) {
  for (let element of data) {
    let row = table.insertRow();
    for (key in element) {
      let cell = row.insertCell();

      if(element[key] == 1){
        cell.className = "couleur1"
      }
      else if (element[key] == 2){
        cell.className = "couleur2"
      }
      else{
        cell.className="couleur3"
      }  
    }
  }
  for (let position in pos){

    let posX = pos[position][0]
    let posY = pos[position][1]
    let ligne1 = table.getElementsByTagName('tr')[posX];
    let cell1 = ligne1.getElementsByTagName('td')[posY];

    cell1.textContent= "J"+position 
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