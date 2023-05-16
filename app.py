from flask import Flask, request, jsonify
from settings import handle_exceptions, logger, connection

app = Flask(__name__)


@app.route("/stock/buying", methods=["POST"], endpoint="buy_stocks")
@handle_exceptions
def buy_stocks():
    cur, conn = connection()
    logger(__name__).warning("starting the database connection")
    if "stock_name" and "quantity" and "buying_cost_per_unit" and "selling_cost_per_unit" not in request.json:
        raise Exception("details missing")
    data = request.get_json()
    stock_name = data['stock_name']
    quantity = data['quantity']
    buying_cost_per_unit = data['buying_cost_per_unit']
    selling_cost_per_unit = data['selling_cost_per_unit']
    cur.execute('INSERT INTO stock_data(stock_name,quantity,buying_cost_per_unit,selling_cost_per_unit )''VALUES (%s,%s, %s, %s);',
                (stock_name, quantity, buying_cost_per_unit, selling_cost_per_unit))
    conn.commit()
    logger(__name__).warning("close the database connection")
    return jsonify({"message" : "created sucessfully"})


# all stocks information
@app.route("/stocks/all", methods=["GET"], endpoint="all_stocks")
@handle_exceptions
def all_stocks():
    cur, conn = connection()
    logger(__name__).warning("starting the database connection")
    cur.execute('SELECT *  FROM stock_data')
    rows = cur.fetchall()
    print(rows)
    if not rows:
        return jsonify({"message": f"No rows found "})
    data_list = []
    for row in rows:
        print("inside loop", row)
        stock_id, stock_name, quantity, buying_cost_per_unit, selling_cost_per_unit = row
        print("content", stock_id, stock_name, quantity, buying_cost_per_unit, selling_cost_per_unit)
        data = {
            "stock_id" : stock_id,
            "stock_name" : stock_name,
            "quantity" : quantity,
            "buying_cost_per_unit" : buying_cost_per_unit,
            "selling_cost_per_unit" : selling_cost_per_unit
        }
        data_list.append(data)
        logger(__name__).warning("close the database connection")
    print(data_list)
    return jsonify({"message":"all stocks","details":data_list})


@app.route("/stocks/<int:stock_id>", methods=["GET"], endpoint="particular_stock")
@handle_exceptions
def all_stocks(stock_id):
    cur, conn = connection()
    logger(__name__).warning("starting the database connection")
    cur.execute('SELECT stock_name, quantity, buying_cost_per_unit, selling_cost_per_unit  FROM stock_data WHERE stock_id = %s',(stock_id,))
    rows = cur.fetchone()
    if not rows:
        return jsonify({"message": f"No rows found "})
    data_list = []
    stock_name, quantity, buying_cost_per_unit, selling_cost_per_unit = rows
    data = {
            "stock_name" : stock_name,
            "quantity" : quantity,
            "buying_cost_per_unit" : buying_cost_per_unit,
            "selling_cost_per_unit" : selling_cost_per_unit
    }
    data_list.append(data)
    logger(__name__).warning("close the database connection")

    return jsonify({"message": "all stocks",  "details":data_list})


# update  buying and selling price of a particular stock
@app.route("/stocks/update/<int:stock_id>", methods=["PUT"], endpoint="update_cost")
@handle_exceptions
def update_cost(stock_id):
    cur, conn = connection()
    if "buying_cost_per_unit" and "selling_cost_per_unit" not in request.json:
        return Exception("details missing")
    data = request.get_json()
    selling_cost_per_unit = data['selling_cost_per_unit']
    buying_cost_per_unit = data['buying_cost_per_unit']
    cur.execute('SELECT buying_cost_per_unit,selling_cost_per_unit FROM stock_data WHERE stock_id=%s', (stock_id,))
    data = cur.fetchone()
    if data:
        cur.execute('UPDATE stock_data SET buying_cost_per_unit=%s, selling_cost_per_unit=%s WHERE stock_id=%s', (buying_cost_per_unit, selling_cost_per_unit, stock_id))
        conn.commit()
        return jsonify({"message":"updated successfully"})
    else:
        return jsonify({"message": "Stock not found"})


# delete stock data
@app.route("/stock/delete/<int:stock_id>", methods=["DELETE"], endpoint="delete_stock")
@handle_exceptions
def update_cost(stock_id):
    cur, conn = connection()
    logger(__name__).warning("starting the database connection")
    cur.execute('DELETE FROM stock_data WHERE stock_id=%s', (stock_id,))
    logger(__name__).warning("close the database connection")
    conn.commit()
    if cur.rowcount > 0:
        return jsonify({"message": "Stock deleted successfully"})
    else:
        return jsonify({"message": "Stock not found"})


# caluclate profit or loss
@app.route("/stock/<int:stock_id>",methods=["GET"], endpoint="calculate_profit_or_loss")
@handle_exceptions
def calculate_profit_or_loss(stock_id):
    cur, conn = connection()
    logger(__name__).warning("starting the database connection")
    cur.execute('SELECT quantity,buying_cost_per_unit,selling_cost_per_unit FROM stock_data WHERE stock_id=%s', (stock_id,))
    row = cur.fetchone()
    if row:
        quantity = row[0]
        buying_cost_per_unit = row[1]
        selling_cost_per_unit = row[2]

        if selling_cost_per_unit > buying_cost_per_unit:
            profit = (selling_cost_per_unit - buying_cost_per_unit)*quantity
            return jsonify({"profit": profit})
        else:
            loss = (buying_cost_per_unit - selling_cost_per_unit)*quantity
            return jsonify({"loss": loss})
    else:
        return jsonify({"message": "Stock not found"})

if __name__ == "__main__":
    app.run(debug=True, port=5000)


