from flask import Blueprint, render_template, jsonify
from app.models.inventory import Inventory
from app.models.sku import SKU
from app.models.warehouse import Warehouse
from app.models.order_history import OrderHistory
from app.services.stockout_service import StockoutService
from app.services.reorder_service import ReorderService
from sqlalchemy import func
from app import db

dashboard_bp = Blueprint("dashboard", __name__, template_folder="../templates")


@dashboard_bp.route("/")
def founder_dashboard():
    """Founder Dashboard with key metrics"""
    return render_template("dashboard.html")


@dashboard_bp.route("/api/metrics")
def api_metrics():
    """API endpoint for dashboard metrics"""
    try:
        # Top 5 SKUs by demand (last 30 days)
        top_demand = (
            db.session.query(
                SKU.name,
                SKU.sku_code,
                func.sum(OrderHistory.quantity_ordered).label("total_orders"),
            )
            .join(OrderHistory)
            .group_by(SKU.id)
            .order_by(func.sum(OrderHistory.quantity_ordered).desc())
            .limit(5)
            .all()
        )

        top_demand_list = [
            {"name": r[0], "sku_code": r[1], "total_orders": r[2] or 0}
            for r in top_demand
        ]

        # Top 5 at risk (stockout)
        stockout_service = StockoutService()
        all_alerts = stockout_service.get_all_alerts()
        at_risk = [a for a in all_alerts if a["risk_level"] in ["high", "medium"]][:5]

        # Current stock value
        stock_value = (
            db.session.query(func.sum(Inventory.quantity * SKU.unit_price))
            .join(SKU)
            .scalar()
            or 0
        )

        # Total inventory count
        total_inventory = db.session.query(func.sum(Inventory.quantity)).scalar() or 0

        # Reorder budget required
        reorder_service = ReorderService()
        recommendations = reorder_service.get_all_recommendations()
        reorder_budget = sum(
            r.get("reorder_quantity", 0) * r.get("unit_price", 0)
            for r in recommendations
            if r.get("reorder_quantity", 0) > 0
        )

        # Warehouse summary
        warehouses = Warehouse.query.all()
        warehouse_summary = []
        for w in warehouses:
            inv_count = (
                db.session.query(func.sum(Inventory.quantity))
                .filter(Inventory.warehouse_id == w.id)
                .scalar()
                or 0
            )
            warehouse_summary.append(
                {"name": w.name, "city": w.city, "total_units": inv_count}
            )

        return jsonify(
            {
                "status": "success",
                "top_demand": top_demand_list,
                "at_risk": at_risk,
                "stock_value": round(stock_value, 2),
                "total_inventory": total_inventory,
                "reorder_budget": round(reorder_budget, 2),
                "warehouse_summary": warehouse_summary,
                "total_skus": SKU.query.count(),
                "total_warehouses": Warehouse.query.count(),
            }
        )

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
