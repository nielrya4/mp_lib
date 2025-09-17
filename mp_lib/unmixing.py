"""
Unmixing module for microplastics source apportionment.
Uses Monte Carlo modeling to determine source contributions to mixed samples.
"""
import numpy as np
import pandas as pd
import random
from typing import List, Tuple
import matplotlib.pyplot as plt
from . import metrics


class Contribution:
    """Represents a source contribution with uncertainty."""
    
    def __init__(self, name: str, contribution: float, standard_deviation: float):
        """
        Initialize a contribution.
        
        Parameters:
            name: Source name
            contribution: Mean contribution percentage
            standard_deviation: Standard deviation of contribution
        """
        self.name = name
        self.contribution = contribution
        self.standard_deviation = standard_deviation
    
    def __str__(self):
        return f"{self.name}: {self.contribution:.1f}% ± {self.standard_deviation:.1f}%"
    
    def __repr__(self):
        return self.__str__()


class UnmixingTrial:
    """Single trial of Monte Carlo unmixing."""
    
    def __init__(self, sink_distribution: np.ndarray, source_distributions: List[np.ndarray], 
                 metric: str = "r2"):
        """
        Initialize an unmixing trial.
        
        Parameters:
            sink_distribution: Target distribution to unmix
            source_distributions: List of potential source distributions
            metric: Similarity metric to use ("r2", "ks", "kuiper", "similarity", "likeness")
        """
        self.sink_distribution = sink_distribution
        self.source_distributions = source_distributions
        self.metric = metric
        self.random_configuration, self.model_distribution, self.test_val = self._do_trial()
    
    def _do_trial(self):
        """Perform a single unmixing trial."""
        sink = self.sink_distribution
        sources = self.source_distributions
        n_sources = len(sources)
        
        # Generate random mixing proportions
        proportions = self._make_random_proportions(n_sources)
        
        # Create mixed model
        model = np.zeros_like(sink)
        for j, source in enumerate(sources):
            model += source * proportions[j]
        
        # Calculate similarity metric
        if self.metric == "r2":
            val = metrics.r2(sink, model)
        elif self.metric == "ks":
            val = metrics.ks(sink, model)
        elif self.metric == "kuiper":
            val = metrics.kuiper(sink, model)
        elif self.metric == "similarity":
            val = metrics.similarity(sink, model)
        elif self.metric == "likeness":
            val = metrics.likeness(sink, model)
        elif self.metric == "chi_squared":
            val = metrics.chi_squared(sink, model)
        else:
            raise ValueError(f"Unknown metric '{self.metric}'")
        
        return proportions, model, val
    
    @staticmethod
    def _make_random_proportions(num_sources: int) -> np.ndarray:
        """Generate random proportions that sum to 1."""
        rands = [random.random() for _ in range(num_sources)]
        total = sum(rands)
        proportions = np.array([rand / total for rand in rands])
        return proportions


