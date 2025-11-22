import json
from config import Config
from app.models.inventory import Inventory
from app.models.sku import SKU
from app.models.warehouse import Warehouse
from app.models.order_history import OrderHistory
from app.services.forecast_service import ForecastService
from app.services.stockout_service import StockoutService
from app.services.reorder_service import ReorderService
from app.services.transfer_planner import TransferPlanner


class LLMAssistant:
    def __init__(self):
        self.groq_key = Config.GROQ_API_KEY

        # services
        self.forecast_service = ForecastService()
        self.stockout_service = StockoutService()
        self.reorder_service = ReorderService()
        self.transfer_planner = TransferPlanner()

    # -------------------------------------------------------------------------
    # Collect all supply-chain data as LLM context
    # -------------------------------------------------------------------------
    def _get_context(self):
        context = {
            "current_date": "2024-01-15",
            "warehouses": [],
            "skus": [],
            "inventory_summary": [],
            "stockout_alerts": [],
            "reorder_recommendations": [],
            "transfer_suggestions": [],
            "recent_orders": [],
        }

        # Warehouses
        warehouses = Warehouse.query.all()
        context["warehouses"] = [w.to_dict() for w in warehouses]

        # SKUs
        skus = SKU.query.all()
        context["skus"] = [s.to_dict() for s in skus]

        # Inventory summary
        inventory = Inventory.query.join(SKU).join(Warehouse).all()
        context["inventory_summary"] = [
            {
                "warehouse": i.warehouse.name,
                "sku": i.sku.name,
                "sku_code": i.sku.sku_code,
                "quantity": i.quantity,
            }
            for i in inventory
        ]

        # Stockout
        context["stockout_alerts"] = self.stockout_service.get_all_alerts()[:10]

        # Reorder
        context["reorder_recommendations"] = (
            self.reorder_service.get_all_recommendations()[:10]
        )

        # Transfer suggestions
        context["transfer_suggestions"] = (
            self.transfer_planner.get_transfer_suggestions()[:5]
        )

        # Last 20 orders
        recent = (
            OrderHistory.query.order_by(OrderHistory.order_date.desc()).limit(20).all()
        )
        context["recent_orders"] = [o.to_dict() for o in recent]

        return context

    # -------------------------------------------------------------------------
    # Build LLM system prompt
    # -------------------------------------------------------------------------
    def _build_system_prompt(self, context):
        return f"""
You are an AI Supply Chain Assistant for Boldfit.

You have access to the following REAL-TIME data:

WAREHOUSES:
{json.dumps(context["warehouses"], indent=2)}

SKUs:
{json.dumps(context["skus"], indent=2)}

INVENTORY:
{json.dumps(context["inventory_summary"], indent=2)}

STOCKOUT ALERTS:
{json.dumps(context["stockout_alerts"], indent=2)}

REORDER RECOMMENDATIONS:
{json.dumps(context["reorder_recommendations"], indent=2)}

TRANSFER SUGGESTIONS:
{json.dumps(context["transfer_suggestions"], indent=2)}

RECENT ORDERS:
{json.dumps(context["recent_orders"], indent=2)}

Your tasks:
- Identify stockout risks
- Recommend reorders
- Suggest warehouse transfers
- Analyze demand patterns
- Give Boldfit operational insights

Always use numbers, SKU names and warehouse names.
"""

    # -------------------------------------------------------------------------
    # Main Chat
    # -------------------------------------------------------------------------
    def chat(self, user_message):
        context = self._get_context()
        system_prompt = self._build_system_prompt(context)

        if self.groq_key:
            return self._chat_groq(system_prompt, user_message)
        else:
            return self._chat_fallback(context, user_message)

    # -------------------------------------------------------------------------
    # GROQ CHAT (NEW API 0.4.x)
    # -------------------------------------------------------------------------

    def _chat_groq(self, system_prompt, user_message):
        """Chat using Groq API - Compatible with groq==0.4.2"""
        try:
            # ✅ CORRECT import for groq 0.4.2
            from groq import Groq

            # Initialize client
            client = Groq(api_key=self.groq_key)

            # Make API call
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                temperature=0.7,
                max_tokens=1024,
            )

            # ✅ CORRECT way to access content in groq 0.4.2
            return response.choices[0].message.content

        except Exception as e:
            error_msg = str(e).lower()

            if "invalid_api_key" in error_msg or "authentication" in error_msg:
                return "❌ Invalid Groq API key. Please update your `.env`."

            if "rate_limit" in error_msg:
                return "⚠️ Rate limit reached. Try again later."

            return f"❌ Groq API Error: {str(e)}"


