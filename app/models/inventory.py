from app import db
from datetime import datetime


class Inventory(db.Model):
    __tablename__ = "inventory"

    id = db.Column(db.Integer, primary_key=True)
    warehouse_id = db.Column(db.Integer, db.ForeignKey("warehouse.id"), nullable=False)
    sku_id = db.Column(db.Integer, db.ForeignKey("sku.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    last_updated = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def to_dict(self):
        return {
            "id": self.id,
            "warehouse_id": self.warehouse_id,
            "warehouse_name": self.warehouse.name if self.warehouse else None,
            "sku_id": self.sku_id,
            "sku_name": self.sku.name if self.sku else None,
            "sku_code": self.sku.sku_code if self.sku else None,
            "quantity": self.quantity,
            "last_updated": self.last_updated.isoformat()
            if self.last_updated
            else None,
        }
