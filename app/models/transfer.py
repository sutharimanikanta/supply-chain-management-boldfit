from app import db
from datetime import datetime


class Transfer(db.Model):
    __tablename__ = "transfer"

    id = db.Column(db.Integer, primary_key=True)
    from_warehouse_id = db.Column(
        db.Integer, db.ForeignKey("warehouse.id"), nullable=False
    )
    to_warehouse_id = db.Column(
        db.Integer, db.ForeignKey("warehouse.id"), nullable=False
    )
    sku_id = db.Column(db.Integer, db.ForeignKey("sku.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.Text)
    status = db.Column(
        db.String(20), default="pending"
    )  # pending, in_transit, completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)

    def to_dict(self):
        return {
            "id": self.id,
            "from_warehouse_id": self.from_warehouse_id,
            "from_warehouse_name": self.from_warehouse.name
            if self.from_warehouse
            else None,
            "to_warehouse_id": self.to_warehouse_id,
            "to_warehouse_name": self.to_warehouse.name if self.to_warehouse else None,
            "sku_id": self.sku_id,
            "sku_name": self.sku.name if self.sku else None,
            "quantity": self.quantity,
            "reason": self.reason,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat()
            if self.completed_at
            else None,
        }
