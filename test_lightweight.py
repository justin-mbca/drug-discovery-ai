#!/usr/bin/env python3
"""Ultra-lightweight test to identify hang source"""

print("1. Starting test...")

try:
    print("2. Importing os...")
    import os
    print("3. Importing json...")
    import json
    print("4. Importing typing...")
    from typing import Dict, List, Optional
    print("5. Imports complete - no hang yet")
    
    print("6. Attempting to import DesignAgent...")
    from agents.design_agent.agent import DesignAgent
    print("7. DesignAgent imported successfully!")
    
    print("8. Creating agent...")
    agent = DesignAgent()
    print("9. Agent created successfully!")
    print(f"10. Agent memory: {agent.memory}")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
