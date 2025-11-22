from app import db


class SKU(db.Model):
    __tablename__ = "sku"

    id = db.Column(db.Integer, primary_key=True)
    sku_code = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100))
    description = db.Column(db.Text)
    unit_price = db.Column(db.Float, default=0.0)
    reorder_lead_days = db.Column(db.Integer, default=3)
    min_stock_level = db.Column(db.Integer, default=10)
    is_active = db.Column(db.Boolean, default=True)

    # Relationships
    inventory = db.relationship("Inventory", backref="sku", lazy=True)
    order_history = db.relationship("OrderHistory", backref="sku", lazy=True)
    transfers = db.relationship("Transfer", backref="sku", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "sku_code": self.sku_code,
            "name": self.name,
            "category": self.category,
            "description": self.description,
            "unit_price": self.unit_price,
            "reorder_lead_days": self.reorder_lead_days,
            "min_stock_level": self.min_stock_level,
            "is_active": self.is_active,
        }
