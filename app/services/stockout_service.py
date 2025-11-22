from datetime import datetime, timedelta
from app.models.inventory import Inventory
from app.models.sku import SKU
from app.models.warehouse import Warehouse
from app.models.order_history import OrderHistory
from app.services.forecast_service import ForecastService


class StockoutService:
    def __init__(self):
        self.forecast_service = ForecastService()

    def calculate_stockout_date(self, current_stock, daily_demand):
        """Calculate when stockout will occur"""
        if daily_demand <= 0:
            return {
                "stockout_date": None,
                "days_until_stockout": float("inf"),
                "risk_level": "safe",
            }

        days_until_stockout = current_stock / daily_demand
        stockout_date = datetime.now() + timedelta(days=days_until_stockout)

        # Determine risk level
        if days_until_stockout < 3:
            risk_level = "high"
        elif days_until_stockout < 5:
            risk_level = "medium"
        else:
            risk_level = "safe"

        return {
            "stockout_date": stockout_date.strftime("%Y-%m-%d"),
            "days_until_stockout": round(days_until_stockout, 1),
            "risk_level": risk_level,
        }

    def get_all_alerts(self):
        """Get stockout alerts for all SKU-warehouse combinations"""
        alerts = []

        inventory_items = Inventory.query.join(SKU).join(Warehouse).all()

        for inv in inventory_items:
            # Get historical demand for this SKU at this warehouse
            historical = (
                OrderHistory.query.filter_by(
                    sku_id=inv.sku_id, warehouse_id=inv.warehouse_id
                )
                .order_by(OrderHistory.order_date.desc())
                .limit(10)
                .all()
            )

            historical_demand = (
                [h.quantity_ordered for h in historical] if historical else [10]
            )

            # Get daily forecast
            daily_forecast = self.forecast_service.predict_demand(
                inv.warehouse_id, inv.sku_id, historical_demand
            )

            # Calculate stockout info
            stockout_info = self.calculate_stockout_date(inv.quantity, daily_forecast)

            alerts.append(
                {
                    "sku_id": inv.sku_id,
                    "sku_name": inv.sku.name,
                    "sku_code": inv.sku.sku_code,
                    "warehouse_id": inv.warehouse_id,
                    "warehouse_name": inv.warehouse.name,
                    "current_stock": inv.quantity,
                    "daily_forecast": round(daily_forecast, 2),
                    "stockout_date": stockout_info["stockout_date"],
                    "days_until_stockout": stockout_info["days_until_stockout"],
                    "risk_level": stockout_info["risk_level"],
                }
            )

        # Sort by risk level (high first)
        risk_order = {"high": 0, "medium": 1, "safe": 2}
        alerts.sort(
            key=lambda x: (risk_order.get(x["risk_level"], 3), x["days_until_stockout"])
        )

        return alerts
