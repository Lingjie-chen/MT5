import numpy as np
import random
import logging
import math
from typing import List, Dict, Callable, Tuple

logger = logging.getLogger(__name__)

class Optimizer:
    """Base Optimization Class"""
    def __init__(self, name: str = "BaseOptimizer"):
        self.name = name
        self.best_solution = None
        self.best_score = -float('inf')
        self.history = []

    def optimize(self, objective_function: Callable, bounds: List[Tuple[float, float]], steps: List[float] = None, epochs: int = 100):
        raise NotImplementedError("Subclasses must implement optimize method")

class WOAm(Optimizer):
    """
    Whale Optimization Algorithm M (Modified)
    Based on MQL5 implementation: AO_WOA_WhaleOptimizationAlgorithm.mqh
    """
    def __init__(self, pop_size: int = 50, ref_prob: float = 0.1, spiral_coeff: float = 0.5, spiral_prob: float = 0.8):
        super().__init__("WOAm")
        self.pop_size = pop_size  # Population Size (Search Width): Larger pop_size (e.g., 50-100) covers broader search space, reducing risk of local optima.
        self.ref_prob = ref_prob
        self.spiral_coeff = spiral_coeff
        self.spiral_prob = spiral_prob
        
    def optimize(self, objective_function: Callable, bounds: List[Tuple[float, float]], steps: List[float] = None, epochs: int = 100, historical_data: List[Dict] = None):
        """
        Run the optimization process.
        
        Args:
            objective_function: Evaluation function
            bounds: Parameter bounds
            steps: Step sizes
            epochs: Number of iterations
            historical_data: Optional historical trade data for self-learning initialization
        """
        dim = len(bounds)
        if steps is None:
            steps = [0.0] * dim
            
        # Initialize
        # Current population (a) and Previous bests for each agent (agent)
        population = np.zeros((self.pop_size, dim)) # a.c
        fitness = np.full(self.pop_size, -float('inf')) # a.f
        
        agent_prev_pos = np.zeros((self.pop_size, dim)) # agent.cPrev
        agent_prev_fit = np.full(self.pop_size, -float('inf')) # agent.fPrev
        
        # Initial Random Population with Heuristic Seeding
        # Use AI-guided heuristics if historical data is available
        ai_suggestions = []
        if historical_data:
            # Simple logic: use best past parameters as seeds
            # Assume historical_data contains dicts with 'params' and 'score'
            sorted_history = sorted(historical_data, key=lambda x: x.get('score', 0), reverse=True)
            for h in sorted_history[:int(self.pop_size * 0.2)]: # Top 20%
                if 'params' in h:
                    ai_suggestions.append(h['params'])

        for i in range(self.pop_size):
            if i < len(ai_suggestions):
                # Initialize with AI suggestion
                suggested_params = ai_suggestions[i]
                for j in range(dim):
                    # Add small noise to avoid stagnation
                    noise = random.uniform(-0.05, 0.05) * (bounds[j][1] - bounds[j][0])
                    val = suggested_params[j] + noise
                    # Boundary check
                    val = max(bounds[j][0], min(bounds[j][1], val))
                    if steps[j] > 0: val = round(val / steps[j]) * steps[j]
                    population[i, j] = val
            else:
                # Random initialization
                for j in range(dim):
                    population[i, j] = random.uniform(bounds[j][0], bounds[j][1])
                    if steps[j] > 0: population[i, j] = round(population[i, j] / steps[j]) * steps[j]
            
            fitness[i] = objective_function(population[i])
            
            # Initialize agent prev
            agent_prev_pos[i] = population[i].copy()
            agent_prev_fit[i] = fitness[i]
            
        # Find global best
        best_idx = np.argmax(fitness)
        self.best_solution = population[best_idx].copy()
        self.best_score = fitness[best_idx]
        
        # Main Loop
        for epoch in range(epochs):
            # ... existing logic ...
            a_ko = 2.0 - epoch * (2.0 / epochs)
            
            new_population = np.zeros_like(population)
            
            for i in range(self.pop_size):
                for j in range(dim):
                    r = random.uniform(-1, 1)
                    A = 2.0 * a_ko * r - a_ko
                    # C = 2.0 * r # Not used in modified version logic directly as per MQL5 snippet logic trace
                    
                    l = random.uniform(-1, 1)
                    p = random.random()
                    
                    x_new = 0.0
                    
                    if p < self.ref_prob:
                        if abs(A) > 1.0:
                            # Explore: Xbest - A * |Xbest - X|
                            # Note: The MQL5 code uses cB (Global Best) here for exploration
                            x_new = self.best_solution[j] - A * abs(self.best_solution[j] - agent_prev_pos[i, j])
                        else:
                            # Exploit/Search around random leader
                            leader_idx = random.randint(0, self.pop_size - 1)
                            # Xlid - A * |Xlid - X|
                            x_new = agent_prev_pos[leader_idx, j] - A * abs(agent_prev_pos[leader_idx, j] - agent_prev_pos[i, j])
                    else:
                        if random.random() < self.spiral_prob:
                            # Spiral Update
                            # XbestPrev + |XbestPrev - X| * exp(bl) * cos(...)
                            # Note: MQL5 uses agent[i].cPrev (X) and a[i].c (Current) in distance calc
                            # But standard WOA uses distance to BEST.
                            # MQL5: x = agent[i].cPrev[c] + MathAbs(agent[i].cPrev[c] - a[i].c[c])...
                            # Let's follow MQL5 logic: Distance between Prev Best of Agent and Current Pos of Agent?
                            # Wait, a[i].c is updated in Moving(), so it's effectively X(t).
                            # agent[i].cPrev is X(t-1) or Pbest.
                            
                            dist = abs(agent_prev_pos[i, j] - population[i, j])
                            x_new = agent_prev_pos[i, j] + dist * math.exp(self.spiral_coeff * l) * math.cos(2 * math.pi * l)
                        else:
                            # Power Distribution (Local Search around Global Best)
                            # u.PowerDistribution(cB[c], rangeMin, rangeMax, 30)
                            # Simplified implementation: Gaussian around Best
                            sigma = (bounds[j][1] - bounds[j][0]) / 30.0
                            x_new = random.gauss(self.best_solution[j], sigma)
                            
                    # Boundary Check
                    x_new = max(bounds[j][0], min(bounds[j][1], x_new))
                    if steps[j] > 0: x_new = round(x_new / steps[j]) * steps[j]
                    
                    new_population[i, j] = x_new
            
            # Evaluate
            population = new_population
            for i in range(self.pop_size):
                f = objective_function(population[i])
                fitness[i] = f
                
                # Update Personal Best (Agent Memory)
                if f > agent_prev_fit[i]:
                    agent_prev_fit[i] = f
                    agent_prev_pos[i] = population[i].copy()
                    
                # Update Global Best
                if f > self.best_score:
                    self.best_score = f
                    self.best_solution = population[i].copy()
            
            self.history.append(self.best_score)
            
            if epoch % 10 == 0:
                logger.info(f"WOAm Epoch {epoch}: Best Score = {self.best_score:.4f}")
                
        return self.best_solution, self.best_score

