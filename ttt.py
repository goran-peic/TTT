from flask import Flask, flash, render_template, request, redirect, url_for
import pandas as pd
import numpy as np

app = Flask(__name__)
app.config["SECRET_KEY"] = "ITSASECRET"

df = pd.DataFrame(index=range(3), columns=range(3))
colNames = ['A', 'B', 'C']
df.columns = colNames
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
    return render_template("index.html", df=df, colNames=colNames, player=player)

@app.route("/<int:player>", methods=["GET"])
def index2(player):
  if checkGameOver(df) is False:
    return render_template("index.html", df=df, colNames=colNames, player=player)
  else:
    winMsg = checkWinner(df)
    return render_template("index.html", df=df, colNames=colNames, player=player, winMsg=winMsg)

@app.route("/redir", methods=["POST"])
def redir():
  info = request.form["info"]
  player = int(info[1]); row = int(info[4]); col = colNames[int(info[7])]
  if checkWinner(df): flash("Game Over! Please reset the board.")
  else:
    if pd.isnull(df.ix[row, col]):
      df.ix[row, col] = player
      if player == 1: player = 0
      else: player = 1
    elif df.ix[row, col] == 0: flash("Player O has already occupied that square!")
    else: flash("Player X has already occupied that square!")
  return redirect(url_for("index2", player=player))

@app.route("/reset", methods=["GET", "POST"])
def reset():
  for row in range(len(df.index)):
    for col in colNames:
      df.ix[row, col] = np.nan
  player = 1
  return redirect(url_for("index"))

if __name__ == "__main__":
  app.run(debug=True)