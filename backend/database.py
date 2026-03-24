"""
DATA LAYER (database.py)
------------------------
This file handles ALL interactions with our SQLite database. 
By keeping this separate, we ensure our API and AI layers don't get tangled with raw database code.
"""

import sqlite3
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "o2c_graph.db"

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    if not DB_PATH.exists():
        raise FileNotFoundError("Database not found. Please run ingest.py first.")
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row # This allows us to access columns by name (like dictionaries)
    return conn

def execute_query(sql_query: str):
    """Executes a raw SQL query and returns the results as a list of dictionaries."""
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute(sql_query)
        rows = cur.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()

def fetch_graph_visualization_data():
    """
    Fetches a slice of the database to be rendered as nodes and links in the frontend graph.
    We limit the data to 50 orders so the browser doesn't freeze.
    """
    conn = get_db_connection()
    cur = conn.cursor()
    
    nodes = []
    links = []
    
    try:
        # Step 1: Find the top 5 'Hub' Customers who have the most orders
        cur.execute("""
            SELECT soldToParty, COUNT(salesOrder) as c 
            FROM sales_order_headers 
            GROUP BY soldToParty 
            ORDER BY c DESC LIMIT 5
        """)
        top_customers = [r["soldToParty"] for r in cur.fetchall()]
        
        if not top_customers:
            return {"nodes": nodes, "links": links}
            
        ph_cust = ",".join("?" * len(top_customers))
        
        # Step 2: Grab up to 150 Orders belonging to these Hubs
        cur.execute(f"SELECT salesOrder, soldToParty FROM sales_order_headers WHERE soldToParty IN ({ph_cust}) LIMIT 150", top_customers)
        orders = cur.fetchall()
        
        customer_ids = set()
        for row in orders:
            order_id = str(row["salesOrder"]).lstrip('0') or '0'
            raw_cust_id = row["soldToParty"]
            customer_id = str(raw_cust_id).lstrip('0') or '0'
            customer_ids.add(raw_cust_id) # keep raw for SQL
            
            # Add Order Node
            nodes.append({"id": f"Order_{order_id}", "label": "SalesOrder", "name": f"Order {order_id}"})
            # Add Edge connecting Order -> Customer Hub
            links.append({"source": f"Order_{order_id}", "target": f"Customer_{customer_id}", "label": "Ordered By"})

        # Step 3: Get the Customers corresponding to those orders
        if customer_ids:
            placeholders = ",".join("?" * len(customer_ids))
            cur.execute(f"SELECT businessPartner, businessPartnerFullName FROM business_partners WHERE businessPartner IN ({placeholders})", list(customer_ids))
            for row in cur.fetchall():
                bp_id = str(row["businessPartner"]).lstrip('0') or '0'
                name = row["businessPartnerFullName"] or f"Customer {bp_id}"
                # Add Customer Node (Hub)
                nodes.append({"id": f"Customer_{bp_id}", "label": "Customer", "name": name})
                
        # Step 4: Get Deliveries fulfilling those orders to create outer spokes
        raw_order_ids = [r["salesOrder"] for r in orders]
        if raw_order_ids:
            ph = ",".join("?" * len(raw_order_ids))
            cur.execute(f"SELECT deliveryDocument, referenceSdDocument FROM outbound_delivery_items WHERE referenceSdDocument IN ({ph}) LIMIT 200", raw_order_ids)
            delivered = cur.fetchall()
            del_ids = set()
            for row in delivered:
                del_id = str(row["deliveryDocument"]).lstrip('0') or '0'
                ref_order = str(row["referenceSdDocument"]).lstrip('0') or '0'
                
                if del_id not in del_ids:
                    # Add Delivery Node
                    nodes.append({"id": f"Delivery_{del_id}", "label": "Delivery", "name": f"Del {del_id}"})
                    del_ids.add(del_id)
                
                # Add Edge connecting Delivery -> Order
                links.append({"source": f"Delivery_{del_id}", "target": f"Order_{ref_order}", "label": "Fulfills"})

        return {"nodes": nodes, "links": links}
    finally:
        conn.close()