class GWO(Optimizer):
    """
    Grey Wolf Optimizer (GWO)
    Based on MQL5 implementation: AO_GWO_GreyWolfOptimizer.mqh
    """
    def __init__(self, pop_size: int = 50, alpha_number: int = 3):
        super().__init__("GWO")
        self.pop_size = pop_size
        self.alpha_number = alpha_number # Standard GWO uses 3 (Alpha, Beta, Delta)
        
    def optimize(self, objective_function: Callable, bounds: List[Tuple[float, float]], steps: List[float] = None, epochs: int = 100, historical_data: List[Dict] = None):
        """
        Run the GWO optimization
        :param objective_function: Function that takes a list of parameters and returns a score (higher is better)
        :param bounds: List of (min, max) tuples for each parameter
        :param steps: List of step sizes for each parameter (optional, for discrete optimization)
        :param epochs: Number of iterations
        :param historical_data: Optional historical trade data for self-learning initialization
        """
        dim = len(bounds)
        if steps is None:
            steps = [0.0] * dim
            
        # 1. Initialize Population
        population = np.zeros((self.pop_size, dim))
        fitness = np.full(self.pop_size, -float('inf'))
        
        # Prepare seeding from history
        ai_suggestions = []
        if historical_data:
            sorted_history = sorted(historical_data, key=lambda x: x.get('score', 0), reverse=True)
            for h in sorted_history[:int(self.pop_size * 0.2)]: 
                if 'params' in h:
                    ai_suggestions.append(h['params'])

        # Random initialization within bounds with seeding
        for i in range(self.pop_size):
            if i < len(ai_suggestions):
                # Seed from history
                suggested = ai_suggestions[i]
                for j in range(dim):
                    noise = random.uniform(-0.05, 0.05) * (bounds[j][1] - bounds[j][0])
                    val = suggested[j] + noise
                    val = max(bounds[j][0], min(bounds[j][1], val))
                    if steps[j] > 0: val = round(val / steps[j]) * steps[j]
                    population[i, j] = val
            else:
                for j in range(dim):
                    min_val, max_val = bounds[j]
                    population[i, j] = random.uniform(min_val, max_val)
                    if steps[j] > 0:
                        population[i, j] = round(population[i, j] / steps[j]) * steps[j]
            
            # Evaluate initial fitness
            fitness[i] = objective_function(population[i])
            
        # Sort population to find initial Alpha, Beta, Delta
        sorted_indices = np.argsort(fitness)[::-1] # Descending order
        population = population[sorted_indices]
        fitness = fitness[sorted_indices]
        
        self.best_solution = population[0].copy()
        self.best_score = fitness[0]
        
        # 2. Main Loop
        for epoch in range(epochs):
            # Calculate a (linearly decreasing from 2 to 0)
            a = 2.0 - 2.0 * (epoch / epochs)
            
            # Identify Leaders (Alpha, Beta, Delta...)
            # In this generalized version, we take top 'alpha_number' wolves
            leaders = population[:self.alpha_number]
            
            # Update positions
            new_population = np.zeros_like(population)
            
            for i in range(self.pop_size):
                # Standard GWO Position Update
                # X(t+1) = (X1 + X2 + X3) / 3
                # Where X1 = Alpha - A1 * D_alpha, etc.
                
                final_pos = np.zeros(dim)
                
                for j in range(dim):
                    # For each dimension
                    x_sum = 0.0
                    
                    # Influence from each leader
                    for k in range(min(self.alpha_number, self.pop_size)):
                        leader_pos = leaders[k][j]
                        
                        r1 = random.random()
                        r2 = random.random()
                        
                        A = 2.0 * a * r1 - a
                        C = 2.0 * r2
                        
                        D = abs(C * leader_pos - population[i, j])
                        X = leader_pos - A * D
                        
                        x_sum += X
                        
                    final_pos[j] = x_sum / min(self.alpha_number, self.pop_size)
                    
                    # Boundary check & Step enforcement
                    min_val, max_val = bounds[j]
                    
                    # Simple clamping
                    final_pos[j] = max(min_val, min(max_val, final_pos[j]))
                    
                    # Step enforcement
                    if steps[j] > 0:
                         final_pos[j] = round(final_pos[j] / steps[j]) * steps[j]
                
                new_population[i] = final_pos
                
            # Evaluate new population
            population = new_population
            for i in range(self.pop_size):
                score = objective_function(population[i])
                fitness[i] = score
                
            # Sort and Update Global Best
            sorted_indices = np.argsort(fitness)[::-1]
            population = population[sorted_indices]
            fitness = fitness[sorted_indices]
            
            if fitness[0] > self.best_score:
                self.best_score = fitness[0]
                self.best_solution = population[0].copy()
                
            self.history.append(self.best_score)
            
            if epoch % 10 == 0:
                logger.info(f"Epoch {epoch}: Best Score = {self.best_score:.4f}")
                
        return self.best_solution, self.best_score

