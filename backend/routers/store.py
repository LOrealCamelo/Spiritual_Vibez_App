"""
NeuroSpicy Mystic Sanctuary Storefront & E-Commerce Router
Official Creator Store: https://www.neurospicymystic.com
"""
from datetime import datetime
from fastapi import APIRouter, HTTPException
from ..models import StoreCartAddRequest
from ..database import get_connection

router = APIRouter()

STORE_URL = "https://www.neurospicymystic.com"

PRODUCTS = [
    {
        "id": "tattoo-tarot-deck",
        "title": "Tattoo Tarot: Ink & Intuition Deck",
        "price": 48.00,
        "currency": "USD",
        "category": "Tarot Decks",
        "in_stock": True,
        "description": "78 custom Marseille-inspired illustrated cards with iconic tattoo symbolism (heart, dagger, rose, snake, diamond) and astrological decans.",
        "url": f"{STORE_URL}/products/tattoo-tarot-deck",
        "tiktok_shop_enabled": True
    },
    {
        "id": "528hz-tuning-forks",
        "title": "528Hz Weighted & Unweighted Tuning Forks",
        "price": 64.00,
        "currency": "USD",
        "category": "Sound Healing",
        "in_stock": True,
        "description": "Medical-grade aluminum biosonic tuning fork with ergonomic grip and activator mallet for somatic nervous system reset.",
        "url": f"{STORE_URL}/products/528hz-tuning-forks",
        "tiktok_shop_enabled": True
    },
    {
        "id": "celestial-apparel",
        "title": "Sacred Geometry & Velvet Apparel",
        "price": 55.00,
        "currency": "USD",
        "category": "Ceremonial Apparel",
        "in_stock": True,
        "description": "Heavyweight organic cotton ceremonial hoodies and celestial kimonos with embroidered moon phase alignments.",
        "url": f"{STORE_URL}/collections/apparel",
        "tiktok_shop_enabled": True
    },
    {
        "id": "digital-moon-journal",
        "title": "Digital Shadow Work & Moon Journal",
        "price": 19.99,
        "currency": "USD",
        "category": "Digital Planners",
        "in_stock": True,
        "description": "Interactive GoodNotes & Notability digital planner covering all 13 lunar cycles, ritual prompts, and natal tracking.",
        "url": f"{STORE_URL}/products/digital-moon-journal",
        "tiktok_shop_enabled": False
    }
]

COMMUNITY_LINKS = {
    "official_website": STORE_URL,
    "tiktok_shop": "https://www.tiktok.com/@neurospicymystic",
    "instagram": "https://www.instagram.com/neurospicymystic",
    "youtube_sound_temple": "https://www.youtube.com/@neurospicymystic"
}

@router.get("/products")
def get_store_products():
    """Returns the official NeuroSpicy Mystic Sanctuary Store product catalog and social links."""
    return {
        "store_name": "NeuroSpicy Mystic Sanctuary Store",
        "store_url": STORE_URL,
        "community_links": COMMUNITY_LINKS,
        "products": PRODUCTS
    }

@router.post("/cart")
def add_to_cart(req: StoreCartAddRequest):
    """Adds a NeuroSpicy Mystic product to the user's shopping bag in SQLite and returns checkout link."""
    product = next((p for p in PRODUCTS if p["id"] == req.product_id), None)
    if not product:
        raise HTTPException(status_code=404, detail=f"Product '{req.product_id}' not found.")

    now = datetime.utcnow().isoformat()
    conn = get_connection()
    conn.execute(
        "INSERT INTO store_cart_items (session_id, product_id, product_title, unit_price, quantity, added_at) VALUES (?, ?, ?, ?, ?, ?)",
        (req.session_id, product["id"], product["title"], product["price"], req.quantity, now)
    )
    conn.commit()
    rows = conn.execute("SELECT * FROM store_cart_items WHERE session_id = ?", (req.session_id,)).fetchall()
    conn.close()

    total = round(sum(r["unit_price"] * r["quantity"] for r in rows), 2)
    return {
        "session_id": req.session_id,
        "added_product": product["title"],
        "item_count": sum(r["quantity"] for r in rows),
        "subtotal_usd": total,
        "checkout_url": product["url"],
        "store_url": STORE_URL
    }

@router.get("/cart/{session_id}")
def get_cart(session_id: str):
    """Retrieves the current shopping bag for a session."""
    conn = get_connection()
    rows = conn.execute("SELECT * FROM store_cart_items WHERE session_id = ? ORDER BY id DESC", (session_id,)).fetchall()
    conn.close()
    items = [
        {
            "id": r["id"],
            "product_id": r["product_id"],
            "product_title": r["product_title"],
            "unit_price": r["unit_price"],
            "quantity": r["quantity"],
            "line_total": round(r["unit_price"] * r["quantity"], 2),
            "added_at": r["added_at"]
        }
        for r in rows
    ]
    return {
        "session_id": session_id,
        "items": items,
        "subtotal_usd": round(sum(i["line_total"] for i in items), 2),
        "checkout_url": STORE_URL
    }
