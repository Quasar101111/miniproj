import numpy as np
from typing import List, Dict, Tuple, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from datetime import datetime
from .schemas import WarehouseBase, TenantBase

class ContentBasedFilter:
    """
    Content-based filtering recommendation system that recommends warehouses based on
    their features and tenant preferences.
    """
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english')
        
    def create_warehouse_profile(self, warehouse: WarehouseBase) -> Dict:
        """Create a feature profile for a warehouse"""
        return {
            'id': warehouse.id,
            'location': (warehouse.latitude, warehouse.longitude),
            'size': warehouse.length * warehouse.width * warehouse.height,
            'price': warehouse.rental_price,
            'facilities': ' '.join(warehouse.facilities),
            'age': (datetime.now().year - warehouse.year_built.year) if hasattr(warehouse.year_built, 'year') else 0
        }
    
    def create_tenant_profile(self, tenant: TenantBase) -> Dict:
        """Create a feature profile for a tenant"""
        avg_price = 0
        if tenant.preferred_price_range:
            avg_price = sum(tenant.preferred_price_range) / 2
            
        return {
            'location': (tenant.latitude or 0, tenant.longitude or 0),
            'price_preference': avg_price,
            'experience': tenant.lease_history_count
        }
    
    def calculate_location_similarity(self, warehouse_loc: Tuple[float, float], 
                                     tenant_loc: Tuple[float, float]) -> float:
        """Calculate similarity between two geographical locations"""
        if tenant_loc[0] == 0 and tenant_loc[1] == 0:
            return 0.5  # Neutral score if tenant location is not specified
            
        # Haversine formula could be used for more accurate distance calculation
        # Using simple Euclidean distance for simplicity
        w_lat, w_lon = warehouse_loc
        t_lat, t_lon = tenant_loc
        
        # Scale distance to a similarity score between 0 and 1
        distance = np.sqrt((w_lat - t_lat)**2 + (w_lon - t_lon)**2)
        max_distance = np.sqrt(180**2 + 360**2)  # Max possible distance
        
        return 1 - (distance / max_distance)
    
    def calculate_price_similarity(self, warehouse_price: float, tenant_price_pref: float) -> float:
        """Calculate similarity between warehouse price and tenant's price preference"""
        if tenant_price_pref == 0:
            return 0.5  # Neutral score if tenant has no price preference
            
        # Calculate normalized price difference
        price_diff = abs(warehouse_price - tenant_price_pref)
        max_price = max(warehouse_price, tenant_price_pref)
        
        return 1 - min(1, price_diff / max_price)
    
    def calculate_facility_similarity(self, warehouses: List[WarehouseBase]) -> np.ndarray:
        """Calculate similarity between warehouses based on their facilities"""
        # Extract facilities text for each warehouse
        facilities_text = [' '.join(w.facilities) if w.facilities else '' for w in warehouses]
        
        # Handle empty facilities
        if all(f == '' for f in facilities_text):
            return np.ones((len(warehouses), len(warehouses)))
            
        # Calculate TF-IDF matrix
        try:
            tfidf_matrix = self.vectorizer.fit_transform(facilities_text)
            # Calculate cosine similarity between warehouses
            return cosine_similarity(tfidf_matrix)
        except:
            # Fallback if vectorization fails
            return np.ones((len(warehouses), len(warehouses)))
    
    def recommend(self, warehouses: List[WarehouseBase], tenant: TenantBase, 
                 weights: Dict[str, float] = None) -> np.ndarray:
        """
        Generate recommendations using content-based filtering
        
        Parameters:
        - warehouses: List of available warehouses
        - tenant: Tenant for whom recommendations are generated
        - weights: Optional dictionary with weights for different features
                 ('location', 'price', 'facilities')
        
        Returns:
        - Array of similarity scores for each warehouse
        """
        if not warehouses:
            return np.array([])
            
        # Default weights
        if weights is None:
            weights = {
                'location': 0.4,
                'price': 0.4,
                'facilities': 0.2
            }
            
        tenant_profile = self.create_tenant_profile(tenant)
        warehouse_profiles = [self.create_warehouse_profile(w) for w in warehouses]
        
        # Calculate facility similarity matrix
        facility_sim_matrix = self.calculate_facility_similarity(warehouses)
        
        # Calculate final scores
        scores = []
        for i, warehouse in enumerate(warehouse_profiles):
            # Location similarity
            loc_sim = self.calculate_location_similarity(
                warehouse['location'], 
                tenant_profile['location']
            )
            
            # Price similarity
            price_sim = self.calculate_price_similarity(
                warehouse['price'], 
                tenant_profile['price_preference']
            )
            
            # Facility similarity (average with all other warehouses)
            facility_sim = np.mean(facility_sim_matrix[i])
            
            # Weighted score
            score = (
                weights['location'] * loc_sim +
                weights['price'] * price_sim +
                weights['facilities'] * facility_sim
            )
            
            scores.append(score)
            
        return np.array(scores)


