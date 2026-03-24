"""
INTELLIGENCE LAYER (agent.py)
-----------------------------
This file is the "Brain" of the application. It takes a user's natural language question,
uses the Groq LLM to convert it into an SQL query, executes that query via the Data Layer, 
and translates the technical result back into plain English.
"""

import os
from dotenv import load_dotenv
from groq import Groq
from database import execute_query

# Robustly try to load .env from current or parent directory
load_dotenv()  
load_dotenv(dotenv_path="../.env")

# Load the key from environment variables (or .env if running locally with dotenv)
groq_key = os.environ.get("GROQ_API_KEY")

# Initialize the Groq AI client
client = Groq(api_key=groq_key)
AI_MODEL = "llama-3.3-70b-versatile"

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
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_query}
            ],
            model=AI_MODEL,
            temperature=0,      # Give us exact, deterministic SQL (no creativity needed here)
            max_tokens=500
        )
        ai_response = response.choices[0].message.content.strip()
        
        # Check if the AI triggered the Guardrail (meaning the topic was irrelevant)
        if "This system is designed" in ai_response:
            return "This system is designed to answer questions related to the provided dataset only."
            
        # Extract the pure SQL code from the AI's response
        sql_query = ai_response.split("```sql")[1].split("```")[0].strip() if "```sql" in ai_response else ai_response.replace("```", "").strip()
        print("Generated SQL:", sql_query)
        
        # Step 2: Execute the SQL against our Data Layer
        db_results = execute_query(sql_query)
        
        # Format results nicely to avoid overwhelming the AI with huge data chunks
        if not db_results:
            results_str = "No records found matching the criteria."
        elif len(db_results) > 20: 
            results_str = str(db_results[:20]) + f"\n... and {len(db_results)-20} more."
        else:
            results_str = str(db_results)
        
        # Step 3: Pass the raw SQL results back to the AI to synthesize a human-friendly answer
        synthesis_prompt = f"""
        User Question: {user_query}
        SQL Executed: {sql_query}
        Raw Database Results: {results_str}
        
        Using ONLY the raw database results, synthesize a crisp, highly professional answer resolving the user's core question. State exact figures if present in the results. Do not mention SQLite or SQL directly unless the user asks for it. Structure the response nicely in Markdown.
        """
        
        final_answer = client.chat.completions.create(
            messages=[{"role": "user", "content": synthesis_prompt}],
            model=AI_MODEL,
            temperature=0.3    # Slightly higher temperature for natural sounding text
        )
        
        return final_answer.choices[0].message.content.strip()
        
    except Exception as e:
        print("Error in process_chat_query:", e)
        return f"Sorry, I encountered an error. Detail: {str(e)}"
