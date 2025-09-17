import numpy as np
from typing import List
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec



def categorical_distribution(category_counts: dict):
    """
    Create a categorical distribution from category counts.
    
    Parameters:
        category_counts: Dictionary mapping category names to counts
        
    Returns:
        categories: Array of category names (sorted)
        probabilities: Array of probabilities for each category
    """
    categories = sorted(category_counts.keys())
    counts = np.array([category_counts[cat] for cat in categories])
    total = counts.sum()
    
    if total == 0:
        probabilities = np.zeros_like(counts, dtype=float)
    else:
        probabilities = counts / total
    
    return np.array(categories), probabilities


def categorical_cdf(category_counts: dict):
    """
    Create a categorical cumulative distribution function from category counts.
    
    Parameters:
        category_counts: Dictionary mapping category names to counts
        
    Returns:
        categories: Array of category names (sorted)
        cdf_values: Array of cumulative probabilities for each category
    """
    categories = sorted(category_counts.keys())
    counts = np.array([category_counts[cat] for cat in categories])
    total = counts.sum()
    
    if total == 0:
        probabilities = np.zeros_like(counts, dtype=float)
    else:
        probabilities = counts / total
    
    # Calculate cumulative distribution
    cdf_values = np.cumsum(probabilities)
    
    return np.array(categories), cdf_values


class Distribution:
    """Represents a microplastics distribution with x and y values."""
    
    def __init__(self, name: str, x_values, y_values):
        """
        Initialize a distribution.
        
        Parameters:
            name: Sample or distribution name
            x_values: X-axis values (categories or numerical)
            y_values: Y-axis values (probabilities/densities)
        """
        self.name = name
        self.x_values = x_values
        self.y_values = y_values
    
    def subset(self, categories: List[str] = None):
        """
        Create a subset of the distribution with only specified categories.
        
        Parameters:
            categories: List of categories to include
            
        Returns:
            New Distribution object with filtered data
        """
        if categories is None:
            return Distribution(self.name, self.x_values, self.y_values)
        
        # For categorical data
        if isinstance(self.x_values[0], str):
            mask = np.isin(self.x_values, categories)
            new_x = self.x_values[mask]
            new_y = self.y_values[mask]
        else:
            # For numerical data, just return as-is
            new_x = self.x_values
            new_y = self.y_values
            
        return Distribution(self.name, new_x, new_y)


def cdf_function(distribution: Distribution):
    """
    Convert a Distribution object to its cumulative distribution function.
    
    Parameters:
        distribution: Distribution object
        
    Returns:
        New Distribution object with CDF values
    """
    x_values = distribution.x_values
    y_values = distribution.y_values
    name = distribution.name
    
    # Calculate cumulative distribution
    cdf_values = np.cumsum(y_values)
    if cdf_values[-1] > 0:
        cdf_values = cdf_values / cdf_values[-1]  # Normalize to ensure it ends at 1
    
    return Distribution(f"{name} (CDF)", x_values, cdf_values)


def distribution_graph(
        distributions: List[Distribution],
        stacked: bool = False,
        legend: bool = True,
        title: str = None,
        font_size: float = 12,
        fig_width: float = 9,
        fig_height: float = 7,
        color_map: str = 'viridis',
        x_label: str = 'Plastic Type',
        y_label: str = 'Probability',
        show_markers: bool = True,
        alpha: float = 0.8,
        line_width: float = 2
):
    """
    Create flexible plots for microplastics distributions.
    
    Parameters:
        distributions: List of Distribution objects to plot
        stacked: If True, create separate subplots for each distribution
        legend: Whether to show legend
        title: Overall plot title
        font_size: Base font size
        fig_width: Figure width in inches
        fig_height: Figure height in inches
        color_map: Matplotlib colormap name
        x_label: X-axis label
        y_label: Y-axis label
        show_markers: Whether to show markers on lines
        alpha: Line transparency
        line_width: Line width
        
    Returns:
        Matplotlib figure object
    """
    num_samples = len(distributions)
    colors_map = plt.cm.get_cmap(color_map, num_samples)
    colors = colors_map(np.linspace(0, 1, num_samples))

    if not stacked:
        # Single plot with all distributions overlaid
        fig, ax = plt.subplots(figsize=(fig_width, fig_height), dpi=100)
        
        for i, distribution in enumerate(distributions):
            x = distribution.x_values
            y = distribution.y_values
            
            # Plot with markers for categorical data, lines for continuous
            if isinstance(x[0], str):
                ax.plot(x, y, label=distribution.name, color=colors[i], 
                       linewidth=line_width, alpha=alpha, 
                       marker='o' if show_markers else None, markersize=6)
            else:
                ax.plot(x, y, label=distribution.name, color=colors[i], 
                       linewidth=line_width, alpha=alpha)
        
        if legend:
            ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
        
        ax.set_xlabel(x_label, fontsize=font_size)
        ax.set_ylabel(y_label, fontsize=font_size)
        ax.grid(True, alpha=0.3)
        
        # Rotate x-axis labels for categorical data
        if distributions and isinstance(distributions[0].x_values[0], str):
            plt.xticks(rotation=45, ha='right')
        
        ax_list = [ax]
    
    else:
        # Stacked subplots
        fig = plt.figure(figsize=(fig_width, fig_height), dpi=100)
        gs = gridspec.GridSpec(len(distributions), 1, figure=fig, 
                              height_ratios=[1] * len(distributions))
        ax_list = []
        
        for i, distribution in enumerate(distributions):
            ax = fig.add_subplot(gs[i])
            ax_list.append(ax)
            
            x = distribution.x_values
            y = distribution.y_values
            
            # Plot with appropriate style
            if isinstance(x[0], str):
                ax.plot(x, y, label=distribution.name, color=colors[i],
                       linewidth=line_width, alpha=alpha,
                       marker='o' if show_markers else None, markersize=6)
            else:
                ax.plot(x, y, label=distribution.name, color=colors[i],
                       linewidth=line_width, alpha=alpha)
            
            if legend:
                ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
            
            ax.set_ylabel(y_label, fontsize=font_size)
            ax.grid(True, alpha=0.3)
            
            # Only rotate labels on bottom plot
            if i == len(distributions) - 1:
                ax.set_xlabel(x_label, fontsize=font_size)
                if isinstance(x[0], str):
                    plt.xticks(rotation=45, ha='right')
            else:
                ax.set_xticklabels([])

    # Set overall title
    if title:
        title_size = font_size * 1.5
        fig.suptitle(title, fontsize=title_size)

    fig.tight_layout(rect=[0.025, 0.025, 0.975, 0.95])
    
    return fig

def __plot_dist(
        x_vals: List[float],
        y_vals: List[float],
        x_label: str = "",
        y_label: str = "",
        title: str = "") -> plt.Figure:
    """
    Plot a distribution and return the figure and axis for further customization.

    Parameters:
        x_vals: X-axis values.
        y_vals: Y-axis values.
        x_label: Label for X-axis.
        y_label: Label for Y-axis.
        title: Plot title and legend label.

    Returns:
        fig: Matplotlib figure.
    """
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(x_vals, y_vals, label=title if title else None, color='blue', lw=2)

    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)

    if title:
        ax.set_title(title)
        ax.legend()

    ax.grid(True, linestyle='--', alpha=0.6)
    fig.tight_layout()
    return fig