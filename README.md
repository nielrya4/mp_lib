# MP-Lib: Microplastics Analysis Library

A comprehensive Python library and command-line tool for microplastics data analysis, including distribution analysis, source unmixing, and multidimensional scaling.

## Features

### 📊 Distribution Analysis
- **Categorical PDFs and CDFs**: Analyze microplastics type distributions
- **Flexible plotting**: Overlay and stacked visualization options
- **Statistical summaries**: Comprehensive distribution statistics

### 🔬 Source Unmixing
- **Monte Carlo analysis**: Determine source contributions to mixed samples
- **Multiple metrics**: R², similarity, likeness, KS, Kuiper, chi-squared tests
- **Uncertainty quantification**: Confidence intervals for all estimates
- **Visualization**: Contribution plots and model fitting assessments

### 📈 Multidimensional Scaling (MDS)
- **Sample relationships**: Visualize similarities between samples in 2D space
- **Multiple distance metrics**: Choose appropriate similarity measures
- **Stress analysis**: Quality assessment of MDS representations
- **Interactive plots**: Nearest neighbor connections and custom styling

### 🖥️ Command-Line Interface
- **Easy-to-use CLI**: Run analyses from the command line
- **Batch processing**: Analyze multiple datasets efficiently
- **Export options**: High-quality plots and data tables
- **Cross-platform**: Works on Linux, macOS, and Windows

## Installation

### Quick Install (Recommended)

**Linux/macOS:**
```bash
curl -sSL https://raw.githubusercontent.com/nielrya4/mp_lib/main/install.sh | bash
```

**Windows PowerShell:**
```powershell
iwr -useb https://raw.githubusercontent.com/nielrya4/mp_lib/main/install.ps1 | iex
```

### Manual Installation

1. **Clone the repository:**
```bash
git clone https://github.com/nielrya4/mp_lib.git
cd mp_lib
```

2. **Install the package:**
```bash
pip install -e .
```

3. **Verify installation:**
```bash
mp-cli --help
```

## Quick Start

### Command Line Usage

```bash
# Get data information
mp-cli --input data.xlsx info --summary

# Distribution analysis
mp-cli --input data.xlsx dist --plot --cdf

# Source unmixing
mp-cli --input data.xlsx unmix --sources "Source1,Source2" --sink "Mixed" --metric r2

# MDS analysis
mp-cli --input data.xlsx mds --plot --metric similarity

# Complete analysis
mp-cli --input data.xlsx analyze --all --output results/
```

### Python Library Usage

```python
from mp_lib import read_excel_samples, monte_carlo_unmixing, mds_analysis

# Load data
samples = read_excel_samples('data.xlsx')

# Unmixing analysis
contributions, models = monte_carlo_unmixing(
    sink_distribution, source_distributions,
    metric='r2', n_trials=10000
)

# MDS analysis
points, stress = mds_analysis(samples, metric='similarity')
```

## Data Format

Input data should be in Excel format with:
- **location** column: Sample names/identifiers
- **Plastic type columns**: Particle counts for each plastic type

Example:

| location | Polyethylene | Polystyrene | Nylon | unknown |
|----------|--------------|-------------|-------|---------|
| Site A   | 45           | 23          | 12    | 156     |
| Site B   | 67           | 34          | 8     | 203     |

## Commands Reference

### Global Options
- `--input, -i`: Input Excel file (required)
- `--output, -o`: Output directory (default: mp_results)
- `--exclude`: Plastic types to exclude (default: unknown)
- `--verbose, -v`: Verbose output

### Commands

#### `info` - Data Information
```bash
mp-cli --input data.xlsx info --summary
```

#### `dist` - Distribution Analysis
```bash
mp-cli --input data.xlsx dist --plot --cdf --stacked --colormap viridis
```

#### `unmix` - Source Unmixing
```bash
mp-cli --input data.xlsx unmix \
  --sources "Source1,Source2,Source3" \
  --sink "Mixed" \
  --metric r2 \
  --trials 10000 \
  --plot
```

#### `mds` - Multidimensional Scaling
```bash
mp-cli --input data.xlsx mds \
  --metric similarity \
  --plot \
  --connections \
  --colormap viridis
```

#### `analyze` - Comprehensive Analysis
```bash
mp-cli --input data.xlsx analyze --all --output results/
```

## Metrics Available

### Similarity Metrics (higher = more similar)
- **R²**: Cross-correlation coefficient
- **Similarity**: Geometric mean-based measure
- **Likeness**: Complement of mismatch measure

### Distance Metrics (lower = more similar)
- **KS**: Kolmogorov-Smirnov test (uses CDFs)
- **Kuiper**: Kuiper test (uses CDFs)
- **Chi-squared**: Chi-squared test for categorical data

## Output Files

The CLI generates various output files:
- **Plots**: High-resolution PNG images (300 DPI)
- **Data**: CSV tables and JSON matrices
- **Summaries**: Text reports with statistics
- **Results**: Organized in output directories

## Dependencies

- Python 3.8+
- NumPy ≥ 1.20.0
- SciPy ≥ 1.7.0
- Matplotlib ≥ 3.4.0
- Pandas ≥ 1.3.0
- OpenPyXL ≥ 3.0.0
- Scikit-learn ≥ 1.0.0

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if needed
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Citation

If you use this software in your research, please cite:

```bibtex
@software{mp_lib,
  title={MP-Lib: Microplastics Analysis Library},
  author={Ryan Nielsen},
  year={2025},
  url={https://github.com/nielrya4/mp_lib}
}
```

## Support

- **Issues**: [GitHub Issues](https://github.com/nielrya4/mp_lib/issues)
- **Documentation**: [Wiki](https://github.com/nielrya4/mp_lib/wiki)
- **Examples**: [Examples Directory](https://github.com/nielrya4/mp_lib/tree/main/examples)

## Roadmap

- [ ] Web interface for analysis
- [ ] Additional statistical tests
- [ ] Machine learning integration
- [ ] Real-time data processing
- [ ] Integration with laboratory instruments