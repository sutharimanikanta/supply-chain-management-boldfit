# from flask import Blueprint, render_template, request, redirect, url_for, jsonify
# from app.models.transfer import Transfer
# from app.models.inventory import Inventory
# from app.models.warehouse import Warehouse
# from app.models.sku import SKU
# from app.services.transfer_planner import TransferPlanner
# from app import db
# from datetime import datetime

# transfer_bp = Blueprint("transfer", __name__, template_folder="../templates")


# @transfer_bp.route("/")
# def list_transfers():
#     transfers = Transfer.query.order_by(Transfer.created_at.desc()).all()
#     warehouses = Warehouse.query.all()
#     skus = SKU.query.all()
#     return render_template(
#         "transfers.html", transfers=transfers, warehouses=warehouses, skus=skus
#     )


# @transfer_bp.route("/api/list")
# def api_list_transfers():
#     transfers = Transfer.query.order_by(Transfer.created_at.desc()).all()
#     return jsonify([t.to_dict() for t in transfers])


# @transfer_bp.route("/add", methods=["POST"])
# def add_transfer():
#     try:
#         data = request.get_json() if request.is_json else request.form

#         from_warehouse_id = int(data["from_warehouse_id"])
#         to_warehouse_id = int(data["to_warehouse_id"])
#         sku_id = int(data["sku_id"])
#         quantity = int(data["quantity"])
#         reason = data.get("reason", "Manual transfer")

#         # Check source inventory
#         source_inv = Inventory.query.filter_by(
#             warehouse_id=from_warehouse_id, sku_id=sku_id
#         ).first()

#         if not source_inv or source_inv.quantity < quantity:
#             return jsonify(
#                 {
#                     "status": "error",
#                     "message": "Insufficient inventory at source warehouse",
#                 }
#             ), 400

#         # Update source inventory
#         source_inv.quantity -= quantity

#         # Update destination inventory
#         dest_inv = Inventory.query.filter_by(
#             warehouse_id=to_warehouse_id, sku_id=sku_id
#         ).first()

#         if dest_inv:
#             dest_inv.quantity += quantity
#         else:
#             dest_inv = Inventory(
#                 warehouse_id=to_warehouse_id, sku_id=sku_id, quantity=quantity
#             )
#             db.session.add(dest_inv)

#         # Create transfer record
#         transfer = Transfer(
#             from_warehouse_id=from_warehouse_id,
#             to_warehouse_id=to_warehouse_id,
#             sku_id=sku_id,
#             quantity=quantity,
#             reason=reason,
#             status="completed",
#             completed_at=datetime.utcnow(),
#         )
#         db.session.add(transfer)
#         db.session.commit()

#         if request.is_json:
#             return jsonify({"status": "success", "transfer": transfer.to_dict()})
#         return redirect(url_for("transfer.list_transfers"))

#     except Exception as e:
#         db.session.rollback()
#         return jsonify({"status": "error", "message": str(e)}), 400


# @transfer_bp.route("/suggestions")
# def transfer_suggestions():
#     """Get automated transfer suggestions"""
#     planner = TransferPlanner()
#     suggestions = planner.get_transfer_suggestions()
#     return render_template("transfer_suggestions.html", suggestions=suggestions)


# @transfer_bp.route("/api/suggestions")
# def api_transfer_suggestions():
#     """API endpoint for transfer suggestions"""
#     planner = TransferPlanner()
#     suggestions = planner.get_transfer_suggestions()
#     return jsonify(suggestions)


# @transfer_bp.route("/execute-suggestion", methods=["POST"])
# def execute_suggestion():
#     """Execute a suggested transfer"""
#     try:
#         data = request.get_json()
#         planner = TransferPlanner()
#         result = planner.execute_transfer(
#             from_warehouse_id=data["from_warehouse_id"],
#             to_warehouse_id=data["to_warehouse_id"],
#             sku_id=data["sku_id"],
#             quantity=data["quantity"],
#             reason=data.get("reason", "Automated rebalancing"),
#         )
#         return jsonify(result)
#     except Exception as e:
#         return jsonify({"status": "error", "message": str(e)}), 400
################################################################################
# FILE: app/routes/transfer_routes.py
#
# Replace your entire transfer_routes.py with this file
################################################################################

from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from app.models.transfer import Transfer
from app.models.inventory import Inventory
from app.models.warehouse import Warehouse
from app.models.sku import SKU
from app.services.transfer_planner import TransferPlanner
from app import db
from datetime import datetime

transfer_bp = Blueprint("transfer", __name__, template_folder="../templates")


@transfer_bp.route("/")
def list_transfers():
    transfers = Transfer.query.order_by(Transfer.created_at.desc()).all()
    warehouses = Warehouse.query.all()
    skus = SKU.query.all()
    return render_template(
        "transfers.html", transfers=transfers, warehouses=warehouses, skus=skus
    )


@transfer_bp.route("/api/list")
def api_list_transfers():
    transfers = Transfer.query.order_by(Transfer.created_at.desc()).all()
    return jsonify([t.to_dict() for t in transfers])


