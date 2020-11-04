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
    this.updateBoard(board, pos);
}
async function main(movement) {
  const response = await jsonRPC("/game/move", {game_id: game_id, player_id: curr_player, move: movement});
  let pos = [];
  for(player of response.players){
    pos[pos.length] = player.position;
  }
  updateBoard(response.board, pos);
  curr_player = changePlayer(curr_player, response.players);
  printPlayerToPlay(response.players, curr_player);
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

    cell1.textContent= "P"+position 
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

function changePlayer(curr_player, players){
  for (let player of players){
    if(player.id == curr_player){
      indice = players.indexOf(player);
      if(indice == players.length-1){
        return players[0].id;
      }
      else{
        return players[indice+1].id;
      }
    }
  }
}

function printPlayerToPlay(players, indice){
  console.log("test")
  for(let player of players){
    if(player.id == indice){
      document.getElementById("player_to_play").textContent= "P"+players.indexOf(player)+" to play";
    }
  }
}