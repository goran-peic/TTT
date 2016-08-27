from flask import Flask, flash, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import numpy as np

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgres://vbxtfqewruqsyd:Iq6hT2zJUXwc065E58bPQ3beBt@ec2-54-235-126-62.compute-1.amazonaws.com:5432/dfj6qs4gm5hmp5"
app.config["SECRET_KEY"] = "ITSASECRET"
db = SQLAlchemy(app)

class GameTable(db.Model):

  __tablename__ = "game"

  id = db.Column(db.Integer, primary_key=True)
  A = db.Column(db.Integer, unique=False, nullable=True)
  B = db.Column(db.Integer, unique=False, nullable=True)
  C = db.Column(db.Integer, unique=False, nullable=True)

  def __init__(self, A, B, C):
    self.A = A
    self.B = B
    self.C = C

db.create_all()

def resetBoard():
  for id in range(1, 4):
    updateTable = GameTable.query.filter_by(id=id).first()
    updateTable.A = None; updateTable.B = None; updateTable.C = None
    db.session.commit()

dframe = pd.DataFrame.from_records([rec.__dict__ for rec in GameTable.query.all()])

if dframe.empty:
  row1 = GameTable(None, None, None); row2 = GameTable(None, None, None); row3 = GameTable(None, None, None)
  db.session.add(row1); db.session.commit()
  db.session.add(row2); db.session.commit()
  db.session.add(row3); db.session.commit()
else:
  resetBoard()

del dframe

player = 1
colNames = ['A', 'B', 'C']

def getDF():
  dframe = pd.DataFrame.from_records([rec.__dict__ for rec in GameTable.query.order_by(GameTable.id).all()])
  dframe = dframe.drop(["_sa_instance_state", "id"], axis=1)
  dframe = dframe.apply(lambda x: pd.to_numeric(x), axis=0)
  dframe = dframe.fillna(value=np.nan)
  dframe.columns = colNames
  return dframe

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
  dframe = getDF()
  return render_template("index.html", dframe=dframe, colNames=colNames, player=player)

@app.route("/<int:player>", methods=["GET"])
def index2(player):
  dframe = getDF()
  if checkGameOver(dframe) is False:
    return render_template("index.html", dframe=dframe, colNames=colNames, player=player)
  else:
    winMsg = checkWinner(dframe)
    return render_template("index.html", dframe=dframe, colNames=colNames, player=player, winMsg=winMsg)

@app.route("/redir", methods=["POST"])
def redir():
  dframe = getDF()
  info = request.form["info"]
  player = int(info[1]); row = int(info[4]); col = colNames[int(info[7])]
  if checkWinner(dframe): flash("Game Over! Please reset the board.")
  else:
    if pd.isnull(dframe.ix[row, col]):
      updateTable = GameTable.query.filter_by(id=1+row).first()
      if col == 'A':
        updateTable.A = player
        db.session.commit()
      elif col == 'B':
        updateTable.B = player
        db.session.commit()
      elif col == 'C':
        updateTable.C = player
        db.session.commit()
      if player == 1: player = 0
      else: player = 1
    elif dframe.ix[row, col] == 0: flash("Player O has already occupied that square!")
    else: flash("Player X has already occupied that square!")
  return redirect(url_for("index2", player=player))

@app.route("/reset", methods=["GET", "POST"])
def reset():
  resetBoard()
  return redirect(url_for("index"))

if __name__ == "__main__":
  db.create_all()
  app.run(debug=True)