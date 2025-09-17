#!/usr/bin/env python3
"""
MP-CLI: Command-line tool for microplastics analysis using mp_lib.

A comprehensive tool for analyzing microplastics data including:
- Distribution analysis (PDF, CDF)
- Source unmixing with multiple metrics
- Multidimensional scaling (MDS)
- Data visualization and export
"""

import argparse
import sys
import os
import json
from pathlib import Path
import numpy as np

# Import mp_lib modules
from mp_lib import (
    read_excel_samples, categorical_distribution, categorical_cdf, cdf_function,
    Distribution, distribution_graph, monte_carlo_unmixing, 
    relative_contribution_graph, relative_contribution_table, top_trials_graph,
    mds_analysis, mds_graph, stress_interpretation, mds_summary_table,
    metrics
)


def setup_parser():
    """Set up command-line argument parser."""
    parser = argparse.ArgumentParser(
        description="MP-CLI: Microplastics analysis command-line tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic distribution analysis
  mp_cli.py dist --input data.xlsx --plot --output results/

  # Unmixing analysis
  mp_cli.py unmix --input data.xlsx --sources "Sample1,Sample2,Sample3" --sink "Mixed" --metric r2

  # MDS analysis
  mp_cli.py mds --input data.xlsx --metric similarity --exclude unknown

  # Multiple analyses
  mp_cli.py analyze --input data.xlsx --all --output results/
        """
    )
    
    # Global options
    parser.add_argument('--input', '-i', required=True,
                       help='Input Excel file with microplastics data')
    parser.add_argument('--output', '-o', default='mp_results',
                       help='Output directory (default: mp_results)')
    parser.add_argument('--exclude', nargs='+', default=['unknown'],
                       help='Plastic types to exclude (default: unknown)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Verbose output')
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Analysis commands')
    
    # Distribution analysis
    dist_parser = subparsers.add_parser('dist', help='Distribution analysis')
    dist_parser.add_argument('--plot', action='store_true',
                           help='Create distribution plots')
    dist_parser.add_argument('--cdf', action='store_true',
                           help='Include CDF analysis')
    dist_parser.add_argument('--stacked', action='store_true',
                           help='Use stacked plots')
    dist_parser.add_argument('--colormap', default='viridis',
                           help='Colormap for plots')
    
    # Unmixing analysis
    unmix_parser = subparsers.add_parser('unmix', help='Source unmixing analysis')
    unmix_parser.add_argument('--sources', required=True,
                            help='Comma-separated list of source sample names')
    unmix_parser.add_argument('--sink', required=True,
                            help='Sink sample name to unmix')
    unmix_parser.add_argument('--metric', choices=['r2', 'similarity', 'likeness', 'ks', 'kuiper', 'chi_squared'],
                            default='r2', help='Similarity metric')
    unmix_parser.add_argument('--trials', type=int, default=10000,
                            help='Number of Monte Carlo trials')
    unmix_parser.add_argument('--plot', action='store_true',
                            help='Create unmixing plots')
    
    # MDS analysis
    mds_parser = subparsers.add_parser('mds', help='Multidimensional scaling analysis')
    mds_parser.add_argument('--metric', choices=['similarity', 'likeness', 'r2', 'ks', 'kuiper'],
                          default='similarity', help='Distance metric')
    mds_parser.add_argument('--plot', action='store_true',
                          help='Create MDS plot')
    mds_parser.add_argument('--colormap', default='viridis',
                          help='Colormap for MDS plot')
    mds_parser.add_argument('--connections', action='store_true',
                          help='Show nearest neighbor connections')
    
    # Comprehensive analysis
    analyze_parser = subparsers.add_parser('analyze', help='Comprehensive analysis')
    analyze_parser.add_argument('--all', action='store_true',
                              help='Run all analyses')
    analyze_parser.add_argument('--distributions', action='store_true',
                              help='Include distribution analysis')
    analyze_parser.add_argument('--mds', action='store_true',
                              help='Include MDS analysis')
    analyze_parser.add_argument('--metrics', action='store_true',
                              help='Calculate all similarity metrics')
    
    # Data info
    info_parser = subparsers.add_parser('info', help='Display data information')
    info_parser.add_argument('--summary', action='store_true',
                           help='Show detailed summary')
    
    return parser


def load_data(input_file, exclude_types, verbose=False):
    """Load and process microplastics data."""
    if verbose:
        print(f"Loading data from {input_file}...")
    
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found.")
        sys.exit(1)
    
    try:
        samples = read_excel_samples(input_file)
        if verbose:
            print(f"Loaded {len(samples)} samples")
            print(f"Excluding plastic types: {exclude_types}")
        
        return samples
    except Exception as e:
        print(f"Error loading data: {e}")
        sys.exit(1)


def ensure_output_dir(output_dir):
    """Create output directory if it doesn't exist."""
    Path(output_dir).mkdir(parents=True, exist_ok=True)


def filter_sample_counts(sample, exclude_types):
    """Filter plastic counts excluding specified types."""
    filtered_counts = {}
    for plastic_type, count in sample.plastic_counts.items():
        if plastic_type not in exclude_types:
            filtered_counts[plastic_type] = count
    return filtered_counts


def cmd_info(args):
    """Display data information."""
    samples = load_data(args.input, args.exclude, args.verbose)
    
    print(f"\nDataset Information:")
    print(f"{'='*50}")
    print(f"Number of samples: {len(samples)}")
    print(f"Input file: {args.input}")
    
    # Get all plastic types
    all_plastics = set()
    for sample in samples:
        all_plastics.update(sample.plastic_counts.keys())
    
    print(f"Total plastic types: {len(all_plastics)}")
    print(f"Excluded types: {args.exclude}")
    print(f"Analyzed types: {len(all_plastics) - len(args.exclude)}")
    
    if args.summary:
        print(f"\nSample Details:")
        print(f"{'Sample Name':<20} {'Total Particles':<15} {'Types Found':<12}")
        print(f"{'-'*50}")
        for sample in samples:
            filtered_counts = filter_sample_counts(sample, args.exclude)
            total = sum(filtered_counts.values())
            types = len([x for x in filtered_counts.values() if x > 0])
            print(f"{sample.name:<20} {total:<15} {types:<12}")
        
        print(f"\nPlastic Types:")
        sorted_plastics = sorted(all_plastics)
        for plastic in sorted_plastics:
            status = "EXCLUDED" if plastic in args.exclude else "included"
            print(f"  {plastic:<35} [{status}]")


def cmd_dist(args):
    """Distribution analysis command."""
    samples = load_data(args.input, args.exclude, args.verbose)
    ensure_output_dir(args.output)
    
    if args.verbose:
        print("Running distribution analysis...")
    
    distributions = []
    plastic_types = None
    
    for sample in samples:
        filtered_counts = filter_sample_counts(sample, args.exclude)
        if filtered_counts:
            x_vals, y_vals = categorical_distribution(filtered_counts)
            dist = Distribution(sample.name, x_vals, y_vals)
            distributions.append(dist)
            if plastic_types is None:
                plastic_types = x_vals
    
    if args.plot:
        # PDF plot
        fig = distribution_graph(
            distributions,
            stacked=args.stacked,
            title="Microplastics Distribution Analysis",
            color_map=args.colormap,
            fig_width=12,
            fig_height=8
        )
        pdf_file = os.path.join(args.output, "distributions_pdf.png")
        fig.savefig(pdf_file, dpi=300, bbox_inches='tight')
        print(f"Saved PDF plot: {pdf_file}")
        
        # CDF plot if requested
        if args.cdf:
            cdf_distributions = []
            for dist in distributions:
                cdf_dist = cdf_function(dist)
                cdf_distributions.append(cdf_dist)
            
            fig = distribution_graph(
                cdf_distributions,
                stacked=args.stacked,
                title="Cumulative Distribution Analysis",
                color_map=args.colormap,
                y_label="Cumulative Probability",
                fig_width=12,
                fig_height=8
            )
            cdf_file = os.path.join(args.output, "distributions_cdf.png")
            fig.savefig(cdf_file, dpi=300, bbox_inches='tight')
            print(f"Saved CDF plot: {cdf_file}")
    
    # Save summary statistics
    summary_file = os.path.join(args.output, "distribution_summary.txt")
    with open(summary_file, 'w') as f:
        f.write("Microplastics Distribution Analysis Summary\n")
        f.write("="*50 + "\n\n")
        f.write(f"Number of samples: {len(distributions)}\n")
        f.write(f"Plastic types analyzed: {len(plastic_types)}\n")
        f.write(f"Excluded types: {args.exclude}\n\n")
        
        f.write("Sample Statistics:\n")
        f.write("-"*30 + "\n")
        for dist in distributions:
            total_prob = np.sum(dist.y_values)
            max_type_idx = np.argmax(dist.y_values)
            max_type = dist.x_values[max_type_idx]
            f.write(f"{dist.name:<20} | Dominant: {max_type} ({dist.y_values[max_type_idx]:.3f})\n")
    
    print(f"Saved summary: {summary_file}")


def cmd_unmix(args):
    """Unmixing analysis command."""
    samples = load_data(args.input, args.exclude, args.verbose)
    ensure_output_dir(args.output)
    
    if args.verbose:
        print("Running unmixing analysis...")
    
    # Find samples
    source_names = [name.strip() for name in args.sources.split(',')]
    sink_name = args.sink.strip()
    
    sample_dict = {sample.name: sample for sample in samples}
    
    # Validate sample names
    missing_sources = [name for name in source_names if name not in sample_dict]
    if missing_sources:
        print(f"Error: Source samples not found: {missing_sources}")
        return
    
    if sink_name not in sample_dict:
        print(f"Error: Sink sample not found: {sink_name}")
        return
    
    # Prepare distributions
    sink_sample = sample_dict[sink_name]
    source_samples = [sample_dict[name] for name in source_names]
    
    # Create distributions
    sink_counts = filter_sample_counts(sink_sample, args.exclude)
    source_dist_objects = []
    plastic_types = None
    
    for sample in source_samples:
        counts = filter_sample_counts(sample, args.exclude)
        if counts:
            if args.metric in ['ks', 'kuiper']:
                x_vals, y_vals = categorical_cdf(counts)
                dist_type = "CDF"
            else:
                x_vals, y_vals = categorical_distribution(counts)
                dist_type = "PDF"
            
            # Create Distribution object
            source_dist = Distribution(sample.name, x_vals, y_vals)
            source_dist_objects.append(source_dist)
            
            if plastic_types is None:
                plastic_types = x_vals
    
    # Sink distribution
    if args.metric in ['ks', 'kuiper']:
        x_vals, sink_y = categorical_cdf(sink_counts)
        dist_type = "CDF"
    else:
        x_vals, sink_y = categorical_distribution(sink_counts)
        dist_type = "PDF"
    
    sink_distribution = Distribution(sink_sample.name, x_vals, sink_y)
    
    if args.verbose:
        print(f"Using {dist_type} distributions for {args.metric} metric")
    
    # Run unmixing
    contributions, top_models = monte_carlo_unmixing(
        sink_distribution, source_dist_objects,
        n_trials=args.trials, metric=args.metric
    )
    
    # Save results
    results_file = os.path.join(args.output, f"unmixing_{args.metric}.csv")
    table = relative_contribution_table(contributions, metric=args.metric)
    table.to_csv(results_file)
    print(f"Saved unmixing results: {results_file}")
    
    # Create plots if requested
    if args.plot:
        # Contributions plot
        fig1 = relative_contribution_graph(
            contributions,
            title=f"Source Contributions ({args.metric} metric)"
        )
        contrib_file = os.path.join(args.output, f"contributions_{args.metric}.png")
        fig1.savefig(contrib_file, dpi=300, bbox_inches='tight')
        print(f"Saved contributions plot: {contrib_file}")
        
        # Model fit plot
        fig2 = top_trials_graph(
            sink_distribution.y_values, top_models, plastic_types,
            title=f"Best Fit Models vs Sink ({args.metric})"
        )
        model_file = os.path.join(args.output, f"models_{args.metric}.png")
        fig2.savefig(model_file, dpi=300, bbox_inches='tight')
        print(f"Saved model fit plot: {model_file}")
    
    # Print results summary
    print(f"\nUnmixing Results ({args.metric} metric):")
    print(f"{'='*40}")
    for contrib in contributions:
        print(f"{contrib.name:<20} {contrib.contribution:6.1f}% ± {contrib.standard_deviation:.1f}%")


def cmd_mds(args):
    """MDS analysis command."""
    samples = load_data(args.input, args.exclude, args.verbose)
    ensure_output_dir(args.output)
    
    if args.verbose:
        print("Running MDS analysis...")
    
    # Run MDS
    points, stress = mds_analysis(samples, metric=args.metric, exclude_plastics=args.exclude)
    
    # Print results
    print(f"\nMDS Analysis Results:")
    print(f"{'='*40}")
    print(f"Metric: {args.metric}")
    print(f"Stress: {stress:.4f} ({stress_interpretation(stress)})")
    
    # Save summary
    summary = mds_summary_table(points, stress)
    summary_file = os.path.join(args.output, f"mds_{args.metric}.txt")
    with open(summary_file, 'w') as f:
        f.write(summary)
    print(f"Saved MDS summary: {summary_file}")
    
    # Create plot if requested
    if args.plot:
        fig = mds_graph(
            points,
            title=f"MDS Analysis ({args.metric} metric, stress: {stress:.3f})",
            color_map=args.colormap,
            show_connections=args.connections,
            fig_width=10,
            fig_height=8
        )
        plot_file = os.path.join(args.output, f"mds_{args.metric}.png")
        fig.savefig(plot_file, dpi=300, bbox_inches='tight')
        print(f"Saved MDS plot: {plot_file}")


def cmd_analyze(args):
    """Comprehensive analysis command."""
    samples = load_data(args.input, args.exclude, args.verbose)
    ensure_output_dir(args.output)
    
    print("Running comprehensive analysis...")
    
    if args.all or args.distributions:
        print("\n1. Distribution Analysis")
        print("-" * 30)
        # Set up args for distribution analysis
        dist_args = argparse.Namespace(
            input=args.input, output=args.output, exclude=args.exclude,
            verbose=args.verbose, plot=True, cdf=True, stacked=False,
            colormap='viridis'
        )
        cmd_dist(dist_args)
    
    if args.all or args.mds:
        print("\n2. MDS Analysis")
        print("-" * 30)
        # Set up args for MDS analysis
        mds_args = argparse.Namespace(
            input=args.input, output=args.output, exclude=args.exclude,
            verbose=args.verbose, metric='similarity', plot=True,
            colormap='viridis', connections=True
        )
        cmd_mds(mds_args)
    
    if args.all or args.metrics:
        print("\n3. Metric Comparisons")
        print("-" * 30)
        # Calculate pairwise metrics between samples
        all_metrics = ['r2', 'similarity', 'likeness', 'ks', 'kuiper', 'chi_squared']
        
        # Prepare distributions
        pdf_dists = []
        cdf_dists = []
        sample_names = []
        
        for sample in samples:
            filtered_counts = filter_sample_counts(sample, args.exclude)
            if filtered_counts:
                _, y_pdf = categorical_distribution(filtered_counts)
                _, y_cdf = categorical_cdf(filtered_counts)
                pdf_dists.append(y_pdf)
                cdf_dists.append(y_cdf)
                sample_names.append(sample.name)
        
        # Calculate metric matrix
        n_samples = len(sample_names)
        metric_results = {}
        
        for metric_name in all_metrics:
            matrix = np.zeros((n_samples, n_samples))
            
            for i in range(n_samples):
                for j in range(i+1, n_samples):
                    if metric_name in ['ks', 'kuiper']:
                        dists = cdf_dists
                    else:
                        dists = pdf_dists
                    
                    if metric_name == 'r2':
                        val = metrics.r2(dists[i], dists[j])
                    elif metric_name == 'similarity':
                        val = metrics.similarity(dists[i], dists[j])
                    elif metric_name == 'likeness':
                        val = metrics.likeness(dists[i], dists[j])
                    elif metric_name == 'ks':
                        val = metrics.ks(dists[i], dists[j])
                    elif metric_name == 'kuiper':
                        val = metrics.kuiper(dists[i], dists[j])
                    elif metric_name == 'chi_squared':
                        val = metrics.chi_squared(dists[i], dists[j])
                    
                    matrix[i, j] = val
                    matrix[j, i] = val
            
            metric_results[metric_name] = matrix
        
        # Save metric matrices
        metrics_file = os.path.join(args.output, "metric_matrices.json")
        results_data = {
            'sample_names': sample_names,
            'metrics': {name: matrix.tolist() for name, matrix in metric_results.items()}
        }
        
        with open(metrics_file, 'w') as f:
            json.dump(results_data, f, indent=2)
        
        print(f"Saved metric matrices: {metrics_file}")
    
    print(f"\nComprehensive analysis complete!")
    print(f"Results saved to: {args.output}/")


def main():
    """Main CLI entry point."""
    parser = setup_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Route to appropriate command
    if args.command == 'info':
        cmd_info(args)
    elif args.command == 'dist':
        cmd_dist(args)
    elif args.command == 'unmix':
        cmd_unmix(args)
    elif args.command == 'mds':
        cmd_mds(args)
    elif args.command == 'analyze':
        cmd_analyze(args)
    else:
        print(f"Unknown command: {args.command}")
        parser.print_help()


if __name__ == "__main__":
    main()