def monte_carlo_unmixing(sink_distribution, 
                        source_distributions: List,
                        n_trials: int = 10000,
                        metric: str = "r2") -> Tuple[List[Contribution], List[np.ndarray]]:
    """
    Perform Monte Carlo unmixing analysis.
    
    Parameters:
        sink_distribution: Sink Distribution object to unmix
        source_distributions: List of potential source Distribution objects
        n_trials: Number of Monte Carlo trials
        metric: Similarity metric ("r2", "ks", "kuiper", "similarity", "likeness")
        
    Returns:
        Tuple of (contributions, top_model_distributions)
    """
    print(f"Running {n_trials} Monte Carlo trials using {metric} metric...")
    
    # Extract y_values from Distribution objects
    sink_y = sink_distribution.y_values
    source_y_values = [source.y_values for source in source_distributions]
    source_names = [source.name for source in source_distributions]
    
    # Run trials
    trials = []
    for i in range(n_trials):
        if i % 1000 == 0:
            print(f"  Trial {i}/{n_trials}")
        trial = UnmixingTrial(sink_y, source_y_values, metric)
        trials.append(trial)
    
    # Sort trials by goodness of fit
    if metric in ["r2", "similarity", "likeness"]:
        # Higher is better
        sorted_trials = sorted(trials, key=lambda x: x.test_val, reverse=True)
    elif metric in ["ks", "kuiper", "chi_squared"]:
        # Lower is better
        sorted_trials = sorted(trials, key=lambda x: x.test_val, reverse=False)
    else:
        raise ValueError(f"Unknown metric '{metric}'")
    
    # Take top 10% of trials
    n_top = max(10, n_trials // 100)
    top_trials = sorted_trials[:n_top]
    
    # Extract results
    top_configurations = [trial.random_configuration for trial in top_trials]
    top_models = [trial.model_distribution for trial in top_trials]
    
    # Calculate statistics
    source_contributions = np.mean(top_configurations, axis=0) * 100
    source_std = np.std(top_configurations, axis=0) * 100
    
    # Create Contribution objects
    contributions = []
    for i, name in enumerate(source_names):
        contrib = Contribution(name, source_contributions[i], source_std[i])
        contributions.append(contrib)
    
    print(f"Best fit score: {sorted_trials[0].test_val:.4f}")
    print("Source contributions:")
    for contrib in contributions:
        print(f"  {contrib}")
    
    return contributions, top_models


def relative_contribution_graph(contributions: List[Contribution],
                               title: str = "Source Contributions",
                               font_size: float = 12,
                               fig_width: float = 9,
                               fig_height: float = 7) -> plt.Figure:
    """
    Create bar chart of source contributions with error bars.
    
    Parameters:
        contributions: List of Contribution objects
        title: Plot title
        font_size: Base font size
        fig_width: Figure width
        fig_height: Figure height
        
    Returns:
        Matplotlib figure
    """
    sample_names = [contrib.name for contrib in contributions]
    x = np.arange(len(contributions))
    y = [contrib.contribution for contrib in contributions]
    e = [contrib.standard_deviation for contrib in contributions]
    
    fig, ax = plt.subplots(figsize=(fig_width, fig_height), dpi=100)
    
    bars = ax.bar(x, y, yerr=e, capsize=5, alpha=0.7, color='skyblue', edgecolor='navy')
    
    ax.set_title(title, fontsize=font_size * 1.5)
    ax.set_xlabel("Source", fontsize=font_size)
    ax.set_ylabel("Contribution (%)", fontsize=font_size)
    ax.set_xticks(x)
    ax.set_xticklabels(sample_names, rotation=45, ha='right', fontsize=font_size)
    ax.grid(True, alpha=0.3)
    
    # Add value labels on bars
    for i, (bar, val, err) in enumerate(zip(bars, y, e)):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + err + 1,
                f'{val:.1f}%', ha='center', va='bottom', fontsize=font_size-1)
    
    plt.tight_layout()
    return fig


def relative_contribution_table(contributions: List[Contribution],
                               metric: str = "r2",
                               title: str = "Source Contribution Analysis") -> pd.DataFrame:
    """
    Create table of source contributions.
    
    Parameters:
        contributions: List of Contribution objects
        metric: Metric used for analysis
        title: Table title
        
    Returns:
        Pandas DataFrame
    """
    sample_names = [contrib.name for contrib in contributions]
    percent_contributions = [contrib.contribution for contrib in contributions]
    standard_deviations = [contrib.standard_deviation for contrib in contributions]
    
    data = {
        f"% Contribution (metric={metric})": percent_contributions,
        "Standard Deviation": standard_deviations
    }
    
    df = pd.DataFrame(data, index=sample_names)
    df.index.name = "Source Sample"
    
    return df


def top_trials_graph(sink_distribution: np.ndarray,
                    model_distributions: List[np.ndarray],
                    x_labels: List[str],
                    title: str = "Best Fit Models vs Sink",
                    font_size: float = 12,
                    fig_width: float = 12,
                    fig_height: float = 8) -> plt.Figure:
    """
    Plot sink distribution vs best fitting model distributions.
    
    Parameters:
        sink_distribution: Sink distribution
        model_distributions: List of best model distributions
        x_labels: Category labels for x-axis
        title: Plot title
        font_size: Base font size
        fig_width: Figure width
        fig_height: Figure height
        
    Returns:
        Matplotlib figure
    """
    fig, ax = plt.subplots(figsize=(fig_width, fig_height), dpi=100)
    
    x = np.arange(len(x_labels))
    
    # Plot model distributions (top trials)
    for i, model in enumerate(model_distributions[:10]):  # Show top 10
        alpha = 0.3 if i > 0 else 0.5
        label = "Best Fit Models" if i == 0 else "_nolegend_"
        ax.plot(x, model, 'c-', alpha=alpha, linewidth=1, label=label)
    
    # Plot sink distribution
    ax.plot(x, sink_distribution, 'b-', linewidth=3, label="Sink Sample", marker='o')
    
    ax.set_title(title, fontsize=font_size * 1.5)
    ax.set_xlabel("Plastic Type", fontsize=font_size)
    ax.set_ylabel("Probability", fontsize=font_size)
    ax.set_xticks(x)
    ax.set_xticklabels(x_labels, rotation=45, ha='right', fontsize=font_size)
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    return fig