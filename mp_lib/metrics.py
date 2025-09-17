"""
Metrics module for comparing microplastics distributions.
Adapted from dz_lib metrics for categorical/discrete data analysis.
"""
import numpy as np


def ks(y1_values, y2_values):
    """
    Kolmogorov-Smirnov test statistic.
    Maximum absolute difference between two CDF curves.
    
    Parameters:
        y1_values: First distribution values (CDF or PDF)
        y2_values: Second distribution values (CDF or PDF)
        
    Returns:
        KS test statistic (0-1, lower is more similar)
    """
    y1 = np.array(y1_values)
    y2 = np.array(y2_values)
    
    # If inputs are PDFs, convert to CDFs
    if np.max(y1) <= 1.0 and np.max(y2) <= 1.0 and not _is_cdf(y1) and not _is_cdf(y2):
        y1 = np.cumsum(y1) / np.sum(y1)
        y2 = np.cumsum(y2) / np.sum(y2)
    
    d_val = np.max(np.abs(y1 - y2))
    return d_val


def kuiper(y1_values, y2_values):
    """
    Kuiper test statistic.
    Sum of max differences in both directions between CDFs.
    
    Parameters:
        y1_values: First distribution values (CDF or PDF)
        y2_values: Second distribution values (CDF or PDF)
        
    Returns:
        Kuiper test statistic (0-2, lower is more similar)
    """
    y1 = np.array(y1_values)
    y2 = np.array(y2_values)
    
    # If inputs are PDFs, convert to CDFs
    if np.max(y1) <= 1.0 and np.max(y2) <= 1.0 and not _is_cdf(y1) and not _is_cdf(y2):
        y1 = np.cumsum(y1) / np.sum(y1)
        y2 = np.cumsum(y2) / np.sum(y2)
    
    v_val = np.max(y1 - y2) + np.max(y2 - y1)
    return v_val


def similarity(y1_values, y2_values):
    """
    Similarity metric based on geometric mean.
    Sum of geometric means at each point.
    
    Parameters:
        y1_values: First distribution values
        y2_values: Second distribution values
        
    Returns:
        Similarity score (0-1, higher is more similar)
    """
    y1 = np.array(y1_values)
    y2 = np.array(y2_values)
    
    # Normalize to ensure they sum to 1
    y1 = y1 / np.sum(y1)
    y2 = y2 / np.sum(y2)
    
    similarity_val = np.sum(np.sqrt(y1 * y2))
    return similarity_val


def likeness(y1_values, y2_values):
    """
    Likeness metric (complement of mismatch).
    1 minus half the sum of absolute differences.
    
    Parameters:
        y1_values: First distribution values
        y2_values: Second distribution values
        
    Returns:
        Likeness score (0-1, higher is more similar)
    """
    y1 = np.array(y1_values)
    y2 = np.array(y2_values)
    
    # Normalize to ensure they sum to 1
    y1 = y1 / np.sum(y1)
    y2 = y2 / np.sum(y2)
    
    likeness_val = 1 - np.sum(np.abs(y1 - y2)) / 2
    return likeness_val


def r2(y1_values, y2_values):
    """
    Cross-correlation (R-squared).
    Coefficient of determination between two distributions.
    
    Parameters:
        y1_values: First distribution values
        y2_values: Second distribution values
        
    Returns:
        R-squared value (0-1, higher is more similar)
    """
    y1 = np.array(y1_values)
    y2 = np.array(y2_values)
    
    correlation_matrix = np.corrcoef(y1, y2)
    correlation_xy = correlation_matrix[0, 1]
    
    # Handle NaN case (when one or both arrays have zero variance)
    if np.isnan(correlation_xy):
        return 0.0
    
    cross_correlation = correlation_xy ** 2
    return cross_correlation


def chi_squared(y1_values, y2_values):
    """
    Chi-squared test statistic for categorical data.
    Measures goodness of fit between observed and expected frequencies.
    
    Parameters:
        y1_values: Observed frequencies
        y2_values: Expected frequencies
        
    Returns:
        Chi-squared statistic (0+, lower is more similar)
    """
    observed = np.array(y1_values)
    expected = np.array(y2_values)
    
    # Normalize to same total
    total_obs = np.sum(observed)
    total_exp = np.sum(expected)
    if total_exp > 0:
        expected = expected * (total_obs / total_exp)
    
    # Avoid division by zero
    expected = np.where(expected == 0, 1e-10, expected)
    
    chi2 = np.sum((observed - expected) ** 2 / expected)
    return chi2


# Distance/dissimilarity versions (higher = more different)
def dis_similarity(y1_values, y2_values):
    """Dissimilarity (1 - similarity)."""
    return 1.0 - similarity(y1_values, y2_values)


def dis_ks(y1_values, y2_values):
    """Inverted KS statistic (1 - ks)."""
    return 1.0 - ks(y1_values, y2_values)


def dis_kuiper(y1_values, y2_values):
    """Inverted Kuiper statistic (1 - kuiper/2)."""
    return 1.0 - kuiper(y1_values, y2_values) / 2


def dis_likeness(y1_values, y2_values):
    """Dissimilarity (1 - likeness)."""
    return 1.0 - likeness(y1_values, y2_values)


def dis_r2(y1_values, y2_values):
    """Inverted R-squared (1 - r2)."""
    return 1.0 - r2(y1_values, y2_values)


def _is_cdf(values):
    """Check if values represent a CDF (monotonically increasing)."""
    return np.all(np.diff(values) >= 0) and values[-1] <= 1.1  # Allow slight numerical error