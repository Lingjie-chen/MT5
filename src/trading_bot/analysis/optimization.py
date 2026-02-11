import numpy as np
import random
import logging
import math
from typing import List, Dict, Callable, Tuple, Optional
from joblib import Parallel, delayed

logger = logging.getLogger(__name__)

class Optimizer:
    """
    Base Optimizer Class (Enhanced with Vectorization Support)
    Uses PCG64 for high-performance random number generation.
    """
    def __init__(self, name: str = "BaseOptimizer", seed: Optional[int] = None, dtype=np.float64):
        self.name = name
        # Optimization: Use PCG64 Generator (35x faster than random.random)
        self.rng = np.random.default_rng(seed)
        self.dtype = dtype
        self.best_solution = None
        self.best_score = -float('inf') # Maximization assumption in this project
        self.history = []

    def _initialize_population(self, pop_size, dim, bounds):
        """Vectorized Population Initialization"""
        lb = np.array([b[0] for b in bounds], dtype=self.dtype)
        ub = np.array([b[1] for b in bounds], dtype=self.dtype)
        # Broadcasting to generate (N, D) matrix
        return self.rng.uniform(lb, ub, size=(pop_size, dim)).astype(self.dtype)

    def optimize(self, objective_function: Callable, bounds: List[Tuple[float, float]], steps: List[float] = None, epochs: int = 100, n_jobs: int = 1, historical_data: List[Dict] = None):
        raise NotImplementedError("Subclasses must implement optimize method")

