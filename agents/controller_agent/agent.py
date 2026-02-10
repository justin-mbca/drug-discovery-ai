"""
ControllerAgent: Lightweight multi-agent workflow orchestrator
- No heavy ML dependencies
- Fast initialization and coordination
- Manages goal-driven molecular discovery
"""

from typing import Dict, Optional


class ControllerAgent:
    """Orchestrates multi-agent workflow for drug discovery"""
    
    def __init__(self, goals: Optional[Dict] = None):
        """
        Initialize ControllerAgent
        
        Args:
            goals: Dictionary of optimization goals and constraints
        """
        self.goals = goals or {}
        self.target_molecules = self.goals.get("target", 10)
        self.success_rate_threshold = self.goals.get("success_rate", 0.5)
        self.max_iterations = self.goals.get("max_iterations", 100)
        
        self.iteration_count = 0
        self.success_count = 0
        self.failure_count = 0

    def stop(self, success_count: int, target: Optional[int] = None) -> bool:
        """
        Check if workflow should stop
        
        Args:
            success_count: Number of successful molecules found
            target: Target number of molecules (overrides init target)
            
        Returns:
            True if stopping criteria met, False otherwise
        """
        target = target or self.target_molecules
        return success_count >= target

    def should_continue(self, iteration: int, success_count: int) -> bool:
        """
        Determine if workflow should continue
        
        Args:
            iteration: Current iteration number
            success_count: Number of successes so far
            
        Returns:
            True if should continue, False if should stop
        """
        # Stop if max iterations reached
        if iteration >= self.max_iterations:
            return False
        
        # Stop if target molecules found
        if success_count >= self.target_molecules:
            return False
        
        return True

    def get_status(self) -> Dict:
        """Get current workflow status"""
        return {
            "goals": self.goals,
            "target_molecules": self.target_molecules,
            "success_rate_threshold": self.success_rate_threshold,
            "max_iterations": self.max_iterations,
            "iteration_count": self.iteration_count,
            "success_count": self.success_count,
            "failure_count": self.failure_count
        }

    def update_goals(self, new_goals: Dict):
        """Update workflow goals"""
        self.goals.update(new_goals)
        self.target_molecules = self.goals.get("target", self.target_molecules)
        self.success_rate_threshold = self.goals.get("success_rate", self.success_rate_threshold)
        self.max_iterations = self.goals.get("max_iterations", self.max_iterations)

    def record_success(self):
        """Record a successful design"""
        self.success_count += 1

    def record_failure(self):
        """Record a failed design"""
        self.failure_count += 1

    def next_iteration(self):
        """Move to next iteration"""
        self.iteration_count += 1

    def reset(self):
        """Reset controller to initial state"""
        self.iteration_count = 0
        self.success_count = 0
        self.failure_count = 0
        print("✓ Controller reset")

    def get_progress(self) -> Dict:
        """Get progress metrics
        
        Returns:
            Dict with progress information
        """
        total = self.success_count + self.failure_count
        success_rate = self.success_count / total if total > 0 else 0
        
        return {
            "iterations": self.iteration_count,
            "successes": self.success_count,
            "failures": self.failure_count,
            "success_rate": success_rate,
            "target_remaining": max(0, self.target_molecules - self.success_count),
            "iterations_remaining": max(0, self.max_iterations - self.iteration_count)
        }

    def print_progress(self):
        """Print formatted progress report"""
        progress = self.get_progress()
        
        print("\n" + "=" * 60)
        print("WORKFLOW PROGRESS")
        print("=" * 60)
        print(f"\nTarget Molecules: {self.target_molecules}")
        print(f"Current Progress: {progress['successes']}/{self.target_molecules}")
        print(f"Success Rate:     {progress['success_rate']:.1%}")
        print(f"\nIterations:")
        print(f"  Current:   {progress['iterations']}")
        print(f"  Remaining: {progress['iterations_remaining']}")
        print(f"\nResults:")
        print(f"  Successes: {progress['successes']}")
        print(f"  Failures:  {progress['failures']}")
        print("\n" + "=" * 60 + "\n")

    def get_success_rate(self) -> float:
        """Get current success rate (0-1)"""
        total = self.success_count + self.failure_count
        return self.success_count / total if total > 0 else 0

    def has_reached_target(self) -> bool:
        """Check if target molecules reached"""
        return self.success_count >= self.target_molecules

    def has_exceeded_iterations(self) -> bool:
        """Check if max iterations exceeded"""
        return self.iteration_count >= self.max_iterations

    def get_remaining(self) -> Dict:
        """Get remaining targets and iterations"""
        return {
            "molecules_remaining": max(0, self.target_molecules - self.success_count),
            "iterations_remaining": max(0, self.max_iterations - self.iteration_count)
        }

    def estimate_completion(self) -> Dict:
        """Estimate iterations needed to reach target
        
        Returns:
            Dict with completion estimates
        """
        if self.iteration_count == 0 or self.success_count == 0:
            return {
                "estimated_iterations": self.max_iterations,
                "sufficient_data": False,
                "message": "Not enough data for estimation"
            }
        
        # Calculate average success rate
        avg_success_rate = self.success_count / self.iteration_count
        remaining = self.target_molecules - self.success_count
        
        if avg_success_rate == 0:
            return {
                "estimated_iterations": float('inf'),
                "sufficient_data": True,
                "message": "No successes yet - cannot estimate"
            }
        
        estimated = remaining / avg_success_rate
        
        return {
            "estimated_iterations": int(estimated),
            "current_success_rate": avg_success_rate,
            "iterations_completed": self.iteration_count,
            "sufficient_data": True,
            "achievable": estimated < self.max_iterations,
            "message": f"Est. {int(estimated)} iterations remaining"
        }

    def log_milestone(self, milestone: str):
        """Log a workflow milestone
        
        Args:
            milestone: Description of milestone
        """
        print(f"📍 MILESTONE: {milestone} (Iteration {self.iteration_count}, Success: {self.success_count})")

    def get_performance_metrics(self) -> Dict:
        """Get detailed performance metrics"""
        total_attempts = self.success_count + self.failure_count
        
        return {
            "total_attempts": total_attempts,
            "successes": self.success_count,
            "failures": self.failure_count,
            "success_rate": self.get_success_rate(),
            "iterations_used": self.iteration_count,
            "iterations_available": self.max_iterations,
            "efficiency": self.iteration_count / total_attempts if total_attempts > 0 else 0,
            "target_progress": self.success_count / self.target_molecules if self.target_molecules > 0 else 0
        }

