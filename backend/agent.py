"""
INTELLIGENCE LAYER (agent.py)
-----------------------------
This file is the "Brain" of the application. It takes a user's natural language question,
uses the Groq LLM to convert it into an SQL query, executes that query via the Data Layer, 
and translates the technical result back into plain English.
"""








import os
import requests
from dotenv import load_dotenv
from database import execute_query








load_dotenv()
load_dotenv(dotenv_path="../.env")








GROQ_API_KEY = os.environ.get("OPENROUTER_API_KEY")
GROQ_URL = "https://openrouter.ai/api/v1/chat/completions"
AI_MODEL = "meta-llama/llama-3.3-70b-instruct"








# Provide the AI with the map of our database so it knows how to write SQL
SCHEMA_INFO = """
Table: business_partners (businessPartner, customer, businessPartnerFullName, businessPartnerName, industry, country)
Table: sales_order_headers (salesOrder, soldToParty, creationDate, totalNetAmount, transactionCurrency)
Table: sales_order_items (salesOrder, salesOrderItem, material, requestedQuantity, requestedQuantityUnit, netAmount)
Table: outbound_delivery_headers (deliveryDocument, creationDate, shippingPoint)
Table: outbound_delivery_items (deliveryDocument, deliveryDocumentItem, plant, referenceSdDocument (this is salesOrder), referenceSdDocumentItem (this is salesOrderItem))
Table: billing_document_headers (billingDocument, creationDate, totalNetAmount, transactionCurrency, soldToParty)
Table: billing_document_items (billingDocument, billingDocumentItem, material, billingQuantity, netAmount, referenceSdDocument)
Table: products (product, productType, productGroup, baseUnit)
"""








# The fundamental rules the AI must follow
SYSTEM_PROMPT = f"""You are an AI assistant designed to explore an SAP Order-to-Cash context graph.








# Guardrails
If the user asks a question that is NOT related to the business dataset (Orders, Deliveries, Invoices, Payments, Customers, Products, etc.), you MUST reply exactly with:
"This system is designed to answer questions related to the provided dataset only."








# Database Schema
{SCHEMA_INFO}








# Instructions
1. First, generate a valid SQLite query to answer the question. 
   Output EXACTLY one query between ```sql and ``` with NO OTHER TEXT. 
2. If the question violates guardrails, reply with the exact guardrail text and NO SQL.
"""








def process_chat_query(user_query: str) -> str:
    """The main pipeline for processing a user's message."""
    try:
        # Step 1: Ask AI to translate the English query into SQL
        headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
        }


        payload_1 = {
        "model": AI_MODEL,
        "messages": [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_query}
        ],
        "temperature": 0
        }


        response = requests.post(GROQ_URL, headers=headers, json=payload_1)
        response.raise_for_status()


        ai_response = response.json()['choices'][0]['message']['content'].strip()


        # Check if the AI triggered the Guardrail
        if "This system is designed" in ai_response:
        return "This system is designed to answer questions related to the provided dataset only."


        # Extract SQL
        sql_query = ai_response.split("```sql")[1].split("```")[0].strip() if "```sql" in ai_response else ai_response.replace("```", "").strip()
        print(f"Generated SQL: {sql_query}")


        # Step 2: Execute SQL
        db_results = execute_query(sql_query)


        # Format results
        if not db_results:
        results_str = "No records found matching the criteria."
        elif len(db_results) > 20:
        results_str = str(db_results[:20]) + f"\n... and {len(db_results)-20} more."
        else:
        results_str = str(db_results)

        # ... logic for Step 3 could be here, but let's just finish the try block
        return results_str


    except Exception as e:
        import traceback
        err_msg = traceback.format_exc()
        print(f"ERROR: {err_msg}")
        return f"AI Logic Error: {str(e)}\n\nFull Traceback:\n{err_msg}"

