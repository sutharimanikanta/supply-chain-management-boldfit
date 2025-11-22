from app import db


class Warehouse(db.Model):
    __tablename__ = "warehouse"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)

    # Relationships
    inventory = db.relationship("Inventory", backref="warehouse", lazy=True)
    order_history = db.relationship("OrderHistory", backref="warehouse", lazy=True)
    transfers_from = db.relationship(
        "Transfer",
        foreign_keys="Transfer.from_warehouse_id",
        backref="from_warehouse",
        lazy=True,
    )
    transfers_to = db.relationship(
        "Transfer",
        foreign_keys="Transfer.to_warehouse_id",
        backref="to_warehouse",
        lazy=True,
    )

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "location": self.location,
            "city": self.city,
            "description": self.description,
            "is_active": self.is_active,
        }