class COAm(Optimizer):
    """
    Cuckoo Optimization Algorithm M (Modified)
    Based on MQL5 implementation: AO_COAm_CuckooOptimizationAlgorithm.mqh
    """
    def __init__(self, pop_size: int = 50, nests_number: int = 20, koef_pa: float = 0.6, koef_alpha: float = 0.6, change_prob: float = 0.63):
        super().__init__("COAm")
        self.pop_size = pop_size # Standard pop size
        self.nests_number = nests_number # But we often treat pop_size as nests number in simple implementations
        self.koef_pa = koef_pa
        self.koef_alpha = koef_alpha
        self.change_prob = change_prob
        
    def optimize(self, objective_function: Callable, bounds: List[Tuple[float, float]], steps: List[float] = None, epochs: int = 100, historical_data: List[Dict] = None):
        dim = len(bounds)
        if steps is None:
            steps = [0.0] * dim
            
        # Initialize Nests
        nests = np.zeros((self.pop_size, dim))
        fitness = np.full(self.pop_size, -float('inf'))
        
        # Prepare seeding
        ai_suggestions = []
        if historical_data:
            sorted_history = sorted(historical_data, key=lambda x: x.get('score', 0), reverse=True)
            for h in sorted_history[:int(self.pop_size * 0.2)]: 
                if 'params' in h:
                    ai_suggestions.append(h['params'])

        # Initial Random Population
        for i in range(self.pop_size):
            if i < len(ai_suggestions):
                suggested = ai_suggestions[i]
                for j in range(dim):
                    noise = random.uniform(-0.05, 0.05) * (bounds[j][1] - bounds[j][0])
                    val = suggested[j] + noise
                    val = max(bounds[j][0], min(bounds[j][1], val))
                    if steps[j] > 0: val = round(val / steps[j]) * steps[j]
                    nests[i, j] = val
            else:
                for j in range(dim):
                    nests[i, j] = random.uniform(bounds[j][0], bounds[j][1])
                    if steps[j] > 0: nests[i, j] = round(nests[i, j] / steps[j]) * steps[j]
            fitness[i] = objective_function(nests[i])
            
        # Find global best
        best_idx = np.argmax(fitness)
        self.best_solution = nests[best_idx].copy()
        self.best_score = fitness[best_idx]
        
        # Step size vector v (from MQL5 Init)
        v = np.zeros(dim)
        for j in range(dim):
            v[j] = (bounds[j][1] - bounds[j][0]) * self.koef_alpha
            
        for epoch in range(epochs):
            # Moving (Lévy flights or Random Walk)
            new_nests = nests.copy()
            
            # In MQL5 Moving():
            # If !revision (first step): random init (already done)
            # Else:
            # For each agent (cuckoo):
            #   If random < changeProb:
            #     r1 = +/- 1
            #     r2 = uniform(1, 20)
            #     new_pos = pos + r1 * v * pow(r2, -2)
            
            # In MQL5, 'a' is a temporary population of cuckoos that try to replace 'nests'.
            # We will simulate this by generating new candidates.
            
            cuckoos = np.zeros_like(nests)
            cuckoo_fitness = np.full(self.pop_size, -float('inf'))
            
            for i in range(self.pop_size):
                if random.random() < self.change_prob:
                    for j in range(dim):
                        r1 = 1.0 if random.random() > 0.5 else -1.0
                        r2 = random.uniform(1.0, 20.0)
                        
                        # New position
                        val = nests[i, j] + r1 * v[j] * (r2 ** -2.0)
                        
                        # Boundary check
                        val = max(bounds[j][0], min(bounds[j][1], val))
                        if steps[j] > 0: val = round(val / steps[j]) * steps[j]
                        
                        cuckoos[i, j] = val
                else:
                    cuckoos[i] = nests[i].copy()
                    
                cuckoo_fitness[i] = objective_function(cuckoos[i])
                
            # Revision (Selection)
            # In MQL5: 
            # For each cuckoo 'a[i]':
            #   Pick random nest 'ind'
            #   If a[i].f > nests[ind].f: Replace nest
            #   Else: Cuckoo dies (we keep nest)
            
            for i in range(self.pop_size):
                ind = random.randint(0, self.pop_size - 1)
                
                if cuckoo_fitness[i] > fitness[ind]:
                    nests[ind] = cuckoos[i].copy()
                    fitness[ind] = cuckoo_fitness[i]
                    
                    if fitness[ind] > self.best_score:
                        self.best_score = fitness[ind]
                        self.best_solution = nests[ind].copy()
                        
            # Abandonment (Discovery of alien eggs)
            # For each nest:
            #   If random < pa:
            #     Destroy nest (re-initialize randomly)
            # Note: Usually we keep the best nest. MQL5 logic:
            # for n in range(nestsNumber): if rand < pa: nests[ind].f = -DBL_MAX (mark for reset?)
            # Wait, MQL5 code sets nests[ind].f = -DBL_MAX? No, it sets nests[ind].f = -DBL_MAX to effectively kill it?
            # Actually standard CS replaces bad nests with new random ones via Lévy flights.
            # Let's implement standard abandonment: replace fraction of worst nests.
            # But adhering to MQL5 logic:
            # "if (u.RNDprobab () < koef_pa) { nests [ind].f = -DBL_MAX; }"
            # It seems it marks them as empty/bad.
            # Let's simply re-randomize them if they are discovered.
            
            for i in range(self.pop_size):
                # Don't destroy the global best
                if np.array_equal(nests[i], self.best_solution):
                    continue
                    
                if random.random() < self.koef_pa:
                    # New random solution
                    for j in range(dim):
                        nests[i, j] = random.uniform(bounds[j][0], bounds[j][1])
                        if steps[j] > 0: nests[i, j] = round(nests[i, j] / steps[j]) * steps[j]
                    fitness[i] = objective_function(nests[i])
            
            # Update Global Best again after abandonment
            best_idx = np.argmax(fitness)
            if fitness[best_idx] > self.best_score:
                self.best_score = fitness[best_idx]
                self.best_solution = nests[best_idx].copy()
                
            self.history.append(self.best_score)
            
            if epoch % 10 == 0:
                logger.info(f"COAm Epoch {epoch}: Best Score = {self.best_score:.4f}")
                
        return self.best_solution, self.best_score

