from flask import Blueprint, render_template, request, jsonify
from app.models.order_history import OrderHistory
from app.models.inventory import Inventory
from app.models.warehouse import Warehouse
from app.models.sku import SKU
from app.services.forecast_service import ForecastService
from app.services.stockout_service import StockoutService
from app.services.reorder_service import ReorderService

forecast_bp = Blueprint("forecast", __name__, template_folder="../templates")


@forecast_bp.route("/")
def forecast_page():
    warehouses = Warehouse.query.all()
    skus = SKU.query.all()
    return render_template("forecast.html", warehouses=warehouses, skus=skus)


@forecast_bp.route("/sku", methods=["POST"])
def forecast_sku():
    """Predict orders for a specific SKU"""
    try:
        data = request.get_json() if request.is_json else request.form
        sku_id = int(data.get("sku_id"))
        warehouse_id = int(data.get("warehouse_id"))

        # Get historical demand (last 10 days)
        historical = (
            OrderHistory.query.filter_by(sku_id=sku_id, warehouse_id=warehouse_id)
            .order_by(OrderHistory.order_date.desc())
            .limit(10)
            .all()
        )

        historical_demand = (
            [h.quantity_ordered for h in historical] if historical else None
        )

        # Manual input fallback
        if not historical_demand:
            manual = data.get("historical_demand", "")
            if manual:
                historical_demand = [int(x.strip()) for x in str(manual).split(",")]
            else:
                historical_demand = [10, 12, 8, 15, 11, 9, 14, 10, 13, 12]  # Default

        # Get forecasts
        forecast_service = ForecastService()
        tomorrow_forecast = forecast_service.predict_demand(
            warehouse_id, sku_id, historical_demand
        )
        seven_day_forecast = forecast_service.predict_7_day_demand(
            warehouse_id, sku_id, historical_demand
        )

        # Get current inventory
        inventory = Inventory.query.filter_by(
            warehouse_id=warehouse_id, sku_id=sku_id
        ).first()
        current_stock = inventory.quantity if inventory else 0

        # Calculate stockout date
        stockout_service = StockoutService()
        stockout_info = stockout_service.calculate_stockout_date(
            current_stock, tomorrow_forecast
        )

        # Get reorder recommendation
        reorder_service = ReorderService()
        reorder_info = reorder_service.calculate_reorder(
            current_stock, seven_day_forecast, sku_id
        )

        return jsonify(
            {
                "status": "success",
                "sku_id": sku_id,
                "warehouse_id": warehouse_id,
                "current_stock": current_stock,
                "tomorrow_forecast": round(tomorrow_forecast, 2),
                "seven_day_forecast": round(seven_day_forecast, 2),
                "daily_average": round(seven_day_forecast / 7, 2),
                "stockout_date": stockout_info["stockout_date"],
                "days_until_stockout": stockout_info["days_until_stockout"],
                "risk_level": stockout_info["risk_level"],
                "reorder_quantity": reorder_info["reorder_quantity"],
                "reorder_urgency": reorder_info["urgency"],
            }
        )

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400


@forecast_bp.route("/stockout-alerts")
def stockout_alerts():
    """Get all SKUs with stockout risk"""
    stockout_service = StockoutService()
    alerts = stockout_service.get_all_alerts()
    return render_template("stockout_alerts.html", alerts=alerts)


@forecast_bp.route("/api/stockout-alerts")
def api_stockout_alerts():
    """API endpoint for stockout alerts"""
    stockout_service = StockoutService()
    alerts = stockout_service.get_all_alerts()
    return jsonify(alerts)


@forecast_bp.route("/reorder")
def reorder_page():
    """Reorder recommendations page"""
    reorder_service = ReorderService()
    recommendations = reorder_service.get_all_recommendations()
    return render_template("reorder.html", recommendations=recommendations)


@forecast_bp.route("/api/reorder")
def api_reorder():
    """API endpoint for reorder recommendations"""
    reorder_service = ReorderService()
    recommendations = reorder_service.get_all_recommendations()
    return jsonify(recommendations)
