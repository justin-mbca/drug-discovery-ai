"""
DesignAgent: Lightweight drug candidate analysis without heavy dependencies
- Fast initialization (no ML library imports at startup)
- Memory tracking for compound analysis
- Lazy-loading of external tools on demand
"""

import json
import os
from typing import Dict, List, Optional


class DesignAgent:
    """Lightweight DesignAgent for fast initialization and testing"""
    
    def __init__(self, use_tools: bool = False):
        """
        Initialize DesignAgent
        
        Args:
            use_tools: If True, lazily load external tools when needed
        """
        self.use_tools = use_tools
        self._tools_loaded = False
        self.pubchem = None
        self.docking = None
        self.qsar = None
        
        # Memory system
        self.memory_file = os.path.join(os.path.dirname(__file__), "memory.json")
        self.memory = {
            "successes": [],
            "failures": [],
            "analyzed": [],
            "generation_count": 0
        }
        self.load_memory()

    def load_memory(self):
        """Load memory from disk if it exists"""
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, 'r') as f:
                    loaded = json.load(f)
                    # Ensure all required keys exist
                    self.memory = {
                        "successes": loaded.get("successes", []),
                        "failures": loaded.get("failures", []),
                        "analyzed": loaded.get("analyzed", []),
                        "generation_count": loaded.get("generation_count", 0)
                    }
            except Exception as e:
                print(f"Could not load memory: {e}")
                self._init_memory()
        else:
            self._init_memory()

    def _init_memory(self):
        """Initialize empty memory structure"""
        self.memory = {
            "successes": [],
            "failures": [],
            "analyzed": [],
            "generation_count": 0
        }

    def save_memory(self):
        """Save memory to disk"""
        try:
            os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
            with open(self.memory_file, 'w') as f:
                json.dump(self.memory, f, indent=2)
            print(f"✓ Memory saved to {self.memory_file}")
        except Exception as e:
            print(f"✗ Error saving memory: {e}")

    def _lazy_load_tools(self):
        """Lazy-load tools only when needed (not on initialization)"""
        if self._tools_loaded or not self.use_tools:
            return
        
        try:
            from tools.pubchem import PubChemTool
            from tools.docking import DockingTool
            from tools.qsar import QSARTool
            
            self.pubchem = PubChemTool()
            self.docking = DockingTool()
            self.qsar = QSARTool()
            self._tools_loaded = True
            print("✓ External tools loaded successfully")
        except Exception as e:
            print(f"⚠ Warning: Could not load tools: {e}")
            self._tools_loaded = True  # Don't retry

    def generate_molecule(self, target: Optional[str] = None) -> Optional[str]:
        """
        Generate a molecule SMILES string
        
        Args:
            target: Optional target protein name for guided generation
            
        Returns:
            SMILES string or None if generation fails
        """
        # Placeholder: would connect to actual generative model
        self.memory["generation_count"] = self.memory.get("generation_count", 0) + 1
        return None

    def run(self, compound: Optional[str] = None, 
            compounds_for_target: Optional[List[Dict]] = None):
        """
        Analyze compound(s)
        
        Args:
            compound: Single compound name/SMILES
            compounds_for_target: List of compounds from target lookup
            
        Returns:
            Analysis results dictionary
        """
        # Handle batch analysis
        if compounds_for_target and isinstance(compounds_for_target, list):
            return self._analyze_batch(compounds_for_target)
        
        # Handle single compound
        if compound:
            result = self._analyze_single(compound)
            self.memory["analyzed"].append(result)
            return result
        
        return {"status": "no compound provided", "success": False}

    def _analyze_batch(self, compounds: List[Dict]) -> Dict:
        """Analyze multiple compounds"""
        if not compounds:
            return {"analyzed_compounds": [], "total": 0}
        
        results = []
        for c in compounds:
            cid = c.get("cid")
            name = c.get("iupac_name", c.get("name", str(cid)))
            
            analysis = self._analyze_single(name, cid)
            results.append(analysis)
            self.memory["analyzed"].append(analysis)
        
        return {
            "analyzed_compounds": results,
            "total": len(results),
            "success": True
        }

    def _analyze_single(self, compound: str, cid: Optional[str] = None) -> Dict:
        """
        Analyze a single compound
        
        Args:
            compound: Compound name or SMILES
            cid: Optional PubChem CID
            
        Returns:
            Analysis result dictionary
        """
        result = {
            "compound": compound,
            "cid": cid,
            "timestamp": self._get_timestamp(),
            "analysis": {
                "pubchem_data": None,
                "docking_score": None,
                "qsar_prediction": None
            },
            "status": "pending"
        }
        
        try:
            # Lazy load tools if needed
            if self.use_tools:
                self._lazy_load_tools()
            
            # Try to get compound info
            if self.pubchem:
                result["analysis"]["pubchem_data"] = self.pubchem.run(compound=compound)
            
            # Try molecular docking
            if self.docking:
                result["analysis"]["docking_score"] = self.docking.screen(compound)
            
            # Try QSAR prediction
            if self.qsar:
                result["analysis"]["qsar_prediction"] = self.qsar.predict(compound)
            
            result["status"] = "completed"
            
        except Exception as e:
            result["status"] = "error"
            result["error"] = str(e)
            print(f"⚠ Error analyzing {compound}: {e}")
        
        return result

    @staticmethod
    def _get_timestamp() -> str:
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().isoformat()

    def log_success(self, compound: str, score: float = 0.0):
        """Log a successful compound"""
        self.memory["successes"].append({
            "compound": compound,
            "score": score,
            "timestamp": self._get_timestamp()
        })

    def log_failure(self, compound: str, reason: str = ""):
        """Log a failed compound"""
        self.memory["failures"].append({
            "compound": compound,
            "reason": reason,
            "timestamp": self._get_timestamp()
        })

    def get_stats(self) -> Dict:
        """Get analysis statistics"""
        return {
            "total_analyzed": len(self.memory["analyzed"]),
            "total_successes": len(self.memory["successes"]),
            "total_failures": len(self.memory["failures"]),
            "generation_attempts": self.memory.get("generation_count", 0)
        }

    def get_successful_compounds(self) -> List[Dict]:
        """Get list of all successful compounds"""
        return self.memory.get("successes", [])

    def get_failed_compounds(self) -> List[Dict]:
        """Get list of all failed compounds"""
        return self.memory.get("failures", [])

    def clear_memory(self):
        """Clear all memory data"""
        self._init_memory()
        print("✓ Memory cleared")

    def search_compound(self, compound_name: str) -> Optional[Dict]:
        """Search for a compound in analyzed history
        
        Args:
            compound_name: Name or SMILES to search for
            
        Returns:
            Analysis dict if found, None otherwise
        """
        for analysis in self.memory.get("analyzed", []):
            if analysis["compound"].lower() == compound_name.lower():
                return analysis
        return None

    def filter_by_status(self, status: str) -> List[Dict]:
        """Filter analyzed compounds by status
        
        Args:
            status: 'completed', 'error', 'pending'
            
        Returns:
            List of analyses with matching status
        """
        return [a for a in self.memory.get("analyzed", []) if a["status"] == status]

    def get_top_successes(self, n: int = 5) -> List[Dict]:
        """Get top N successful compounds by score
        
        Args:
            n: Number of top compounds to return
            
        Returns:
            List of successful compounds sorted by score
        """
        successes = self.memory.get("successes", [])
        sorted_successes = sorted(successes, key=lambda x: x.get("score", 0), reverse=True)
        return sorted_successes[:n]

    def export_memory(self, filepath: str) -> bool:
        """Export memory to a custom location
        
        Args:
            filepath: Path to export memory to
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(filepath, 'w') as f:
                json.dump(self.memory, f, indent=2)
            print(f"✓ Memory exported to {filepath}")
            return True
        except Exception as e:
            print(f"✗ Error exporting memory: {e}")
            return False

    def import_memory(self, filepath: str) -> bool:
        """Import memory from a file
        
        Args:
            filepath: Path to import memory from
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(filepath, 'r') as f:
                self.memory = json.load(f)
            print(f"✓ Memory imported from {filepath}")
            return True
        except Exception as e:
            print(f"✗ Error importing memory: {e}")
            return False

    def get_analysis_summary(self) -> Dict:
        """Get comprehensive analysis summary
        
        Returns:
            Dict with detailed statistics and summaries
        """
        stats = self.get_stats()
        successes = self.get_successful_compounds()
        failures = self.get_failed_compounds()
        
        # Calculate success rate
        total = stats["total_successes"] + stats["total_failures"]
        success_rate = stats["total_successes"] / total if total > 0 else 0
        
        # Get average success score
        avg_score = 0
        if successes:
            scores = [s.get("score", 0) for s in successes]
            avg_score = sum(scores) / len(scores)
        
        return {
            "stats": stats,
            "success_rate": success_rate,
            "average_success_score": avg_score,
            "top_successes": self.get_top_successes(3),
            "failure_reasons": self._get_failure_reasons(),
            "timestamp": self._get_timestamp()
        }

    def _get_failure_reasons(self) -> Dict[str, int]:
        """Analyze failure reasons
        
        Returns:
            Dict mapping reason to count
        """
        reasons = {}
        for failure in self.memory.get("failures", []):
            reason = failure.get("reason", "unknown")
            reasons[reason] = reasons.get(reason, 0) + 1
        return reasons

    def print_summary(self):
        """Print formatted analysis summary to console"""
        summary = self.get_analysis_summary()
        
        print("\n" + "=" * 60)
        print("DESIGN AGENT ANALYSIS SUMMARY")
        print("=" * 60)
        
        stats = summary["stats"]
        print(f"\n📊 Statistics:")
        print(f"   Total Analyzed:  {stats['total_analyzed']}")
        print(f"   Successes:       {stats['total_successes']}")
        print(f"   Failures:        {stats['total_failures']}")
        print(f"   Generation Attempts: {stats['generation_attempts']}")
        
        print(f"\n📈 Performance:")
        print(f"   Success Rate:    {summary['success_rate']:.1%}")
        print(f"   Avg Score:       {summary['average_success_score']:.2f}")
        
        if summary["top_successes"]:
            print(f"\n🏆 Top Successes:")
            for i, compound in enumerate(summary["top_successes"], 1):
                print(f"   {i}. {compound['compound']} (score: {compound.get('score', 0):.2f})")
        
        if summary["failure_reasons"]:
            print(f"\n❌ Failure Reasons:")
            for reason, count in summary["failure_reasons"].items():
                print(f"   {reason}: {count}")
        
        print("\n" + "=" * 60 + "\n")


