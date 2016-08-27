from flask import Flask, flash, render_template, request, redirect, url_for
import pandas as pd
import numpy as np

app = Flask(__name__)
app.config["SECRET_KEY"] = "ITSASECRET"

dframe = pd.DataFrame(index=range(3), columns=range(3))
colNames = ['A', 'B', 'C']
dframe.columns = colNames
player = 1

def sumOfDiagonal(dframe, align):
  colNamesTemp = colNames[:]
  tempSum = 0
  if align == "left":
    for i in range(3): tempSum += dframe.ix[i, colNames[i]]
    return(tempSum)
  else:
    colNamesTemp.reverse()
    for i in range(3): tempSum += dframe.ix[i, colNamesTemp[i]]
    return(tempSum)

def checkWinner(dframe):
  if any(dframe.sum(axis=0, skipna=False) == 3) or any(dframe.sum(axis=1, skipna=False) == 3) or sumOfDiagonal(dframe, "left") == 3 or sumOfDiagonal(dframe, "right") == 3:
    temp = "Player X Won!"
    return temp
  elif any(dframe.sum(axis=0, skipna=False) == 0) or any(dframe.sum(axis=1, skipna=False) == 0) or sumOfDiagonal(dframe, "left") == 0 or sumOfDiagonal(dframe, "right") == 0:
    temp = "Player O Won!"
    return temp
  else:
    return None

def checkGameOver(dframe):
  if checkWinner(dframe) is not None: return True
  else: return False

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", dframe=dframe, colNames=colNames, player=player)

@app.route("/<int:player>", methods=["GET"])
def index2(player):
  print("#####")
  print(dframe)
  print("#####")
  if checkGameOver(dframe) is False:
    return render_template("index.html", dframe=dframe, colNames=colNames, player=player)
  else:
    winMsg = checkWinner(dframe)
    return render_template("index.html", dframe=dframe, colNames=colNames, player=player, winMsg=winMsg)

@app.route("/redir", methods=["POST"])
def redir():
  info = request.form["info"]
  player = int(info[1]); row = int(info[4]); col = colNames[int(info[7])]
  if checkWinner(dframe): flash("Game Over! Please reset the board.")
  else:
    if pd.isnull(dframe.ix[row, col]):
      dframe.ix[row, col] = player
      if player == 1: player = 0
      else: player = 1
    elif dframe.ix[row, col] == 0: flash("Player O has already occupied that square!")
    else: flash("Player X has already occupied that square!")
  return redirect(url_for("index2", player=player))

@app.route("/reset", methods=["GET", "POST"])
def reset():
  for row in range(len(dframe.index)):
    for col in colNames:
      dframe.ix[row, col] = np.nan
  player = 1
  return redirect(url_for("index"))

if __name__ == "__main__":
  app.run()