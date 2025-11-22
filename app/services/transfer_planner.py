from app.models.inventory import Inventory
from app.models.transfer import Transfer
from app.models.sku import SKU
from app.models.warehouse import Warehouse
from app.models.order_history import OrderHistory
from app.services.forecast_service import ForecastService
from datetime import datetime
from app import db


class TransferPlanner:
    def __init__(self):
        self.forecast_service = ForecastService()

    def get_transfer_suggestions(self):
        """Generate automated transfer suggestions based on demand forecasts"""
        suggestions = []

        # Get all SKUs
        skus = SKU.query.all()
        warehouses = Warehouse.query.all()

        for sku in skus:
            # Get inventory and forecast for each warehouse
            warehouse_data = []

            for warehouse in warehouses:
                inv = Inventory.query.filter_by(
                    sku_id=sku.id, warehouse_id=warehouse.id
                ).first()

                current_stock = inv.quantity if inv else 0

                # Get historical demand
                historical = (
                    OrderHistory.query.filter_by(
                        sku_id=sku.id, warehouse_id=warehouse.id
                    )
                    .order_by(OrderHistory.order_date.desc())
                    .limit(10)
                    .all()
                )

                historical_demand = (
                    [h.quantity_ordered for h in historical] if historical else [5]
                )

                # Get 7-day forecast
                forecast = self.forecast_service.predict_7_day_demand(
                    warehouse.id, sku.id, historical_demand
                )

                days_of_stock = (
                    current_stock / (forecast / 7) if forecast > 0 else float("inf")
                )

                warehouse_data.append(
                    {
                        "warehouse_id": warehouse.id,
                        "warehouse_name": warehouse.name,
                        "warehouse_city": warehouse.city,
                        "current_stock": current_stock,
                        "forecast": forecast,
                        "days_of_stock": days_of_stock,
                    }
                )

            # Find warehouses with excess and deficit
            excess_warehouses = [w for w in warehouse_data if w["days_of_stock"] > 14]
            deficit_warehouses = [w for w in warehouse_data if w["days_of_stock"] < 5]

            # Generate transfer suggestions
            for deficit in deficit_warehouses:
                for excess in excess_warehouses:
                    if excess["current_stock"] > 0:
                        # Calculate optimal transfer quantity
                        needed = max(
                            0, (deficit["forecast"] / 7 * 7) - deficit["current_stock"]
                        )
                        available = excess["current_stock"] - (
                            excess["forecast"] / 7 * 7
                        )

                        transfer_qty = min(needed, max(0, available))

                        if transfer_qty >= 5:  # Minimum transfer threshold
                            suggestions.append(
                                {
                                    "sku_id": sku.id,
                                    "sku_name": sku.name,
                                    "sku_code": sku.sku_code,
                                    "from_warehouse_id": excess["warehouse_id"],
                                    "from_warehouse_name": excess["warehouse_name"],
                                    "to_warehouse_id": deficit["warehouse_id"],
                                    "to_warehouse_name": deficit["warehouse_name"],
                                    "quantity": round(transfer_qty),
                                    "reason": f"Forecasted demand spike at {deficit['warehouse_name']}. "
                                    f"Current stock covers only {round(deficit['days_of_stock'], 1)} days.",
                                    "priority": "high"
                                    if deficit["days_of_stock"] < 3
                                    else "medium",
                                }
                            )

        # Sort by priority
        priority_order = {"high": 0, "medium": 1, "low": 2}
        suggestions.sort(key=lambda x: priority_order.get(x.get("priority", "low"), 3))

        return suggestions

    def execute_transfer(
        self, from_warehouse_id, to_warehouse_id, sku_id, quantity, reason=""
    ):
        """Execute a transfer between warehouses"""
        try:
            # Check source inventory
            source_inv = Inventory.query.filter_by(
                warehouse_id=from_warehouse_id, sku_id=sku_id
            ).first()

            if not source_inv or source_inv.quantity < quantity:
                return {
                    "status": "error",
                    "message": "Insufficient inventory at source warehouse",
                }

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

            return {
                "status": "success",
                "message": f"Successfully transferred {quantity} units",
                "transfer": transfer.to_dict(),
            }

        except Exception as e:
            db.session.rollback()
            return {"status": "error", "message": str(e)}
