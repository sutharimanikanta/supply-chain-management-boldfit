from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from app.models.sku import SKU
from app import db

sku_bp = Blueprint("sku", __name__, template_folder="../templates")


@sku_bp.route("/")
def list_skus():
    skus = SKU.query.all()
    return render_template("skus.html", skus=skus)


@sku_bp.route("/api/list")
def api_list_skus():
    skus = SKU.query.all()
    return jsonify([s.to_dict() for s in skus])


@sku_bp.route("/add", methods=["GET", "POST"])
def add_sku():
    if request.method == "POST":
        sku = SKU(
            sku_code=request.form["sku_code"],
            name=request.form["name"],
            category=request.form.get("category", ""),
            description=request.form.get("description", ""),
            unit_price=float(request.form.get("unit_price", 0)),
            reorder_lead_days=int(request.form.get("reorder_lead_days", 3)),
            min_stock_level=int(request.form.get("min_stock_level", 10)),
        )
        db.session.add(sku)
        db.session.commit()
        return redirect(url_for("sku.list_skus"))
    return render_template("add_sku.html")


@sku_bp.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_sku(id):
    sku = SKU.query.get_or_404(id)
    if request.method == "POST":
        sku.sku_code = request.form["sku_code"]
        sku.name = request.form["name"]
        sku.category = request.form.get("category", "")
        sku.description = request.form.get("description", "")
        sku.unit_price = float(request.form.get("unit_price", 0))
        sku.reorder_lead_days = int(request.form.get("reorder_lead_days", 3))
        sku.min_stock_level = int(request.form.get("min_stock_level", 10))
        db.session.commit()
        return redirect(url_for("sku.list_skus"))
    return render_template("edit_sku.html", sku=sku)


@sku_bp.route("/delete/<int:id>", methods=["POST"])
def delete_sku(id):
    sku = SKU.query.get_or_404(id)
    db.session.delete(sku)
    db.session.commit()
    return redirect(url_for("sku.list_skus"))
