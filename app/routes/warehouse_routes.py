from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from app.models.warehouse import Warehouse
from app import db

warehouse_bp = Blueprint("warehouse", __name__, template_folder="../templates")


@warehouse_bp.route("/")
def list_warehouses():
    warehouses = Warehouse.query.all()
    return render_template("warehouses.html", warehouses=warehouses)


@warehouse_bp.route("/api/list")
def api_list_warehouses():
    warehouses = Warehouse.query.all()
    return jsonify([w.to_dict() for w in warehouses])


@warehouse_bp.route("/add", methods=["GET", "POST"])
def add_warehouse():
    if request.method == "POST":
        warehouse = Warehouse(
            name=request.form["name"],
            location=request.form["location"],
            city=request.form["city"],
            description=request.form.get("description", ""),
        )
        db.session.add(warehouse)
        db.session.commit()
        return redirect(url_for("warehouse.list_warehouses"))
    return render_template("add_warehouse.html")


@warehouse_bp.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_warehouse(id):
    warehouse = Warehouse.query.get_or_404(id)
    if request.method == "POST":
        warehouse.name = request.form["name"]
        warehouse.location = request.form["location"]
        warehouse.city = request.form["city"]
        warehouse.description = request.form.get("description", "")
        db.session.commit()
        return redirect(url_for("warehouse.list_warehouses"))
    return render_template("edit_warehouse.html", warehouse=warehouse)


@warehouse_bp.route("/delete/<int:id>", methods=["POST"])
def delete_warehouse(id):
    warehouse = Warehouse.query.get_or_404(id)
    db.session.delete(warehouse)
    db.session.commit()
    return redirect(url_for("warehouse.list_warehouses"))
