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
Table: business_partners (businessPartner, customer, businessPartnerFullName, businessPartnerName, industry)
Table: business_partner_addresses (businessPartner, cityName, country, postalCode, region, streetName)
Table: sales_order_headers (salesOrder, soldToParty, creationDate, totalNetAmount, transactionCurrency)
Table: sales_order_items (salesOrder, salesOrderItem, material, requestedQuantity, requestedQuantityUnit, netAmount)
Table: outbound_delivery_headers (deliveryDocument, creationDate, shippingPoint)
Table: outbound_delivery_items (deliveryDocument, deliveryDocumentItem, plant, referenceSdDocument (this is salesOrder), referenceSdDocumentItem (this is salesOrderItem))
Table: billing_document_headers (billingDocument, creationDate, totalNetAmount, transactionCurrency, soldToParty)
Table: billing_document_items (billingDocument, billingDocumentItem, material, billingQuantity, netAmount, referenceSdDocument)
Table: journal_entry_items_accounts_receivable (companyCode, accountingDocument, referenceDocument, transactionCurrency, amountInTransactionCurrency, customer, postingDate)
Table: payments_accounts_receivable (companyCode, accountingDocument, clearingDate, clearingAccountingDocument, amountInTransactionCurrency, customer, invoiceReference, salesDocument, postingDate)
Table: products (product, productType, productGroup, baseUnit)
Table: product_descriptions (product, language, productDescription)
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
2. If the user asks about a Graph ID (e.g., 'Order_740603' or 'Delivery_80754575'):
   - Strip the prefix ('Order_', 'Delivery_', 'Customer_', etc.) to get the raw ID '740603'.
   - SAP Database IDs are typically zero-padded to 10 characters (e.g., '0000740603'). 
   - You MUST query using `LIKE '%740603'` to ensure it correctly matches the zero-padded database string without the prefix. Example: `WHERE salesOrder LIKE '%740603'`.
3. If the question violates guardrails, reply with the exact guardrail text and NO SQL.
"""


def process_chat_query(user_query: str) -> str:
    """The main pipeline for processing a user's message."""
    try:
        # Step 1: Ask AI to translate English to SQL
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
        if "This system is designed" in ai_response:
            return "This system is designed to answer questions related to the provided dataset only."
        sql_query = ai_response.split("```sql")[1].split("```")[0].strip() if "```sql" in ai_response else ai_response.replace("```", "").strip()
        print(f"Generated SQL: {sql_query}")
        db_results = execute_query(sql_query)
        if not db_results:
            results_str = "No records found matching the criteria."
        elif len(db_results) > 20:
            results_str = str(db_results[:20]) + f"\n... and {len(db_results)-20} more."
        synthesis_prompt = f"""User Question: {user_query}\nSQL Executed: {sql_query}\nRaw Database Results: {results_str}\n\nUsing ONLY the raw database results, synthesize a crisp answer."""
        
        # Route both logic and synthesis through the reliable 70B flagship model to ensure perfect stability.
        payload_2 = {"model": AI_MODEL, "messages": [{"role": "user", "content": synthesis_prompt}], "temperature": 0.3}
        
        final_resp = requests.post(GROQ_URL, headers=headers, json=payload_2)
        final_resp.raise_for_status()
        return final_resp.json()['choices'][0]['message']['content'].strip()
    except Exception as e:
        import traceback
        err_msg = traceback.format_exc()
        print(f"Error: {err_msg}")
        return f"AI Logic Error: {str(e)}"

if __name__ == "__main__":
    print(process_chat_query("Which products are in the dataset?"))