# =============================================================================
# ALTERNATIVE: If above still gives proxy error, use requests directly
# =============================================================================


# def _chat_groq(self, system_prompt, user_message):
#     """Chat using Groq API via direct HTTP request (no SDK issues)"""
#     import requests

#     url = "https://api.groq.com/openai/v1/chat/completions"

#     headers = {
#         "Authorization": f"Bearer {self.groq_key}",
#         "Content-Type": "application/json",
#     }

#     payload = {
#         "model": "llama-3.1-70b-versatile",
#         "messages": [
#             {"role": "system", "content": system_prompt},
#             {"role": "user", "content": user_message},
#         ],
#         "temperature": 0.7,
#         "max_tokens": 1024,
#     }

#     try:
#         response = requests.post(url, headers=headers, json=payload, timeout=60)

#         if response.status_code == 401:
#             return "❌ Invalid Groq API key. Check your `.env` file."

#         if response.status_code == 429:
#             return "⚠️ Rate limit reached. Please wait and try again."

#         response.raise_for_status()
#         data = response.json()
#         return data["choices"][0]["message"]["content"]

#     except requests.exceptions.Timeout:
#         return "⚠️ Request timed out. Please try again."
#     except requests.exceptions.RequestException as e:
#         return f"❌ Network Error: {str(e)}"
#     except Exception as e:
#         return f"❌ Error: {str(e)}"

#     # -------------------------------------------------------------------------
#     # FALLBACK MODE (No API Key)
#     # -------------------------------------------------------------------------
#     def _chat_fallback(self, context, user_message):
#         msg = user_message.lower()

#         if "risk" in msg or "stockout" in msg:
#             alerts = context["stockout_alerts"]
#             if not alerts:
#                 return "✅ No stockout risks."

#             response = "🚨 HIGH RISK STOCKOUTS:\n\n"
#             for a in alerts[:5]:
#                 response += (
#                     f"• {a['sku_name']} at {a['warehouse_name']} — "
#                     f"{a['current_stock']} units left, "
#                     f"{a['days_until_stockout']} days until stockout.\n"
#                 )
#             return response

#         if "reorder" in msg:
#             recs = context["reorder_recommendations"]
#             if not recs:
#                 return "✅ No reorder recommendations."

#             response = "📦 REORDER SUGGESTIONS:\n\n"
#             for r in recs[:5]:
#                 response += (
#                     f"• {r['sku_name']} — reorder {r['reorder_quantity']} units "
#                     f"(Urgency: {r['urgency'].upper()})\n"
#                 )
#             return response

#         if "transfer" in msg or "move" in msg:
#             suggestions = context["transfer_suggestions"]
#             if not suggestions:
#                 return "✅ No transfers needed."

#             response = "🚚 TRANSFER SUGGESTIONS:\n\n"
#             for s in suggestions[:5]:
#                 response += (
#                     f"• Move {s['quantity']} units of {s['sku_name']} "
#                     f"from {s['from_warehouse_name']} → {s['to_warehouse_name']}\n"
#                     f"  Reason: {s['reason']}\n\n"
#                 )
#             return response

#         if "inventory" in msg:
#             inv = context["inventory_summary"]
#             response = "📊 INVENTORY OVERVIEW:\n\n"
#             for i in inv[:10]:
#                 response += f"• {i['sku']} at {i['warehouse']}: {i['quantity']} units\n"
#             return response

#         return """
# ⚠️ Groq API key missing.

# Add this to your `.env`:

# GROQ_API_KEY=gsk_your_key_here

# Get a free key from https://console.groq.com
# """
