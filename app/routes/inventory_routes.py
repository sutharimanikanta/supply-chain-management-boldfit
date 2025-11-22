from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from app.models.inventory import Inventory
from app.models.warehouse import Warehouse
from app.models.sku import SKU
from app import db

inventory_bp = Blueprint("inventory", __name__, template_folder="../templates")


@inventory_bp.route("/")
def list_inventory():
    inventory = Inventory.query.join(Warehouse).join(SKU).all()
    warehouses = Warehouse.query.all()
    skus = SKU.query.all()
    return render_template(
        "inventory.html", inventory=inventory, warehouses=warehouses, skus=skus
    )


@inventory_bp.route("/api/list")
def api_list_inventory():
    inventory = Inventory.query.all()
    return jsonify([i.to_dict() for i in inventory])


@inventory_bp.route("/api/by-sku/<int:sku_id>")
def api_inventory_by_sku(sku_id):
    inventory = Inventory.query.filter_by(sku_id=sku_id).all()
    return jsonify([i.to_dict() for i in inventory])


@inventory_bp.route("/add", methods=["GET", "POST"])
def add_inventory():
    warehouses = Warehouse.query.all()
    skus = SKU.query.all()
    if request.method == "POST":
        # Check if entry already exists
        existing = Inventory.query.filter_by(
            warehouse_id=request.form["warehouse_id"], sku_id=request.form["sku_id"]
        ).first()

        if existing:
            existing.quantity += int(request.form["quantity"])
        else:
            inventory = Inventory(
                warehouse_id=request.form["warehouse_id"],
                sku_id=request.form["sku_id"],
                quantity=request.form["quantity"],
            )
            db.session.add(inventory)

        db.session.commit()
        return redirect(url_for("inventory.list_inventory"))
    return render_template("add_inventory.html", warehouses=warehouses, skus=skus)


@inventory_bp.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_inventory(id):
    inventory = Inventory.query.get_or_404(id)
    warehouses = Warehouse.query.all()
    skus = SKU.query.all()
    if request.method == "POST":
        inventory.warehouse_id = request.form["warehouse_id"]
        inventory.sku_id = request.form["sku_id"]
        inventory.quantity = request.form["quantity"]
        db.session.commit()
        return redirect(url_for("inventory.list_inventory"))
    return render_template(
        "edit_inventory.html", inventory=inventory, warehouses=warehouses, skus=skus
    )


@inventory_bp.route("/delete/<int:id>", methods=["POST"])
def delete_inventory(id):
    inventory = Inventory.query.get_or_404(id)
    db.session.delete(inventory)
    db.session.commit()
    return redirect(url_for("inventory.list_inventory"))