class BBO(Optimizer):
    """
    Biogeography-Based Optimization (BBO)
    Based on MQL5 implementation: AO_BBO_BiogeographyBasedOptimization.mqh
    """
    def __init__(self, pop_size: int = 50, immigration_max: float = 1.0, emigration_max: float = 1.0, mutation_prob: float = 0.5, elitism_count: int = 2):
        super().__init__("BBO")
        self.pop_size = pop_size
        self.immigration_max = immigration_max
        self.emigration_max = emigration_max
        self.mutation_prob = mutation_prob
        self.elitism_count = elitism_count
        
    def optimize(self, objective_function: Callable, bounds: List[Tuple[float, float]], steps: List[float] = None, epochs: int = 100, historical_data: List[Dict] = None):
        dim = len(bounds)
        if steps is None:
            steps = [0.0] * dim
            
        # Initialize Population
        population = np.zeros((self.pop_size, dim))
        fitness = np.full(self.pop_size, -float('inf'))
        
        # Seeding
        ai_suggestions = []
        if historical_data:
            sorted_history = sorted(historical_data, key=lambda x: x.get('score', 0), reverse=True)
            for h in sorted_history[:int(self.pop_size * 0.2)]: 
                if 'params' in h:
                    ai_suggestions.append(h['params'])

        for i in range(self.pop_size):
            if i < len(ai_suggestions):
                suggested = ai_suggestions[i]
                for j in range(dim):
                    noise = random.uniform(-0.05, 0.05) * (bounds[j][1] - bounds[j][0])
                    val = suggested[j] + noise
                    val = max(bounds[j][0], min(bounds[j][1], val))
                    if steps[j] > 0: val = round(val / steps[j]) * steps[j]
                    population[i, j] = val
            else:
                for j in range(dim):
                    population[i, j] = random.uniform(bounds[j][0], bounds[j][1])
                    if steps[j] > 0: population[i, j] = round(population[i, j] / steps[j]) * steps[j]
            fitness[i] = objective_function(population[i])
            
        # Sort by fitness (HSI)
        sorted_indices = np.argsort(fitness)[::-1]
        population = population[sorted_indices]
        fitness = fitness[sorted_indices]
        
        self.best_solution = population[0].copy()
        self.best_score = fitness[0]
        
        # BBO Parameters
        species_max = self.pop_size # S_max
        
        for epoch in range(epochs):
            # 1. Calculate Rates (Lambda, Mu)
            # Sorted: Index 0 is Best (Most Species), Index N is Worst (Fewest Species)
            # In MQL5: i=0 is best.
            # species_count = S_max - i (Linear map: Best has S_max, Worst has 0)
            
            lambda_vec = np.zeros(self.pop_size) # Immigration Rate
            mu_vec = np.zeros(self.pop_size)     # Emigration Rate
            
            for i in range(self.pop_size):
                k = i # rank, 0 is best
                ratio = k / self.pop_size
                # lambda_vec[i] = self.immigration_max * ratio # High rank (low i) -> Low Immigration?
                # Wait, MQL5: immigration = I * (1 - k/N).
                # If i=0 (Best), Im = I * (1 - 0) = I (High Immigration?)
                # Actually, usually Best habitats have High Emigration, Low Immigration.
                # Let's check MQL5 code:
                # habitatData[i].speciesCount = speciesMax - (i * speciesMax / popSize); (i=0 -> S=Max)
                # immigration = I * (1 - S/Smax). If S=Smax (Best), Im = 0.
                # emigration = E * S/Smax. If S=Smax (Best), Em = E.
                # So Best solutions (i=0) have Im=0, Em=Max. Correct.
                
                species_count = species_max - (i * species_max / self.pop_size)
                ratio_s = species_count / species_max
                
                lambda_vec[i] = self.immigration_max * (1.0 - ratio_s)
                mu_vec[i] = self.emigration_max * ratio_s
                
            # 2. Migration
            new_population = population.copy()
            
            for i in range(self.elitism_count, self.pop_size): # Skip elites
                if random.random() < lambda_vec[i]:
                    for j in range(dim):
                        if random.random() < lambda_vec[i]: # MQL5 logic: check for each coord?
                            # MQL5: if (RND < Im) { for c: if (RND < Im) ... }
                            # Yes, checking again per coordinate seems to be the implementation.
                            
                            # Select Source (Roulette Wheel based on Emigration Rate)
                            sum_mu = np.sum(mu_vec) - mu_vec[i] # Exclude self? MQL5 excludes self.
                            if sum_mu > 0:
                                pick = random.uniform(0, sum_mu)
                                current = 0
                                source_idx = -1
                                for k in range(self.pop_size):
                                    if k == i: continue
                                    current += mu_vec[k]
                                    if current >= pick:
                                        source_idx = k
                                        break
                                
                                if source_idx != -1:
                                    new_population[i, j] = population[source_idx, j]
                                    
            # 3. Mutation
            for i in range(self.elitism_count, self.pop_size):
                # Mutation prob based on species count (probability of existence)
                # MQL5 uses a Gaussian-like prob model.
                # We simplified: mutationRate = prob * (1 - P).
                # Let's just use constant mutation for simplicity or simple adaptive.
                
                mutation_rate = self.mutation_prob # Simplified
                
                if random.random() < mutation_rate:
                    mutate_idx = random.randint(0, dim - 1)
                    val = random.uniform(bounds[mutate_idx][0], bounds[mutate_idx][1])
                    if steps[mutate_idx] > 0: val = round(val / steps[mutate_idx]) * steps[mutate_idx]
                    new_population[i, mutate_idx] = val
                    
            # Evaluate
            population = new_population
            for i in range(self.pop_size):
                fitness[i] = objective_function(population[i])
                
            # Sort
            sorted_indices = np.argsort(fitness)[::-1]
            population = population[sorted_indices]
            fitness = fitness[sorted_indices]
            
            if fitness[0] > self.best_score:
                self.best_score = fitness[0]
                self.best_solution = population[0].copy()
                
            self.history.append(self.best_score)
            
            if epoch % 10 == 0:
                logger.info(f"BBO Epoch {epoch}: Best Score = {self.best_score:.4f}")
                
        return self.best_solution, self.best_score

