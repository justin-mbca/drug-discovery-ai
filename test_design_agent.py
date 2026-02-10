"""Quick test of DesignAgent functionality"""

if __name__ == "__main__":
    print("Importing DesignAgent...")
    from agents.design_agent.agent import DesignAgent
    
    print("Creating agent instance...")
    agent = DesignAgent()
    
    print("Running agent analysis...")
    agent.run()
    
    print("Agent memory:", agent.memory)
    
    print("Saving memory...")
    agent.save_memory()
    
    print("✓ Test completed successfully!")
