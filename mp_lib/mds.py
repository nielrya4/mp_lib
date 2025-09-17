"""
Multidimensional Scaling (MDS) module for microplastics analysis.
Creates 2D representations of sample relationships based on distribution similarities.
"""
import numpy as np
import matplotlib.pyplot as plt
from sklearn.manifold import MDS
from typing import List, Tuple, Optional
from . import metrics
from .distributions import categorical_distribution, categorical_cdf


class MDSPoint:
    """Represents a point in MDS space with nearest neighbor information."""
    
    def __init__(self, x: float, y: float, label: str, 
                 nearest_neighbor: Optional[Tuple[float, float]] = None):
        """
        Initialize an MDS point.
        
        Parameters:
            x: X coordinate in MDS space
            y: Y coordinate in MDS space
            label: Sample label/name
            nearest_neighbor: Coordinates of nearest neighbor point
        """
        self.x = x
        self.y = y
        self.label = label
        self.nearest_neighbor = nearest_neighbor
    
    def __str__(self):
        return f"MDSPoint({self.label}: ({self.x:.3f}, {self.y:.3f}))"
    
    def __repr__(self):
        return self.__str__()


def mds_analysis(samples: List, metric: str = "similarity", 
                exclude_plastics: List[str] = None) -> Tuple[List[MDSPoint], float]:
    """
    Perform MDS analysis on microplastics samples.
    
    Parameters:
        samples: List of Sample objects
        metric: Distance metric ("similarity", "likeness", "r2", "ks", "kuiper")
        exclude_plastics: List of plastic types to exclude from analysis
        
    Returns:
        Tuple of (MDS points, stress value)
    """
    if exclude_plastics is None:
        exclude_plastics = ['unknown']
    
    print(f"Performing MDS analysis with {metric} metric...")
    print(f"Excluding plastic types: {exclude_plastics}")
    
    # Prepare distributions
    sample_names = [sample.name for sample in samples]
    n_samples = len(samples)
    
    # Create probability distributions
    prob_distributions = []
    cdf_distributions = []
    
    for sample in samples:
        # Filter plastic counts
        filtered_counts = {}
        for plastic_type, count in sample.plastic_counts.items():
            if plastic_type not in exclude_plastics:
                filtered_counts[plastic_type] = count
        
        # Create distributions
        if filtered_counts:
            _, y_vals = categorical_distribution(filtered_counts)
            prob_distributions.append(y_vals)
            
            _, cdf_vals = categorical_cdf(filtered_counts)
            cdf_distributions.append(cdf_vals)
        else:
            raise ValueError(f"Sample {sample.name} has no valid plastic types after filtering")
    
    # Calculate dissimilarity matrix
    print("Calculating dissimilarity matrix...")
    dissimilarity_matrix = np.zeros((n_samples, n_samples))
    
    for i in range(n_samples):
        for j in range(i + 1, n_samples):
            if metric == "similarity":
                dissim = metrics.dis_similarity(prob_distributions[i], prob_distributions[j])
            elif metric == "likeness":
                dissim = metrics.dis_likeness(prob_distributions[i], prob_distributions[j])
            elif metric == "r2" or metric == "cross_correlation":
                dissim = metrics.dis_r2(prob_distributions[i], prob_distributions[j])
            elif metric == "ks":
                dissim = metrics.ks(cdf_distributions[i], cdf_distributions[j])
            elif metric == "kuiper":
                dissim = metrics.kuiper(cdf_distributions[i], cdf_distributions[j])
            else:
                raise ValueError(f"Unknown metric '{metric}'")
            
            dissimilarity_matrix[i, j] = dissim
            dissimilarity_matrix[j, i] = dissim
    
    # Perform MDS
    print("Performing MDS transformation...")
    mds_model = MDS(n_components=2, dissimilarity='precomputed', random_state=42)
    mds_coordinates = mds_model.fit_transform(dissimilarity_matrix)
    
    # Find nearest neighbors and create MDS points
    print("Finding nearest neighbors...")
    points = []
    
    for i in range(n_samples):
        # Find nearest neighbor
        min_distance = float('inf')
        nearest_idx = None
        
        for j in range(n_samples):
            if i != j:
                distance = dissimilarity_matrix[i, j]
                if distance < min_distance:
                    min_distance = distance
                    nearest_idx = j
        
        # Create MDS point
        x1, y1 = mds_coordinates[i]
        if nearest_idx is not None:
            x2, y2 = mds_coordinates[nearest_idx]
            nearest_neighbor = (x2, y2)
        else:
            nearest_neighbor = None
        
        point = MDSPoint(x1, y1, sample_names[i], nearest_neighbor)
        points.append(point)
    
    stress = mds_model.stress_
    print(f"MDS stress: {stress:.4f}")
    
    return points, stress


