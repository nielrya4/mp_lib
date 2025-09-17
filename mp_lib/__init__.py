"""mp_lib package for microplastics analysis."""

import pandas as pd
from typing import List
from .distributions import categorical_distribution, categorical_cdf, cdf_function, Distribution, distribution_graph
from . import metrics
from .unmixing import Contribution, monte_carlo_unmixing, relative_contribution_graph, relative_contribution_table, top_trials_graph
from .mds import MDSPoint, mds_analysis, mds_graph, stress_interpretation, mds_summary_table

class Sample:
    """Represents a microplastics sample with location and particle counts."""
    
    def __init__(self, name: str, plastic_counts: dict):
        """
        Initialize a sample.
        
        Parameters:
            name: Sample location/identifier
            plastic_counts: Dictionary mapping plastic type to particle count
        """
        self.name = name
        self.plastic_counts = plastic_counts
    
    def total_particles(self) -> int:
        """Return total number of particles in the sample."""
        return sum(self.plastic_counts.values())
    
    def get_plastic_types(self) -> list:
        """Return list of plastic types found in the sample."""
        return list(self.plastic_counts.keys())
    
    def get_count(self, plastic_type: str) -> int:
        """Return count for a specific plastic type."""
        return self.plastic_counts.get(plastic_type, 0)
    
    def __str__(self):
        return f"Sample({self.name}, {self.total_particles()} particles)"
    
    def __repr__(self):
        return self.__str__()


def read_excel_samples(file_path: str) -> List[Sample]:
    """
    Read Excel file and create Sample objects for each location.
    
    Parameters:
        file_path: Path to Excel file with microplastics data
        
    Returns:
        List of Sample objects
    """
    df = pd.read_excel(file_path)
    samples = []
    
    for _, row in df.iterrows():
        location = row['location']
        plastic_counts = {}
        
        # Extract all plastic columns (excluding location)
        for col in df.columns:
            if col != 'location':
                plastic_counts[col] = row[col]
        
        samples.append(Sample(location, plastic_counts))
    
    return samples