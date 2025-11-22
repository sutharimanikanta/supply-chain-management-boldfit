from app import db
from datetime import datetime


class OrderHistory(db.Model):
    __tablename__ = "order_history"

    id = db.Column(db.Integer, primary_key=True)
    warehouse_id = db.Column(db.Integer, db.ForeignKey("warehouse.id"), nullable=False)
    sku_id = db.Column(db.Integer, db.ForeignKey("sku.id"), nullable=False)
    quantity_ordered = db.Column(db.Integer, nullable=False)
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    fulfilled = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            "id": self.id,
            "warehouse_id": self.warehouse_id,
            "warehouse_name": self.warehouse.name if self.warehouse else None,
            "sku_id": self.sku_id,
            "sku_name": self.sku.name if self.sku else None,
            "quantity_ordered": self.quantity_ordered,
            "order_date": self.order_date.isoformat() if self.order_date else None,
            "fulfilled": self.fulfilled,
        }
