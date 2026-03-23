"""
DATA LAYER (database.py)
------------------------
This file handles ALL interactions with our SQLite database. 
By keeping this separate, we ensure our API and AI layers don't get tangled with raw database code.
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(r"C:\Users\INDRAKUMAR\Desktop\FDE Task\backend\o2c_graph.db")

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
        # Step 1: Get 50 Sales Orders
        cur.execute("SELECT salesOrder, soldToParty FROM sales_order_headers LIMIT 50")
        orders = cur.fetchall()
        
        customer_ids = set()
        for row in orders:
            order_id = row["salesOrder"]
            customer_id = row["soldToParty"]
            customer_ids.add(customer_id)
            
            # Add Order Node
            nodes.append({"id": f"Order_{order_id}", "label": "SalesOrder", "name": f"Order {order_id}"})
            # Add Edge connecting Order -> Customer
            links.append({"source": f"Order_{order_id}", "target": f"Customer_{customer_id}", "label": "Ordered By"})

        # Step 2: Get the Customers corresponding to those orders
        if customer_ids:
            placeholders = ",".join("?" * len(customer_ids))
            cur.execute(f"SELECT businessPartner, businessPartnerName FROM business_partners WHERE businessPartner IN ({placeholders})", list(customer_ids))
            for row in cur.fetchall():
                bp_id = row["businessPartner"]
                name = row["businessPartnerName"] or bp_id
                # Add Customer Node
                nodes.append({"id": f"Customer_{bp_id}", "label": "Customer", "name": name})
                
        # Step 3: Get Deliveries fulfilling those orders
        order_ids = [r["salesOrder"] for r in orders]
        if order_ids:
            ph = ",".join("?" * len(order_ids))
            cur.execute(f"SELECT deliveryDocument, referenceSdDocument FROM outbound_delivery_items WHERE referenceSdDocument IN ({ph}) LIMIT 100", order_ids)
            delivered = cur.fetchall()
            del_ids = set()
            for row in delivered:
                del_id = row["deliveryDocument"]
                ref_order = row["referenceSdDocument"]
                
                if del_id not in del_ids:
                    # Add Delivery Node
                    nodes.append({"id": f"Delivery_{del_id}", "label": "Delivery", "name": f"Del {del_id}"})
                    del_ids.add(del_id)
                
                # Add Edge connecting Delivery -> Order
                links.append({"source": f"Delivery_{del_id}", "target": f"Order_{ref_order}", "label": "Fulfills"})

        return {"nodes": nodes, "links": links}
    finally:
        conn.close()
