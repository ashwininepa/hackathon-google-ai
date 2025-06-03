from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain.chains import RetrievalQA
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate

# Load environment variables from .env file
# load_dotenv()
GOOGLE_API_KEY="AIzaSyCSEP886to23PwHtoaTtFEuwgHEvSECrLQ"

# --- Configuration ---
VECTOR_STORE_PATH = "./chroma_db"

# --- Initialize Clients ---
# Same embeddings as used for creating the vector store
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={'device': 'cpu'},
    encode_kwargs={'normalize_embeddings': True}
)

# Initialize LLM (using Google's Gemini - free tier available)
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=GOOGLE_API_KEY,
    temperature=0.3
)

class CustomerSupportBot:
    def __init__(self):
        """Initialize the customer support bot with vector store and LLM."""
        # Load existing vector store
        self.vectorstore = Chroma(
            persist_directory=VECTOR_STORE_PATH,
            embedding_function=embeddings
        )
        
        # Create retriever
        self.retriever = self.vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 3}  # Retrieve top 3 most similar documents
        )
        
        # Define category-specific response templates - Updated to match your categories
        self.category_templates = {
            "Order_Management_Cancellation": """
            Based on the customer's cancellation request, provide helpful cancellation support:
            1. Acknowledge their request
            2. Provide clear cancellation steps
            3. Mention any important policies or deadlines
            4. Offer alternatives if appropriate
            """,
            "Returns_Exchanges": """
            Based on the customer's refund/return/exchange request, provide helpful support:
            1. Acknowledge their request
            2. Explain the return/refund/exchange process
            3. Mention timeframes and requirements
            4. Provide next steps
            """,
            "Shipping_Delivery": """
            Based on the customer's shipping/delivery inquiry, provide helpful support:
            1. Acknowledge their concern
            2. Provide tracking information or shipping updates
            3. Explain delivery processes
            4. Offer solutions for shipping issues
            """,
            "Product_Service_Issues": """
            Based on the customer's product/service issue, provide helpful technical support:
            1. Acknowledge the problem
            2. Provide troubleshooting steps
            3. Offer additional resources
            4. Suggest escalation if needed
            """,
            "Other_General": """
            Based on the customer's general inquiry, provide helpful support:
            1. Acknowledge their question
            2. Provide relevant information
            3. Offer additional resources
            4. Suggest next steps if needed
            """
        }
        
        # Create prompt template - Fixed the input variables to match RetrievalQA expectations
        self.prompt_template = PromptTemplate(
            input_variables=["context", "question"],  # Changed "query" to "question"
            template="""
            You are a helpful customer support assistant. Use the following context from previous customer interactions to help answer the customer's question.

            Context from similar customer interactions:
            {context}

            Customer Question: {question}

            Please provide a helpful, professional, and empathetic response that:
            - Directly addresses the customer's concern
            - Uses information from the context when relevant
            - Is clear and actionable
            - Maintains a friendly and professional tone

            Response:
            """
        )
        
        # Create QA chain - Fixed the chain setup
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=self.retriever,
            chain_type_kwargs={"prompt": self.prompt_template}
        )
    
    def classify_query_category(self, query: str) -> str:
        """Classify the customer query into a category based on keywords."""
        query_lower = query.lower()
        
        # Define keyword mappings for categories
        category_keywords = {
            "Order_Management_Cancellation": ["cancel", "cancel_request", "proforma_invoice", "cancellation", "terminate", "end", "stop", "discontinue"],
            "Returns_Exchanges": ["exchange", "how_to_return", "no_proof", "proof_complaint", "receipt", "return", "returns", "money back", "reimburse", "refund"],
            "Shipping_Delivery": ["fw_shipping_process", "missing", "shipping", "status_shipping", "wrong_address", "delivery", "shipment", "tracking", "lost package", "package"],
            "Product_Service_Issues": ["complaint", "price", "price_match", "product", "wrong_product", "not working", "broken", "error", "bug", "technical", "issue", "problem", "fix", "defective", "quality"],
            "Other_General": ["3f2", "discount_code", "other", "status_return", "unclear_c_request", "unsubscribe", "general", "help", "question", "inquiry", "password", "reset", "login"]
        }
        
        # Check for category keywords
        for category, keywords in category_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                return category
        
        return "Other_General"
    
    def get_response(self, customer_query: str) -> dict:
        """Get a response for the customer query."""
        try:
            # Classify the query
            category = self.classify_query_category(customer_query)
            print(f"Debug: Classified category: {category}")
            
            # Get category-specific guidance
            category_guidance = self.category_templates.get(category, self.category_templates["Other_General"])
            
            # Retrieve similar documents
            relevant_docs = self.retriever.get_relevant_documents(customer_query)
            print(f"Debug: Found {len(relevant_docs)} relevant documents")
            
            # Generate response using the QA chain - Fixed the parameter passing
            response = self.qa_chain.run(customer_query)
            
            return {
                "response": response,
                "category": category,
                "confidence": "high" if relevant_docs else "low",
                "relevant_docs_count": len(relevant_docs)
            }
            
        except Exception as e:
            print(f"Debug: Error occurred: {str(e)}")
            return {
                "response": "I apologize, but I'm having trouble processing your request right now. Please try again or contact our support team directly.",
                "category": "ERROR",
                "error": str(e)
            }

def main():
    """Test the customer support bot."""
    try:
        bot = CustomerSupportBot()
        print("Bot initialized successfully!")
        
        # Test queries
        test_queries = [
            "I want to cancel my subscription",
            "I need a refund for my last purchase", 
            "The app is not working properly",
            "Where is my package?",
            "How do I reset my password?"
        ]
        
        print("Customer Support Bot Test\n" + "="*50)
        
        for query in test_queries:
            print(f"\nCustomer Query: {query}")
            result = bot.get_response(query)
            print(f"Category: {result['category']}")
            print(f"Response: {result['response']}")
            print("-" * 50)
            
    except Exception as e:
        print(f"Error initializing bot: {str(e)}")

if __name__ == "__main__":
    main()