class WOAm(Optimizer):
    """
    Whale Optimization Algorithm M (Modified) - Vectorized Implementation
    High-Performance Matrix Algebra Version based on HPC analysis.
    """
    def __init__(self, pop_size: int = 200, power_dist_coeff: float = 30.0):
        super().__init__("WOAm")
        self.pop_size = pop_size
        self.power_dist_coeff = power_dist_coeff
        
    def optimize(self, objective_function: Callable, bounds: List[Tuple[float, float]], steps: List[float] = None, epochs: int = 100, n_jobs: int = 1, historical_data: List[Dict] = None):
        """
        Vectorized optimization loop using NumPy broadcasting and Joblib parallelism.
        """
        dim = len(bounds)
        X = self._initialize_population(self.pop_size, dim, bounds)
        
        # Pre-allocate loop constants
        lb = np.array([b[0] for b in bounds])
        ub = np.array([b[1] for b in bounds])
        
        # Handle Discretization Steps (SeInDiSp optimization)
        step_arr = None
        if steps is not None:
            step_arr = np.array(steps)
            
        # --- Seeding from History (Vectorized) ---
        if historical_data:
            # Sort and pick top 20%
            sorted_history = sorted(historical_data, key=lambda x: x.get('score', 0), reverse=True)
            seed_count = min(len(sorted_history), int(self.pop_size * 0.2))
            
            for i in range(seed_count):
                if 'params' in sorted_history[i]:
                    suggested = np.array(sorted_history[i]['params'])
                    # Add noise
                    noise = self.rng.uniform(-0.05, 0.05, size=dim) * (ub - lb)
                    candidate = suggested + noise
                    candidate = np.clip(candidate, lb, ub)
                    if step_arr is not None:
                        candidate = lb + np.round((candidate - lb) / step_arr) * step_arr
                    X[i] = candidate

        # Helper for evaluation to avoid code duplication and manage parallel pool
        def evaluate(population, parallel_pool=None):
            if parallel_pool:
                return np.array(parallel_pool(delayed(objective_function)(ind) for ind in population))
            else:
                return np.array([objective_function(ind) for ind in population])

        # --- Optimization Loop with Resource Management ---
        # Use threading backend on Windows to completely avoid resource_tracker/multiprocessing issues
        # NumPy releases GIL for vector operations, so threading is efficient and safe here.
        with Parallel(n_jobs=n_jobs, backend="threading") as parallel:
            pool = parallel if n_jobs != 1 else None

            # --- Initial Evaluation ---
            fitness = evaluate(X, pool)
            
            # Initial Best Finding
            # Note: We are MAXIMIZING score in this project
            best_idx = np.argmax(fitness)
            self.best_solution = X[best_idx].copy()
            self.best_score = fitness[best_idx]
            
            # Pre-allocate History
            self.history = np.zeros(epochs)
    
            # --- Main Optimization Loop (No Agent Loop!) ---
            for t in range(epochs):
                # 1. Update WOA Parameters
                a = 2.0 - t * (2.0 / epochs)
                b = 1.0 # Spiral constant
                
                # Generate random vectors for ALL agents simultaneously (Batch Entropy)
                r1 = self.rng.random((self.pop_size, dim))
                r2 = self.rng.random((self.pop_size, dim))
                p = self.rng.random((self.pop_size, 1))  # (N, 1) for broadcasting
                l = self.rng.uniform(-1, 1, (self.pop_size, dim))
                
                A = 2.0 * a * r1 - a
                C = 2.0 * r2
                
                # 2. Logic Masking (Branchless Approach)
                # Spiral Mask
                spiral_mask = (p >= 0.5)
                
                # Exploit vs Explore Mask
                abs_A = np.abs(A)
                encircle_mask = (p < 0.5) & (abs_A < 1.0)
                search_mask = (p < 0.5) & (abs_A >= 1.0)
                
                # 3. Calculate Potential Positions (All Paths)
                
                # Path A: Shrinking Encircling (Towards Best)
                D_encircle = np.abs(C * self.best_solution - X)
                X_encircle = self.best_solution - A * D_encircle
                
                # Path B: Spiral Update (Towards Best)
                D_spiral = np.abs(self.best_solution - X)
                X_spiral = D_spiral * np.exp(b * l) * np.cos(2 * np.pi * l) + self.best_solution
                
                # Path C: Search for Prey (Towards Random Agent)
                # Efficiently shuffle indices to pick random partners
                rand_idxs = self.rng.integers(0, self.pop_size, size=self.pop_size)
                X_rand = X[rand_idxs]
                D_search = np.abs(C * X_rand - X)
                X_search = X_rand - A * D_search
                
                # 4. Modified WOAm Logic: Migration (PowerDistribution)
                # 1% probability of migration
                migration_mask = (self.rng.random((self.pop_size, 1)) < 0.01)
                # Vectorized Power Law generation
                u_mig = self.rng.random((self.pop_size, dim))
                mig_steps = u_mig ** (1.0 / (self.power_dist_coeff + 1))
                X_migration = lb + mig_steps * (ub - lb)
    
                # 5. Composite Update (Layering Masks)
                # Start with Spiral as base (p >= 0.5)
                X_next = np.where(spiral_mask, X_spiral, X)
                # Apply Encircle (p < 0.5 & |A| < 1)
                X_next = np.where(encircle_mask, X_encircle, X_next)
                # Apply Search (p < 0.5 & |A| >= 1)
                X_next = np.where(search_mask, X_search, X_next)
                # Apply Migration (Override)
                X_next = np.where(migration_mask, X_migration, X_next)
                
                # 6. Boundary Handling & Discretization (SeInDiSp)
                X_next = np.clip(X_next, lb, ub)
                if step_arr is not None:
                    # Vectorized SeInDiSp
                    # round((x - min) / step) * step + min
                    steps_matrix = (X_next - lb) / step_arr
                    X_next = lb + np.round(steps_matrix) * step_arr
                
                X = X_next
                
                # 7. Evaluation
                fitness = evaluate(X, pool)
                
                # 8. Update Best
                current_best_idx = np.argmax(fitness)
                current_best_val = fitness[current_best_idx]
                
                if current_best_val > self.best_score:
                    self.best_score = current_best_val
                    self.best_solution = X[current_best_idx].copy()
                
                self.history[t] = self.best_score
                
                # Optional: Logging
                if t % 10 == 0 or t == epochs - 1:
                    # logger.info(f"WOAm Epoch {t}: Best Score = {self.best_score:.4f}")
                    pass
            
        return self.best_solution, self.best_score

