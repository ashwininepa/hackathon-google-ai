from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from src.customer_support_bot import CustomerSupportBot

app = FastAPI(title="Customer Support Bot API", version="1.0.0")

# Initialize the bot
bot = CustomerSupportBot()

# Pydantic model for request body
class ChatRequest(BaseModel):
    message: str

# Pydantic model for response
class ChatResponse(BaseModel):
    response: str
    category: str
    confidence: str
    relevant_docs_count: int
    error: str = None

@app.get("/", response_class=HTMLResponse)
async def home():
    """Serve the chat interface"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Customer Support Bot</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .chat-container { border: 1px solid #ccc; height: 400px; overflow-y: scroll; padding: 10px; margin-bottom: 10px; }
            .message { margin: 10px 0; padding: 10px; border-radius: 5px; }
            .user { background-color: #e3f2fd; text-align: right; }
            .bot { background-color: #f5f5f5; }
            .category { font-size: 0.8em; color: #666; font-style: italic; }
            input[type="text"] { width: 70%; padding: 10px; }
            button { padding: 10px 20px; margin-left: 10px; }
            .loading { color: #666; font-style: italic; }
        </style>
    </head>
    <body>
        <h1>Customer Support Bot</h1>
        <div id="chat-container" class="chat-container"></div>
        <div>
            <input type="text" id="user-input" placeholder="Type your question here..." onkeypress="if(event.key==='Enter') sendMessage()">
            <button onclick="sendMessage()">Send</button>
        </div>

        <script>
            async function sendMessage() {
                const input = document.getElementById('user-input');
                const message = input.value.trim();
                if (!message) return;

                // Display user message
                addMessage(message, 'user');
                input.value = '';
                
                // Show loading message
                addMessage('Thinking...', 'bot', null, 'loading');

                try {
                    // Send to bot
                    const response = await fetch('/chat', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({message: message})
                    });
                    
                    const data = await response.json();
                    
                    // Remove loading message
                    const container = document.getElementById('chat-container');
                    const lastMessage = container.lastElementChild;
                    if (lastMessage && lastMessage.classList.contains('loading')) {
                        container.removeChild(lastMessage);
                    }
                    
                    if (response.ok) {
                        addMessage(data.response, 'bot', data.category);
                    } else {
                        addMessage(data.detail || 'Sorry, there was an error processing your request.', 'bot');
                    }
                } catch (error) {
                    // Remove loading message
                    const container = document.getElementById('chat-container');
                    const lastMessage = container.lastElementChild;
                    if (lastMessage && lastMessage.classList.contains('loading')) {
                        container.removeChild(lastMessage);
                    }
                    
                    addMessage('Sorry, there was an error processing your request.', 'bot');
                }
            }

            function addMessage(text, sender, category = null, className = null) {
                const container = document.getElementById('chat-container');
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${sender}`;
                
                if (className) {
                    messageDiv.classList.add(className);
                }
                
                let content = text;
                if (category) {
                    content = `<div class="category">Category: ${category}</div>${text}`;
                }
                
                messageDiv.innerHTML = content;
                container.appendChild(messageDiv);
                container.scrollTop = container.scrollHeight;
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Handle chat requests"""
    if not request.message:
        raise HTTPException(status_code=400, detail="No message provided")
    
    try:
        response = bot.get_response(request.message)
        return ChatResponse(**response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Customer Support Bot API is running"}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)