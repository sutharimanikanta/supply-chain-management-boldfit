################################################################################
# FILE: seed_demo_data.py
#
# This script ADDS data to your existing Warehouses
# Run: python seed_demo_data.py
################################################################################

from app import create_app, db
from app.models.warehouse import Warehouse
from app.models.sku import SKU
from app.models.inventory import Inventory
from app.models.order_history import OrderHistory
from datetime import datetime, timedelta
import random

app = create_app()


def seed_demo_data():
    with app.app_context():
        # =====================================================================
        # STEP 1: Check existing Warehouses
        # =====================================================================
        print("📍 Checking Warehouses...")
        warehouses = Warehouse.query.all()

        if not warehouses:
            print("❌ No warehouses found! Please add warehouses first via UI.")
            return

        print(f"   Found {len(warehouses)} warehouses:")
        for w in warehouses:
            print(f"   - ID {w.id}: {w.name} ({w.city})")

        # =====================================================================
        # STEP 2: Add SKUs (if not already present)
        # =====================================================================
        print("\n📦 Adding SKUs...")

        skus_to_add = [
            (
                "BF-WHEY-1KG-CHOC",
                "Whey Protein 1kg Chocolate",
                "supplementory",
                2000.0,
                3,
                10,
            ),
            ("BF-BCAA-300G", "BCAA Powder 300g Berry", "supplementory", 799.0, 4, 40),
            ("BF-BANDS-SET5", "Resistance Bands Set 5pcs", "equipment", 449.0, 3, 100),
            ("BF-YOGA-6MM", "Premium Yoga Mat 6mm", "equipment", 699.0, 3, 80),
            ("BF-SHAKER-700", "Protein Shaker 700ml", "accessories", 299.0, 2, 150),
            (
                "BF-CREATINE-250",
                "Creatine Monohydrate 250g",
                "supplementory",
                599.0,
                4,
                60,
            ),
        ]

        for sku_code, name, category, price, lead, min_stock in skus_to_add:
            existing = SKU.query.filter_by(sku_code=sku_code).first()
            if not existing:
                sku = SKU(
                    sku_code=sku_code,
                    name=name,
                    category=category,
                    unit_price=price,
                    reorder_lead_days=lead,
                    min_stock_level=min_stock,
                )
                db.session.add(sku)
                print(f"   ✅ Added: {name}")
            else:
                print(f"   ⏭️  Exists: {name}")

        db.session.commit()

        # =====================================================================
        # STEP 3: Get all SKUs and Warehouses
        # =====================================================================
        all_skus = SKU.query.all()
        all_warehouses = Warehouse.query.all()

        print(f"\n📊 Total SKUs: {len(all_skus)}")

        # Map warehouses by city (case-insensitive)
        wh_map = {}
        for w in all_warehouses:
            city_lower = w.city.lower()
            wh_map[city_lower] = w

        # =====================================================================
        # STEP 4: Clear old inventory and orders (fresh start)
        # =====================================================================
        print("\n🗑️  Clearing old inventory and order history...")
        OrderHistory.query.delete()
        Inventory.query.delete()
        db.session.commit()

        # =====================================================================
        # STEP 5: Add Inventory with strategic quantities
        # =====================================================================
        print("\n📈 Adding Inventory...")

        # Inventory levels per city
        # Format: {city: {sku_code: quantity}}
        inventory_plan = {
            "hyderabad": {  # HIGH stock - transfer source
                "BF-WHEY-1KG-CHOC": 200,
                "BF-BCAA-300G": 150,
                "BF-BANDS-SET5": 300,
                "BF-YOGA-6MM": 180,
                "BF-SHAKER-700": 400,
                "BF-CREATINE-250": 220,
            },
            "bangalore": {  # LOW stock - will show alerts
                "BF-WHEY-1KG-CHOC": 12,
                "BF-BCAA-300G": 8,
                "BF-BANDS-SET5": 20,
                "BF-YOGA-6MM": 10,
                "BF-SHAKER-700": 35,
                "BF-CREATINE-250": 7,
            },
            "mumbai": {  # Medium stock
                "BF-WHEY-1KG-CHOC": 80,
                "BF-BCAA-300G": 60,
                "BF-BANDS-SET5": 100,
                "BF-YOGA-6MM": 70,
                "BF-SHAKER-700": 120,
                "BF-CREATINE-250": 55,
            },
            "delhi": {  # Mixed stock
                "BF-WHEY-1KG-CHOC": 50,
                "BF-BCAA-300G": 35,
                "BF-BANDS-SET5": 80,
                "BF-YOGA-6MM": 45,
                "BF-SHAKER-700": 200,
                "BF-CREATINE-250": 25,
            },
        }

        inventory_count = 0
        for city, sku_quantities in inventory_plan.items():
            warehouse = wh_map.get(city)
            if not warehouse:
                print(f"   ⚠️  Warehouse not found for city: {city}")
                continue

            for sku_code, qty in sku_quantities.items():
                sku = SKU.query.filter_by(sku_code=sku_code).first()
                if sku:
                    inv = Inventory(
                        warehouse_id=warehouse.id, sku_id=sku.id, quantity=qty
                    )
                    db.session.add(inv)
                    inventory_count += 1

        db.session.commit()
        print(f"   ✅ Added {inventory_count} inventory records")

        # =====================================================================
        # STEP 6: Add Order History (14 days for forecasting)
        # =====================================================================
        print("\n📅 Adding Order History (14 days)...")

        # Average daily demand per city
        demand_patterns = {
            "hyderabad": {
                "BF-WHEY-1KG-CHOC": 12,
                "BF-BCAA-300G": 8,
                "BF-BANDS-SET5": 15,
                "BF-YOGA-6MM": 10,
                "BF-SHAKER-700": 20,
                "BF-CREATINE-250": 9,
            },
            "bangalore": {  # High demand + low stock = alerts!
                "BF-WHEY-1KG-CHOC": 8,
                "BF-BCAA-300G": 6,
                "BF-BANDS-SET5": 12,
                "BF-YOGA-6MM": 7,
                "BF-SHAKER-700": 15,
                "BF-CREATINE-250": 5,
            },
            "mumbai": {
                "BF-WHEY-1KG-CHOC": 10,
                "BF-BCAA-300G": 6,
                "BF-BANDS-SET5": 14,
                "BF-YOGA-6MM": 8,
                "BF-SHAKER-700": 18,
                "BF-CREATINE-250": 7,
            },
            "delhi": {
                "BF-WHEY-1KG-CHOC": 9,
                "BF-BCAA-300G": 5,
                "BF-BANDS-SET5": 11,
                "BF-YOGA-6MM": 6,
                "BF-SHAKER-700": 16,
                "BF-CREATINE-250": 8,
            },
        }

        order_count = 0
        for days_ago in range(14):
            order_date = datetime.utcnow() - timedelta(days=days_ago)

            for city, sku_demands in demand_patterns.items():
                warehouse = wh_map.get(city)
                if not warehouse:
                    continue

                for sku_code, avg_demand in sku_demands.items():
                    sku = SKU.query.filter_by(sku_code=sku_code).first()
                    if sku:
                        # Add ±30% variation
                        qty = max(1, int(avg_demand * random.uniform(0.7, 1.3)))

                        order = OrderHistory(
                            warehouse_id=warehouse.id,
                            sku_id=sku.id,
                            quantity_ordered=qty,
                            order_date=order_date,
                            fulfilled=True,
                        )
                        db.session.add(order)
                        order_count += 1

        db.session.commit()
        print(f"   ✅ Added {order_count} order history records")

        # =====================================================================
        # SUMMARY
        # =====================================================================
        print("\n" + "=" * 60)
        print("✅ DEMO DATA READY!")
        print("=" * 60)
        print(f"   Warehouses: {Warehouse.query.count()}")
        print(f"   SKUs: {SKU.query.count()}")
        print(f"   Inventory: {Inventory.query.count()}")
        print(f"   Order History: {OrderHistory.query.count()}")
        print("=" * 60)
        print("\n🚀 Now test these features:")
        print("   1. /forecast → Select Bangalore + Whey Protein")
        print("   2. /forecast/stockout-alerts → See RED alerts")
        print("   3. /forecast/reorder → See CRITICAL recommendations")
        print("   4. /transfers/suggestions → See transfer suggestions")
        print("   5. /assistant → Ask 'Which SKUs are at risk?'")
        print("=" * 60)


if __name__ == "__main__":
    seed_demo_data()
