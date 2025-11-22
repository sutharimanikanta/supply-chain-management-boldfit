from app.models.inventory import Inventory
from app.models.sku import SKU
from app.models.warehouse import Warehouse
from app.models.order_history import OrderHistory
from app.services.forecast_service import ForecastService


class ReorderService:
    def __init__(self):
        self.forecast_service = ForecastService()
        self.safety_multiplier = 1.2  # 20% buffer

    def calculate_reorder(self, current_stock, seven_day_forecast, sku_id):
        """Calculate reorder quantity recommendation"""
        sku = SKU.query.get(sku_id)
        lead_time = sku.reorder_lead_days if sku else 3

        # Formula: (7-day-forecast * safety_multiplier) - current_inventory
        target_stock = seven_day_forecast * self.safety_multiplier
        reorder_qty = max(0, target_stock - current_stock)

        # Determine urgency
        days_of_stock = (
            current_stock / (seven_day_forecast / 7)
            if seven_day_forecast > 0
            else float("inf")
        )

        if days_of_stock < lead_time:
            urgency = "critical"
        elif days_of_stock < lead_time + 2:
            urgency = "high"
        elif days_of_stock < 7:
            urgency = "medium"
        else:
            urgency = "low"

        return {
            "reorder_quantity": round(reorder_qty),
            "urgency": urgency,
            "lead_time_days": lead_time,
            "target_stock": round(target_stock),
        }

    def get_all_recommendations(self):
        """Get reorder recommendations for all SKU-warehouse combinations"""
        recommendations = []

        inventory_items = Inventory.query.join(SKU).join(Warehouse).all()

        for inv in inventory_items:
            # Get historical demand
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

            # Get 7-day forecast
            seven_day_forecast = self.forecast_service.predict_7_day_demand(
                inv.warehouse_id, inv.sku_id, historical_demand
            )

            # Calculate reorder info
            reorder_info = self.calculate_reorder(
                inv.quantity, seven_day_forecast, inv.sku_id
            )

            if reorder_info["reorder_quantity"] > 0:
                recommendations.append(
                    {
                        "sku_id": inv.sku_id,
                        "sku_name": inv.sku.name,
                        "sku_code": inv.sku.sku_code,
                        "warehouse_id": inv.warehouse_id,
                        "warehouse_name": inv.warehouse.name,
                        "current_stock": inv.quantity,
                        "seven_day_forecast": round(seven_day_forecast, 2),
                        "reorder_quantity": reorder_info["reorder_quantity"],
                        "urgency": reorder_info["urgency"],
                        "lead_time_days": reorder_info["lead_time_days"],
                        "unit_price": inv.sku.unit_price,
                        "reorder_cost": round(
                            reorder_info["reorder_quantity"] * inv.sku.unit_price, 2
                        ),
                    }
                )

        # Sort by urgency
        urgency_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        recommendations.sort(key=lambda x: urgency_order.get(x["urgency"], 4))

        return recommendations
