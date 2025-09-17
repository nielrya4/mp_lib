import numpy as np
import matplotlib.pyplot as plt
from typing import List, Tuple, Optional


def plot_ternary_diagram(
        component_names: Tuple[str, str, str],
        component_1: List[float],
        component_2: List[float],
        component_3: List[float],
        labels: Optional[List[str]] = None,
        steps: int = 5,
        title: str = "Ternary Diagram",
        point_color: str = 'red',
        component_colors: Tuple[str, str, str] = ('red', 'green', 'blue'),
        annotate: bool = True):
    """
    Plot a ternary diagram from three component arrays (e.g., sand, silt, clay).
    Each component has its own color for gridlines and text.
    """
    a = np.array(component_1, dtype=float)
    b = np.array(component_2, dtype=float)
    c = np.array(component_3, dtype=float)

    total = a + b + c
    valid = total > 0
    a, b, c = a[valid], b[valid], c[valid]
    total = total[valid]

    a /= total
    b /= total
    c /= total

    x = 0.5 * (2 * b + c)
    y = (np.sqrt(3) / 2) * c

    A = np.array([0.5, np.sqrt(3) / 2])  # Corner 3 (component_3)
    B = np.array([0, 0])  # Corner 1 (component_1)
    C = np.array([1, 0])  # Corner 2 (component_2)

    fig, ax = plt.subplots(figsize=(6, 6))

    # Triangle outline in black
    ax.plot([A[0], B[0]], [A[1], B[1]], 'k-', lw=1.5)
    ax.plot([B[0], C[0]], [B[1], C[1]], 'k-', lw=1.5)
    ax.plot([C[0], A[0]], [C[1], A[1]], 'k-', lw=1.5)

    # Colored gridlines for each component
    for i in range(1, steps):
        f = i / steps

        # Component 1 gridlines (parallel to side BC, opposite to corner B)
        x1, y1 = 0.5 * (2 * (1 - f)), 0
        x2, y2 = 0.5 * (1 - f), (np.sqrt(3) / 2) * (1 - f)
        ax.plot([x1, x2], [y1, y2], color=component_colors[0], linestyle=':', lw=0.8, alpha=1)

        # Component 2 gridlines (parallel to side AC, opposite to corner C)
        x1, y1 = 0.5 * f, (np.sqrt(3) / 2) * f
        x2, y2 = 0.5 * (2 * (1 - f) + f), (np.sqrt(3) / 2) * f
        ax.plot([x1, x2], [y1, y2], color=component_colors[2], linestyle=':', lw=0.8, alpha=1)

        # Component 3 gridlines (parallel to side AB, opposite to corner A)
        x1, y1 = 0.5 * (2 * f), 0
        x2, y2 = 0.5 * (2 * f + (1 - f)), (np.sqrt(3) / 2) * (1 - f)
        ax.plot([x1, x2], [y1, y2], color=component_colors[1], linestyle=':', lw=0.8, alpha=1)

    # Plot data points
    ax.scatter(x, y, s=70, color=point_color, alpha=0.8, edgecolor='black')

    # Annotate points if requested
    if annotate and labels:
        valid_labels = [labels[i] for i in range(len(labels)) if valid[i]]
        for i in range(min(len(x), len(valid_labels))):
            ax.annotate(valid_labels[i], (x[i], y[i]), xytext=(4, 4),
                        textcoords='offset points', fontsize=7)

    # Corner labels with component colors
    ax.text(B[0], B[1] - 0.07, component_names[0], ha='center', va='top',
            fontsize=10, fontweight='bold', color=component_colors[0])
    ax.text(C[0], C[1] - 0.07, component_names[1], ha='center', va='top',
            fontsize=10, fontweight='bold', color=component_colors[1])
    ax.text(A[0], A[1] + 0.05, component_names[2], ha='center', va='bottom',
            fontsize=10, fontweight='bold', color=component_colors[2])

    # Edge percentage labels with component colors
    percentages = [20, 40, 60, 80]
    for i, pct in enumerate(percentages):
        f = (i + 1) / steps

        # Component 1 percentages (along BC edge)
        edge_point = (1 - f) * B + f * C
        ax.text(edge_point[0], edge_point[1] - 0.03, f"{pct}%",
                ha='center', va='top', fontsize=8, alpha=1, color=component_colors[1])

        # Component 3 percentages (along AB edge)
        edge_point = (1 - f) * A + f * B
        ax.text(edge_point[0] - 0.02, edge_point[1] + 0.01, f"{pct}%",
                ha='right', va='bottom', fontsize=8, alpha=1, rotation=60, color=component_colors[0])

        # Component 2 percentages (along AC edge)
        comp2_pct = 100 - pct
        edge_point = (1 - f) * A + f * C
        ax.text(edge_point[0] + 0.02, edge_point[1] + 0.01, f"{comp2_pct}%",
                ha='left', va='bottom', fontsize=8, alpha=1, rotation=-60, color=component_colors[2])

    # Title
    ax.text(0.5, np.sqrt(3) / 2 + 0.12, title, ha='center', va='bottom',
            fontsize=12, fontweight='bold')

    ax.set_aspect('equal')
    ax.axis('off')
    fig.tight_layout()

    return fig