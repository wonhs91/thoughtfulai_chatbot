from thoughtfulAI_agent import agent
from langchain_core.messages import HumanMessage
def chat_with_agent(agent):
    print("\n\nChat with your LangGraph agent. Type 'q' to quit.\n")

    while True:
        # Prompt the user for input
        user_input = input("You: ")
        
        # Exit the loop if the user types 'q'
        if user_input.strip().lower() == 'q':
            print("Exiting chat. Goodbye!")
            break
        
        try:
            # Pass the input to the agent and get the response
            state = {
                "messages": [HumanMessage(user_input)]
            }
            config = {
                "configurable": {"thread_id": 1}
            }
            response = agent.invoke(state, config=config)
            print(f"Agent: {response['messages'][-1].content}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == '__main__':
    chat_with_agent(agent)