class DE(Optimizer):
    """
    Differential Evolution (DE)
    Another popular AO from the list
    """
    def __init__(self, pop_size: int = 50, F: float = 0.5, CR: float = 0.7):
        super().__init__("DE")
        self.pop_size = pop_size
        self.F = F   # Mutation factor
        self.CR = CR # Crossover rate
        
    def optimize(self, objective_function: Callable, bounds: List[Tuple[float, float]], steps: List[float] = None, epochs: int = 100, historical_data: List[Dict] = None):
        dim = len(bounds)
        if steps is None:
            steps = [0.0] * dim
            
        # Initialize
        population = np.zeros((self.pop_size, dim))
        fitness = np.full(self.pop_size, -float('inf'))
        
        # Seeding
        ai_suggestions = []
        if historical_data:
            sorted_history = sorted(historical_data, key=lambda x: x.get('score', 0), reverse=True)
            for h in sorted_history[:int(self.pop_size * 0.2)]: 
                if 'params' in h:
                    ai_suggestions.append(h['params'])

        for i in range(self.pop_size):
            if i < len(ai_suggestions):
                suggested = ai_suggestions[i]
                for j in range(dim):
                    noise = random.uniform(-0.05, 0.05) * (bounds[j][1] - bounds[j][0])
                    val = suggested[j] + noise
                    val = max(bounds[j][0], min(bounds[j][1], val))
                    if steps[j] > 0: val = round(val / steps[j]) * steps[j]
                    population[i, j] = val
            else:
                for j in range(dim):
                    population[i, j] = random.uniform(bounds[j][0], bounds[j][1])
                    if steps[j] > 0: population[i, j] = round(population[i, j] / steps[j]) * steps[j]
            fitness[i] = objective_function(population[i])
            
        best_idx = np.argmax(fitness)
        self.best_solution = population[best_idx].copy()
        self.best_score = fitness[best_idx]
        
        for epoch in range(epochs):
            for i in range(self.pop_size):
                # Mutation
                idxs = [idx for idx in range(self.pop_size) if idx != i]
                a, b, c = population[np.random.choice(idxs, 3, replace=False)]
                mutant = a + self.F * (b - c)
                
                # Crossover
                cross_points = np.random.rand(dim) < self.CR
                if not np.any(cross_points):
                    cross_points[np.random.randint(0, dim)] = True
                    
                trial = np.where(cross_points, mutant, population[i])
                
                # Boundary & Step
                for j in range(dim):
                    trial[j] = max(bounds[j][0], min(bounds[j][1], trial[j]))
                    if steps[j] > 0: trial[j] = round(trial[j] / steps[j]) * steps[j]
                    
                # Selection
                f_trial = objective_function(trial)
                if f_trial > fitness[i]:
                    population[i] = trial
                    fitness[i] = f_trial
                    if f_trial > self.best_score:
                        self.best_score = f_trial
                        self.best_solution = trial.copy()
                        
            if epoch % 10 == 0:
                logger.info(f"DE Epoch {epoch}: Best Score = {self.best_score:.4f}")
                
        return self.best_solution, self.best_score