class CollaborativeFilter:
    """
    Collaborative filtering recommendation system that recommends warehouses based on
    tenant-warehouse interaction patterns.
    """
    def __init__(self):
        # tenant_id -> [warehouse_id1, warehouse_id2, ...]
        self.tenant_history: Dict[int, List[int]] = {}
        # warehouse_id -> [tenant_id1, tenant_id2, ...]
        self.warehouse_tenants: Dict[int, List[int]] = {}
        
    def add_tenant_warehouse_interaction(self, tenant_id: int, warehouse_id: int):
        """Record an interaction between a tenant and warehouse"""
        if tenant_id not in self.tenant_history:
            self.tenant_history[tenant_id] = []
        if warehouse_id not in self.warehouse_tenants:
            self.warehouse_tenants[warehouse_id] = []
            
        if warehouse_id not in self.tenant_history[tenant_id]:
            self.tenant_history[tenant_id].append(warehouse_id)
        if tenant_id not in self.warehouse_tenants[warehouse_id]:
            self.warehouse_tenants[warehouse_id].append(tenant_id)
    
    def find_similar_tenants(self, tenant_id: int, n: int = 5) -> List[Tuple[int, float]]:
        """
        Find top N tenants similar to the given tenant based on warehouse history
        
        Uses Jaccard similarity: the size of the intersection divided by the size of the union.
        Higher similarity means tenants have more warehouses in common compared to their total combined history.
        
        Examples:
        - If tenant A visited warehouses [1,2] and tenant B visited [1,3], similarity = 1/3 = 0.33
        - If tenant A visited warehouses [1,2] and tenant C visited [2], similarity = 1/2 = 0.5
        
        In these examples, tenant C would be considered more similar to tenant A than tenant B.
        """
        if tenant_id not in self.tenant_history or not self.tenant_history[tenant_id]:
            return []
            
        tenant_warehouses = set(self.tenant_history[tenant_id])
        similarities = []
        
        for other_id, other_warehouses in self.tenant_history.items():
            if other_id == tenant_id:
                continue
                
            other_set = set(other_warehouses)
            if not other_set:
                continue
                
            # Jaccard similarity: intersection / union
            intersection = len(tenant_warehouses.intersection(other_set))
            union = len(tenant_warehouses.union(other_set))
            
            if union > 0:
                similarity = intersection / union
                similarities.append((other_id, similarity))
                
        # Sort by similarity score (descending) and return top N
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:n]
    
    def recommend(self, tenant_id: int, available_warehouses: List[WarehouseBase], 
                  n_similar_tenants: int = 5) -> np.ndarray:
        """
        Generate recommendations using collaborative filtering
        
        Parameters:
        - tenant_id: ID of the tenant for whom recommendations are generated
        - available_warehouses: List of available warehouses to score
        - n_similar_tenants: Number of similar tenants to consider
        
        Returns:
        - Array of similarity scores for each warehouse
        """
        if not available_warehouses:
            return np.array([])
            
        # If tenant has no history, return neutral scores
        if tenant_id not in self.tenant_history or not self.tenant_history[tenant_id]:
            return np.full(len(available_warehouses), 0.5)
            
        # Find similar tenants
        similar_tenants = self.find_similar_tenants(tenant_id, n_similar_tenants)
        
        if not similar_tenants:
            return np.full(len(available_warehouses), 0.5)
            
        # Calculate scores for each warehouse
        warehouse_scores = {}
        available_ids = [w.id for w in available_warehouses]
        
        # Tenant's own history (negative bias for already visited warehouses)
        tenant_visited = set(self.tenant_history[tenant_id])
        
        for warehouse_id in available_ids:
            # Start with neutral score
            score = 0.5
            total_weight = 1.0
            
            # Adjust score based on similar tenants' history
            for similar_id, similarity in similar_tenants:
                if similar_id in self.tenant_history and warehouse_id in self.tenant_history[similar_id]:
                    # Positive influence from similar tenants
                    score += similarity 
                    total_weight += similarity
            
            # Normalize score
            warehouse_scores[warehouse_id] = score / total_weight
            
            # Apply small penalty for warehouses the tenant has already visited
            if warehouse_id in tenant_visited:
                warehouse_scores[warehouse_id] *= 0.9
                
        # Convert to ordered array matching available_warehouses order
        scores = [warehouse_scores.get(w_id, 0.5) for w_id in available_ids]
        return np.array(scores)


class HybridRecommender:
    """
    Hybrid recommendation system that combines content-based and collaborative filtering
    to provide the best of both approaches.
    """
    def __init__(self):
        self.content_based = ContentBasedFilter()
        self.collaborative = CollaborativeFilter()
        
    def recommend(self, 
                 warehouses: List[WarehouseBase], 
                 tenant: TenantBase,
                 tenant_id: Optional[int] = None,
                 weights: Dict[str, float] = None) -> np.ndarray:
        """
        Generate recommendations using a hybrid approach
        
        Parameters:
        - warehouses: List of available warehouses
        - tenant: Tenant for whom recommendations are generated
        - tenant_id: Optional ID of tenant for collaborative filtering
        - weights: Optional dictionary with weights for different algorithms
                 ('content_based', 'collaborative')
        
        Returns:
        - Array of similarity scores for each warehouse
        """
        if not warehouses:
            return np.array([])
            
        # Default weights
        if weights is None:
            weights = {
                'content_based': 0.7,
                'collaborative': 0.3
            }
            
        # Content-based scores
        content_scores = self.content_based.recommend(warehouses, tenant)
        
        # Collaborative scores (if tenant_id is provided)
        if tenant_id is not None:
            collab_scores = self.collaborative.recommend(tenant_id, warehouses)
            
            # Combine scores with weights
            final_scores = (
                weights['content_based'] * content_scores + 
                weights['collaborative'] * collab_scores
            )
        else:
            # If no tenant_id, use only content-based scores
            final_scores = content_scores
            
        return final_scores
        
    def add_interaction(self, tenant_id: int, warehouse_id: int):
        """Record an interaction to improve future collaborative recommendations"""
        self.collaborative.add_tenant_warehouse_interaction(tenant_id, warehouse_id) 