class TETA(Optimizer):
    """
    Time Evolution Travel Algorithm (TETA)
    Updated to use PCG64 RNG from Base Class.
    """
    def __init__(self, pop_size: int = 200):
        super().__init__("TETA")
        self.pop_size = pop_size

    def optimize(self, objective_function: Callable, bounds: List[Tuple[float, float]], steps: List[float] = None, epochs: int = 100, n_jobs: int = 1, historical_data: List[Dict] = None):
        dim = len(bounds)
        if steps is None:
            steps = [0.0] * dim
            
        # Use vectorized init from base
        population = self._initialize_population(self.pop_size, dim, bounds)
        
        # Helper for evaluation to avoid code duplication and manage parallel pool
        def evaluate(pop, parallel_pool=None):
            if parallel_pool:
                return np.array(parallel_pool(delayed(objective_function)(ind) for ind in pop))
            else:
                return np.array([objective_function(ind) for ind in pop])

        # --- Optimization Loop with Resource Management ---
        # max_nbytes=None disables memory mapping for arguments to avoid file cleanup race conditions
        with Parallel(n_jobs=n_jobs, max_nbytes=None) as parallel:
            pool = parallel if n_jobs != 1 else None

            # Parallel Evaluation
            fitness = evaluate(population, pool)
    
            local_best_pos = population.copy()
            local_best_fit = fitness.copy()
    
            best_idx = np.argmax(fitness)
            self.best_solution = population[best_idx].copy()
            self.best_score = fitness[best_idx]
    
            # Sort population
            sort_idx = np.argsort(local_best_fit)[::-1] # Descending
            population = population[sort_idx]
            fitness = fitness[sort_idx]
            local_best_pos = local_best_pos[sort_idx]
            local_best_fit = local_best_fit[sort_idx]
    
            for epoch in range(epochs):
                # Moving (Partially vectorized logic)
                # TETA logic is pairwise, harder to fully vectorize without adjacency matrix.
                # Keeping loop for now but using numpy arrays for speed.
                
                new_pop = population.copy()
                
                for i in range(self.pop_size):
                    for j in range(dim):
                        rnd = self.rng.random()
                        rnd *= rnd
                        
                        pair = int(rnd * (self.pop_size - 1))
                        pair = max(0, min(self.pop_size - 1, pair))
                        
                        val = 0.0
                        
                        if i != pair:
                            if i < pair: # i is better
                                val = population[i, j] + rnd * (local_best_pos[pair, j] - local_best_pos[i, j])
                            else: # i is worse
                                if self.rng.random() > rnd:
                                    val = local_best_pos[i, j] + (1.0 - rnd) * (local_best_pos[pair, j] - local_best_pos[i, j])
                                else:
                                    val = local_best_pos[pair, j]
                        else:
                            # Gaussian
                            sigma = (bounds[j][1] - bounds[j][0]) / 6.0
                            val = self.rng.normal(self.best_solution[j], sigma)
                        
                        # Bound
                        val = max(bounds[j][0], min(bounds[j][1], val))
                        if steps[j] > 0: val = round(val / steps[j]) * steps[j]
                        new_pop[i, j] = val
    
                population = new_pop
                
                # Evaluation
                fitness = evaluate(population, pool)
    
                # Update Global
                curr_best_idx = np.argmax(fitness)
                if fitness[curr_best_idx] > self.best_score:
                    self.best_score = fitness[curr_best_idx]
                    self.best_solution = population[curr_best_idx].copy()
                
                # Update Local
                improved_mask = fitness > local_best_fit
                local_best_fit[improved_mask] = fitness[improved_mask]
                local_best_pos[improved_mask] = population[improved_mask]
                
                # Sort
                sort_idx = np.argsort(local_best_fit)[::-1]
                population = population[sort_idx]
                fitness = fitness[sort_idx]
                local_best_pos = local_best_pos[sort_idx]
                local_best_fit = local_best_fit[sort_idx]
                
        return self.best_solution, self.best_score

# Compatibility aliases/placeholders for others if needed
# GWO, COAm, BBO, DE can be similarly updated. 
# For now, we focus on WOAm and TETA as primary.
