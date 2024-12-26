# %%
from langchain_ollama import ChatOllama
from langchain_groq import ChatGroq
from typing import TypedDict, Annotated, List
from langchain_core.messages import AnyMessage, HumanMessage, SystemMessage, RemoveMessage, AIMessage
from langgraph.graph import add_messages, START, END, StateGraph
from langgraph.prebuilt import tools_condition, ToolNode
from langgraph.checkpoint.memory import MemorySaver
from dotenv import load_dotenv

load_dotenv()
# Tool
def get_thoughtai_knowledge(search_query: str):
    """
    Searches and retrieves information about Thoughtful AI's products, services, and capabilities from an authorized knowledge base.
    Returns relevant, accurate information matching the search query.

    Args:
        search_query: query string to search
    """
    predefined_data = """
{
    "questions": [
        {
            "question": "What does the eligibility verification agent (EVA) do?",
            "answer": "EVA automates the process of verifying a patient’s eligibility and benefits information in real-time, eliminating manual data entry errors and reducing claim rejections."
        },
        {
            "question": "What does the claims processing agent (CAM) do?",
            "answer": "CAM streamlines the submission and management of claims, improving accuracy, reducing manual intervention, and accelerating reimbursements."
        },
        {
            "question": "How does the payment posting agent (PHIL) work?",
            "answer": "PHIL automates the posting of payments to patient accounts, ensuring fast, accurate reconciliation of payments and reducing administrative burden."
        },
        {
            "question": "Tell me about Thoughtful AI's Agents.",
            "answer": "Thoughtful AI provides a suite of AI-powered automation agents designed to streamline healthcare processes. These include Eligibility Verification (EVA), Claims Processing (CAM), and Payment Posting (PHIL), among others."
        },
        {
            "question": "What are the benefits of using Thoughtful AI's agents?",
            "answer": "Using Thoughtful AI's Agents can significantly reduce administrative costs, improve operational efficiency, and reduce errors in critical processes like claims management and payment posting."
        }
    ]
}
    """
    return predefined_data

# llm = ChatOllama(model="llama3.2")
llm = ChatGroq(model_name="llama-3.3-70b-versatile")

tools = [get_thoughtai_knowledge]

llm_with_knowledge = llm.bind_tools(tools)

# Define state
class State(TypedDict):
    messages: Annotated[List[AnyMessage], add_messages]
    summary: str
    

# Define Nodes
def chatbot(state):
    sys_msg = """
You are an AI Customer Support Assistant for Thoughtful AI, a company that specializes in AI agent solutions. Your primary role is to provide accurate, helpful information about Thoughtful AI's products and services while maintaining a professional and friendly demeanor.

Tool Usage:
1. You have access to a tool called "get_thoughtai_knowledge" that can search for specific information about Thoughtful AI's products and services.
    Thoughtful AI's Product Knowledge Scope:
    - EVA (Eligibility Verification Agent)
    - CAM (Claims Processing Agent)
    - PHIL (Payment Posting Agent)
    - General benefits of Thoughtful AI's automation solutions
    - Basic overview of Thoughtful AI's service offerings
2. When a user asks a question about Thoughtful AI's products or services:
   - First, formulate a clear, specific search query based on the user's question
   - Call get_thoughtai_knowledge with this query
   - Use the returned information to construct your response
3. If the tool returns no results or insufficient information, acknowledge this and offer to help with related topics you can address.

Search Query Guidelines:
1. Keep search queries focused and specific
2. Use key terms from the user's question
3. Remove unnecessary words and context
4. Prioritize product names and specific features in queries

Example Tool Usage:
User: "How does EVA handle insurance verification?"
Action: Call get_thoughtai_knowledge("EVA eligibility verification process")
Response: Use returned information to explain EVA's capabilities

Core Behaviors:
1. You should communicate in a clear, professional, yet approachable manner.
2. Your responses should be concise and directly address the user's questions without unnecessary elaboration.
3. When providing information about Thoughtful AI's products, prioritize accuracy over comprehensiveness.

Response Structure:
1. Begin each response by acknowledging the user's question.
2. If needed, call get_thoughtai_knowledge to retrieve relevant information.
3. Provide the retrieved information in a clear, structured manner.
4. If clarification is needed, ask focused follow-up questions.
5. End responses with an offer to help with any additional questions when appropriate.

Error Handling:
1. If get_thoughtai_knowledge returns no results, acknowledge this honestly.
2. When the tool returns partial information, use what's available and acknowledge any gaps.
3. If a user's question is unclear, request clarification before making a tool call.

Conversational Guidelines:
1. Maintain a helpful, professional tone
2. Use clear, concise language
3. Avoid technical jargon unless specifically requested
4. Stay focused on Thoughtful AI's healthcare automation solutions
5. Be patient with repeated or similar questions

Remember that your primary goal is to provide accurate, helpful information about Thoughtful AI's products while maintaining a professional and supportive interaction with users. Always use the get_thoughtai_knowledge tool to ensure accuracy in your responses about Thoughtful AI's products and services.
    """
    messages = [SystemMessage(content=sys_msg)]
    summary = state.get("summary", "")
    if summary:
        summary_message = f"Summary of conversation earlier: {summary}"
        messages = messages + [AIMessage(content=summary_message)]

    response = llm_with_knowledge.invoke(messages + state["messages"])
    
    return {
        "messages": response
    }
    
def summarybot(state):
        
    messages = state["messages"]
    
    # If there are more than six messages, then we summarize the conversation
    if len(messages) < 6:
        return {}
    
    # First, we get any existing summary
    summary = state.get("summary", "")

    # Create our summarization prompt 
    if summary:
        
        # A summary already exists
        summary_message = (
            f"This is summary of the conversation to date: {summary}\n\n"
            "Extend the summary by taking into account the new messages above:"
        )
        
    else:
        summary_message = "Create a summary of the conversation above:"
        
    response = llm.invoke(state["messages"] + [HumanMessage(content=summary_message)])
    
    delete_messages = [RemoveMessage(id=m.id) for m in state["messages"][:-2]]
    return {
        "messages": delete_messages,
        "summary": response.content
    }


# Build Graph
builder = StateGraph(State)
builder.add_node(chatbot)
builder.add_node(ToolNode(tools))
builder.add_node(summarybot)

builder.add_edge(START, "chatbot")
builder.add_conditional_edges("chatbot", tools_condition, {"tools": "tools", "__end__": "summarybot"})
builder.add_edge("tools", "chatbot")
builder.add_edge("summarybot", END)


memory = MemorySaver()

agent = builder.compile(checkpointer=memory)