def mds_graph(points: List[MDSPoint],
              title: str = "MDS Analysis",
              font_size: float = 12,
              fig_width: float = 9,
              fig_height: float = 7,
              color_map: str = 'viridis',
              show_connections: bool = True,
              show_labels: bool = True) -> plt.Figure:
    """
    Create MDS visualization plot.
    
    Parameters:
        points: List of MDSPoint objects
        title: Plot title
        font_size: Base font size
        fig_width: Figure width
        fig_height: Figure height
        color_map: Matplotlib colormap name
        show_connections: Whether to show nearest neighbor connections
        show_labels: Whether to show sample labels
        
    Returns:
        Matplotlib figure
    """
    n_samples = len(points)
    colors_map = plt.cm.get_cmap(color_map, n_samples)
    colors = colors_map(np.linspace(0, 1, n_samples))
    
    fig, ax = plt.subplots(figsize=(fig_width, fig_height), dpi=100)
    
    # Plot points and connections
    for i, point in enumerate(points):
        x1, y1 = point.x, point.y
        
        # Plot point
        ax.scatter(x1, y1, color=colors[i], s=100, alpha=0.8, edgecolors='black', linewidth=1)
        
        # Add label
        if show_labels:
            ax.annotate(point.label, (x1, y1), xytext=(5, 5), 
                       textcoords='offset points', fontsize=font_size-2, 
                       ha='left', va='bottom', 
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.7))
        
        # Draw connection to nearest neighbor
        if show_connections and point.nearest_neighbor is not None:
            x2, y2 = point.nearest_neighbor
            ax.plot([x1, x2], [y1, y2], 'k--', linewidth=1, alpha=0.5)
    
    # Customize plot
    ax.set_title(title, fontsize=font_size * 1.5, pad=20)
    ax.set_xlabel('MDS Dimension 1', fontsize=font_size)
    ax.set_ylabel('MDS Dimension 2', fontsize=font_size)
    ax.grid(True, alpha=0.3)
    
    # Equal aspect ratio for better interpretation
    ax.set_aspect('equal', adjustable='box')
    
    plt.tight_layout()
    return fig


def stress_interpretation(stress: float) -> str:
    """
    Provide interpretation of MDS stress value.
    
    Parameters:
        stress: MDS stress value
        
    Returns:
        Interpretation string
    """
    if stress < 0.05:
        return "Excellent representation"
    elif stress < 0.10:
        return "Good representation"
    elif stress < 0.20:
        return "Fair representation"
    else:
        return "Poor representation"


def mds_summary_table(points: List[MDSPoint], stress: float) -> str:
    """
    Create a summary table of MDS results.
    
    Parameters:
        points: List of MDSPoint objects
        stress: MDS stress value
        
    Returns:
        Formatted summary string
    """
    summary = f"""
MDS Analysis Summary
{'='*50}
Number of samples: {len(points)}
Stress value: {stress:.4f} ({stress_interpretation(stress)})

Sample Coordinates:
{'-'*30}
"""
    
    for point in points:
        summary += f"{point.label:15} ({point.x:6.3f}, {point.y:6.3f})\n"
    
    return summary