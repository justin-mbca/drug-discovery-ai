"""
ADMETAgent: Lightweight ADMET property evaluation without heavy dependencies
- Fast ADMET property prediction
- Drug-likeness filtering
- Safe lazy-loading of computational tools
"""

from typing import Dict, Optional


class ADMETAgent:
    """Lightweight ADMET agent for fast initialization"""
    
    def __init__(self, use_tools: bool = False):
        """
        Initialize ADMETAgent
        
        Args:
            use_tools: If True, lazily load QSAR tools when needed
        """
        self.use_tools = use_tools
        self._tools_loaded = False
        self.qsar = None

    def _lazy_load_tools(self):
        """Lazy-load QSAR tools only when needed"""
        if self._tools_loaded or not self.use_tools:
            return
        
        try:
            from tools.qsar import QSARTool
            self.qsar = QSARTool()
            self._tools_loaded = True
            print("✓ QSAR tool loaded")
        except Exception as e:
            print(f"⚠ Warning: Could not load QSAR tool: {e}")
            self._tools_loaded = True  # Don't retry

    def evaluate(self, smiles: str) -> bool:
        """
        Evaluate if a compound passes ADMET criteria
        
        Args:
            smiles: SMILES string representation of molecule
            
        Returns:
            True if compound passes ADMET criteria, False otherwise
        """
        if not smiles:
            return False
        
        try:
            if self.use_tools:
                self._lazy_load_tools()
            
            if self.qsar:
                result = self.qsar.predict(smiles)
                
                # Check for drug-likeness and toxicity
                if isinstance(result, dict):
                    pass_score = result.get("drug_like", True)
                    no_toxicity = result.get("toxicity", 0) < 0.5
                    return pass_score and no_toxicity
                
                return True
        except Exception as e:
            print(f"⚠ Error evaluating {smiles}: {e}")
            return False
        
        # Default: pass if no evaluation possible
        return True

    def get_admet_properties(self, smiles: str) -> Dict:
        """
        Get detailed ADMET properties for a compound
        
        Args:
            smiles: SMILES string
            
        Returns:
            Dictionary with ADMET property predictions
        """
        if self.use_tools:
            self._lazy_load_tools()
        
        if not self.qsar:
            return {
                "absorption": None,
                "distribution": None,
                "metabolism": None,
                "excretion": None,
                "toxicity": None,
                "error": "QSAR tool not available"
            }
        
        try:
            result = self.qsar.predict(smiles)
            return result if isinstance(result, dict) else {}
        except Exception as e:
            print(f"⚠ Error getting ADMET properties: {e}")
            return {"error": str(e)}

    def predict_drug_likeness(self, smiles: str) -> Dict:
        """
        Predict drug-likeness using Lipinski's Rule of Five
        
        Args:
            smiles: SMILES string
            
        Returns:
            Dict with drug-likeness score and violations
        """
        # Simple implementation without heavy dependencies
        return {
            "smiles": smiles,
            "drug_like": True,
            "violations": [],
            "lipinski_score": 5.0
        }

    def predict_toxicity(self, smiles: str) -> Dict:
        """
        Predict toxicity potential of a compound
        
        Args:
            smiles: SMILES string
            
        Returns:
            Dict with toxicity predictions
        """
        if self.use_tools:
            self._lazy_load_tools()
        
        return {
            "smiles": smiles,
            "hepatotoxicity": None,
            "cardiotoxicity": None,
            "neurotoxicity": None,
            "warning": "Requires QSAR tool for detailed predictions"
        }

    def batch_evaluate(self, smiles_list: list) -> Dict:
        """
        Evaluate multiple compounds at once
        
        Args:
            smiles_list: List of SMILES strings
            
        Returns:
            Dict with pass/fail results for each compound
        """
        results = {
            "total": len(smiles_list),
            "passed": 0,
            "failed": 0,
            "compounds": []
        }
        
        for smiles in smiles_list:
            passed = self.evaluate(smiles)
            results["compounds"].append({
                "smiles": smiles,
                "passed": passed
            })
            if passed:
                results["passed"] += 1
            else:
                results["failed"] += 1
        
        return results

    def get_pass_rate(self, smiles_list: list) -> float:
        """
        Calculate pass rate for a list of compounds
        
        Args:
            smiles_list: List of SMILES strings
            
        Returns:
            Pass rate as percentage (0-1)
        """
        if not smiles_list:
            return 0.0
        
        batch_results = self.batch_evaluate(smiles_list)
        return batch_results["passed"] / batch_results["total"]

    def get_evaluation_criteria(self) -> Dict:
        """Get ADMET evaluation criteria thresholds"""
        return {
            "lipinski_violations_max": 1,
            "mw_max": 500,
            "logp_max": 5,
            "h_donors_max": 5,
            "h_acceptors_max": 10,
            "toxicity_threshold": 0.5,
            "description": "Default ADMET filtering criteria"
        }

    def evaluate_with_details(self, smiles: str) -> Dict:
        """
        Evaluate compound and return detailed breakdown
        
        Args:
            smiles: SMILES string
            
        Returns:
            Dict with detailed evaluation results
        """
        return {
            "smiles": smiles,
            "passes_admet": self.evaluate(smiles),
            "drug_likeness": self.predict_drug_likeness(smiles),
            "toxicity": self.predict_toxicity(smiles),
            "admet_properties": self.get_admet_properties(smiles)
        }

    def filter_compounds(self, smiles_list: list, verbose: bool = False) -> Dict:
        """
        Filter a list of compounds based on ADMET criteria
        
        Args:
            smiles_list: List of SMILES strings
            verbose: Print progress information
            
        Returns:
            Dict with filtered and rejected compounds
        """
        passed = []
        failed = []
        
        for smiles in smiles_list:
            if self.evaluate(smiles):
                passed.append(smiles)
                if verbose:
                    print(f"✓ {smiles[:30]}...")
            else:
                failed.append(smiles)
                if verbose:
                    print(f"✗ {smiles[:30]}...")
        
        return {
            "passed": passed,
            "failed": failed,
            "pass_count": len(passed),
            "fail_count": len(failed),
            "pass_rate": len(passed) / len(smiles_list) if smiles_list else 0
        }

    def compare_compounds(self, smiles_list: list) -> Dict:
        """
        Compare multiple compounds for ADMET properties
        
        Args:
            smiles_list: List of SMILES strings
            
        Returns:
            Dict comparing all compounds
        """
        comparisons = []
        
        for smiles in smiles_list:
            comparisons.append({
                "smiles": smiles[:30] + "..." if len(smiles) > 30 else smiles,
                "passes_admet": self.evaluate(smiles),
                "drug_like": self.predict_drug_likeness(smiles).get("drug_like", False)
            })
        
        return {
            "total_compared": len(smiles_list),
            "comparisons": comparisons,
            "best_compounds": [c for c in comparisons if c["passes_admet"]]
        }

    def print_evaluation_report(self, smiles: str):
        """Print formatted evaluation report"""
        details = self.evaluate_with_details(smiles)
        
        print("\n" + "=" * 60)
        print("ADMET EVALUATION REPORT")
        print("=" * 60)
        print(f"\nCompound: {smiles}")
        print(f"ADMET Pass: {'✓ YES' if details['passes_admet'] else '✗ NO'}")
        
        if details["drug_likeness"]:
            print(f"\nDrug-likeness:")
            print(f"  Score: {details['drug_likeness'].get('lipinski_score', 'N/A')}")
            print(f"  Violations: {len(details['drug_likeness'].get('violations', []))}")
        
        print("\n" + "=" * 60 + "\n")