@transfer_bp.route("/add", methods=["POST"])
def add_transfer():
    try:
        data = request.get_json() if request.is_json else request.form

        from_warehouse_id = int(data["from_warehouse_id"])
        to_warehouse_id = int(data["to_warehouse_id"])
        sku_id = int(data["sku_id"])
        quantity = int(data["quantity"])
        reason = data.get("reason", "Manual transfer")

        # Check source inventory
        source_inv = Inventory.query.filter_by(
            warehouse_id=from_warehouse_id, sku_id=sku_id
        ).first()

        if not source_inv or source_inv.quantity < quantity:
            return jsonify(
                {
                    "status": "error",
                    "message": "Insufficient inventory at source warehouse",
                }
            ), 400

        # Update source inventory
        source_inv.quantity -= quantity

        # Update destination inventory
        dest_inv = Inventory.query.filter_by(
            warehouse_id=to_warehouse_id, sku_id=sku_id
        ).first()

        if dest_inv:
            dest_inv.quantity += quantity
        else:
            dest_inv = Inventory(
                warehouse_id=to_warehouse_id, sku_id=sku_id, quantity=quantity
            )
            db.session.add(dest_inv)

        # Create transfer record
        transfer = Transfer(
            from_warehouse_id=from_warehouse_id,
            to_warehouse_id=to_warehouse_id,
            sku_id=sku_id,
            quantity=quantity,
            reason=reason,
            status="completed",
            completed_at=datetime.utcnow(),
        )
        db.session.add(transfer)
        db.session.commit()

        if request.is_json:
            return jsonify({"status": "success", "transfer": transfer.to_dict()})
        return redirect(url_for("transfer.list_transfers"))

    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 400


@transfer_bp.route("/suggestions")
def transfer_suggestions():
    """Get automated transfer suggestions"""
    planner = TransferPlanner()
    suggestions = planner.get_transfer_suggestions()
    return render_template("transfer_suggestions.html", suggestions=suggestions)


@transfer_bp.route("/api/suggestions")
def api_transfer_suggestions():
    """API endpoint for transfer suggestions"""
    planner = TransferPlanner()
    suggestions = planner.get_transfer_suggestions()
    return jsonify(suggestions)


@transfer_bp.route("/execute-suggestion", methods=["POST"])
def execute_suggestion():
    """Execute a suggested transfer - FIXED VERSION"""
    try:
        # Get JSON data from request
        data = request.get_json()

        if not data:
            return jsonify({"status": "error", "message": "No data received"}), 400

        # Extract and validate parameters
        from_warehouse_id = int(data.get("from_warehouse_id"))
        to_warehouse_id = int(data.get("to_warehouse_id"))
        sku_id = int(data.get("sku_id"))
        quantity = int(data.get("quantity"))
        reason = data.get("reason", "Automated rebalancing")

        # Log for debugging
        print(f"[Transfer] Executing: {quantity} units of SKU {sku_id}")
        print(
            f"[Transfer] From warehouse {from_warehouse_id} to warehouse {to_warehouse_id}"
        )

        # Validate entities exist
        from_warehouse = Warehouse.query.get(from_warehouse_id)
        to_warehouse = Warehouse.query.get(to_warehouse_id)
        sku = SKU.query.get(sku_id)

        if not from_warehouse:
            return jsonify(
                {
                    "status": "error",
                    "message": f"Source warehouse (ID: {from_warehouse_id}) not found",
                }
            ), 400

        if not to_warehouse:
            return jsonify(
                {
                    "status": "error",
                    "message": f"Destination warehouse (ID: {to_warehouse_id}) not found",
                }
            ), 400

        if not sku:
            return jsonify(
                {"status": "error", "message": f"SKU (ID: {sku_id}) not found"}
            ), 400

        # Check source inventory exists and has enough quantity
        source_inv = Inventory.query.filter_by(
            warehouse_id=from_warehouse_id, sku_id=sku_id
        ).first()

        if not source_inv:
            return jsonify(
                {
                    "status": "error",
                    "message": f"No inventory record for {sku.name} at {from_warehouse.name}",
                }
            ), 400

        if source_inv.quantity < quantity:
            return jsonify(
                {
                    "status": "error",
                    "message": f"Insufficient inventory. Available: {source_inv.quantity}, Requested: {quantity}",
                }
            ), 400

        # ===== PERFORM THE TRANSFER =====

        # 1. Subtract from source
        source_inv.quantity -= quantity
        print(
            f"[Transfer] Source inventory updated: {source_inv.quantity + quantity} -> {source_inv.quantity}"
        )

        # 2. Add to destination
        dest_inv = Inventory.query.filter_by(
            warehouse_id=to_warehouse_id, sku_id=sku_id
        ).first()

        if dest_inv:
            old_qty = dest_inv.quantity
            dest_inv.quantity += quantity
            print(
                f"[Transfer] Destination inventory updated: {old_qty} -> {dest_inv.quantity}"
            )
        else:
            # Create new inventory record at destination
            dest_inv = Inventory(
                warehouse_id=to_warehouse_id, sku_id=sku_id, quantity=quantity
            )
            db.session.add(dest_inv)
            print(f"[Transfer] New inventory record created at destination: {quantity}")

        # 3. Create transfer record
        transfer = Transfer(
            from_warehouse_id=from_warehouse_id,
            to_warehouse_id=to_warehouse_id,
            sku_id=sku_id,
            quantity=quantity,
            reason=reason,
            status="completed",
            completed_at=datetime.utcnow(),
        )
        db.session.add(transfer)

        # 4. Commit all changes
        db.session.commit()

        print(f"[Transfer] SUCCESS! Transfer ID: {transfer.id}")

        # Return success response
        return jsonify(
            {
                "status": "success",
                "message": f"Transferred {quantity} units of {sku.name} from {from_warehouse.name} to {to_warehouse.name}",
                "transfer_id": transfer.id,
                "details": {
                    "sku_name": sku.name,
                    "from_warehouse": from_warehouse.name,
                    "to_warehouse": to_warehouse.name,
                    "quantity": quantity,
                    "new_source_quantity": source_inv.quantity,
                    "new_destination_quantity": dest_inv.quantity,
                },
            }
        )

    except ValueError as e:
        print(f"[Transfer] ValueError: {str(e)}")
        return jsonify(
            {"status": "error", "message": f"Invalid data format: {str(e)}"}
        ), 400

    except Exception as e:
        db.session.rollback()
        print(f"[Transfer] Exception: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500