class TETA(Optimizer):
    """
    Time Evolution Travel Algorithm (TETA)
    Based on MQL5 implementation: AO_TETA_TimeEvolutionTravelAlgorithm.mqh
    """
    def __init__(self, pop_size: int = 50):
        super().__init__("TETA")
        self.pop_size = pop_size

    def optimize(self, objective_function: Callable, bounds: List[Tuple[float, float]], steps: List[float] = None, epochs: int = 100, historical_data: List[Dict] = None):
        dim = len(bounds)
        if steps is None:
            steps = [0.0] * dim

        # Initialize Population
        # a.c (current coordinates)
        population = np.zeros((self.pop_size, dim))
        # a.f (current fitness)
        fitness = np.full(self.pop_size, -float('inf'))
        
        # a.cB (local best coordinates)
        local_best_pos = np.zeros((self.pop_size, dim))
        # a.fB (local best fitness)
        local_best_fit = np.full(self.pop_size, -float('inf'))

        # Global Best
        self.best_solution = np.zeros(dim)
        self.best_score = -float('inf')

        # Seeding
        ai_suggestions = []
        if historical_data:
            sorted_history = sorted(historical_data, key=lambda x: x.get('score', 0), reverse=True)
            for h in sorted_history[:int(self.pop_size * 0.2)]: 
                if 'params' in h:
                    ai_suggestions.append(h['params'])

        # Initialization
        for i in range(self.pop_size):
            if i < len(ai_suggestions):
                suggested = ai_suggestions[i]
                for j in range(dim):
                    noise = random.uniform(-0.05, 0.05) * (bounds[j][1] - bounds[j][0])
                    val = suggested[j] + noise
                    val = max(bounds[j][0], min(bounds[j][1], val))
                    if steps[j] > 0: val = round(val / steps[j]) * steps[j]
                    population[i, j] = val
            else:
                for j in range(dim):
                    population[i, j] = random.uniform(bounds[j][0], bounds[j][1])
                    if steps[j] > 0: population[i, j] = round(population[i, j] / steps[j]) * steps[j]
            
            # Initial Evaluation
            fitness[i] = objective_function(population[i])
            
            # Update Local Best
            local_best_pos[i] = population[i].copy()
            local_best_fit[i] = fitness[i]
            
            # Update Global Best
            if fitness[i] > self.best_score:
                self.best_score = fitness[i]
                self.best_solution = population[i].copy()

        # Sort population by local best fitness (fB) initially
        sort_idx = np.argsort(local_best_fit)[::-1]
        population = population[sort_idx]
        fitness = fitness[sort_idx]
        local_best_pos = local_best_pos[sort_idx]
        local_best_fit = local_best_fit[sort_idx]

        for epoch in range(epochs):
            # Moving
            # Update current coordinates 'population'
            # Since we sorted, index 0 is best, index N-1 is worst.
            
            for i in range(self.pop_size):
                for j in range(dim):
                    rnd = random.random()
                    rnd *= rnd
                    
                    # Select pair: Scale rnd (0..1) to (0..pop_size-1)
                    pair = int(rnd * (self.pop_size - 1))
                    pair = max(0, min(self.pop_size - 1, pair))
                    
                    val = 0.0
                    
                    if i != pair:
                        if i < pair:
                            # Current universe 'i' is better than 'pair' (since sorted descending)
                            # val = c + rnd * (cB_pair - cB_i)
                            val = population[i, j] + rnd * (local_best_pos[pair, j] - local_best_pos[i, j])
                        else:
                            # Current 'i' is worse than 'pair'
                            if random.random() > rnd:
                                # val = cB_i + (1-rnd) * (cB_pair - cB_i)
                                val = local_best_pos[i, j] + (1.0 - rnd) * (local_best_pos[pair, j] - local_best_pos[i, j])
                            else:
                                val = local_best_pos[pair, j]
                    else:
                        # i == pair
                        # Gaussian around Global Best
                        sigma = (bounds[j][1] - bounds[j][0]) / 6.0
                        val = random.gauss(self.best_solution[j], sigma)
                    
                    # Boundary and Step
                    val = max(bounds[j][0], min(bounds[j][1], val))
                    if steps[j] > 0: val = round(val / steps[j]) * steps[j]
                    
                    population[i, j] = val

            # Revision
            for i in range(self.pop_size):
                fitness[i] = objective_function(population[i])
                
                # Update Global Best
                if fitness[i] > self.best_score:
                    self.best_score = fitness[i]
                    self.best_solution = population[i].copy()
                
                # Update Local Best
                if fitness[i] > local_best_fit[i]:
                    local_best_fit[i] = fitness[i]
                    local_best_pos[i] = population[i].copy()
            
            # Sort universes by Local Best Fitness (fB) for next iteration
            sort_idx = np.argsort(local_best_fit)[::-1]
            population = population[sort_idx]
            fitness = fitness[sort_idx]
            local_best_pos = local_best_pos[sort_idx]
            local_best_fit = local_best_fit[sort_idx]
            
            self.history.append(self.best_score)
            
            if epoch % 10 == 0:
                logger.info(f"TETA Epoch {epoch}: Best Score = {self.best_score:.4f}")

        return self.best_solution, self.best_score
