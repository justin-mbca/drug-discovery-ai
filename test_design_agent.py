from agents.design_agent.agent import DesignAgent

if __name__ == "__main__":
    agent = DesignAgent()
    agent.run()
    print("Memory:", agent.memory)
    agent.save_memory()