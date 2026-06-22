"""
Sector Rotation Analysis API

Generates sector rotation analysis and returns results for web app display.
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime
import shutil
import pandas as pd

# Import sector analysis modules
sector_analysis_dir = Path(__file__).parent.parent.parent / 'sector_analysis'
sys.path.insert(0, str(sector_analysis_dir / 'scripts'))

from fetch_sector_data import fetch_sector_etfs
from calculate_sector_metrics import (
    calculate_relative_strength,
    calculate_momentum,
    rank_sectors,
    identify_rotation_quadrants
)


def generate_sector_analysis():
    """
    Generate sector rotation analysis

    Returns:
        dict with sector rankings, rotation map, and portfolio recommendations
    """
    try:
        # Fetch sector data
        df = fetch_sector_etfs(lookback_days=365)

        # Calculate metrics
        df = calculate_relative_strength(df)
        df = calculate_momentum(df)

        # Rank sectors
        rankings = rank_sectors(df)

        # Identify rotation quadrants
        quadrants = identify_rotation_quadrants(df)

        # Generate full report
        from generate_sector_report import generate_markdown_report, save_report

        md_report = generate_markdown_report(rankings, quadrants, df)
        md_path = save_report(md_report)

        # Convert to HTML
        html_path = md_path.replace('.md', '.html')
        try:
            sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'utils'))
            from md_to_html import convert_md_to_html
            convert_md_to_html(md_path, html_path)
        except Exception as e:
            print(f"[WARNING] HTML conversion failed: {str(e)}")

        # Copy reports to web app reports directory
        reports_dir = Path(__file__).parent.parent / 'reports'
        reports_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        dest_md = reports_dir / f'Sector_Rotation_{timestamp}.md'
        dest_html = reports_dir / f'Sector_Rotation_{timestamp}.html'

        shutil.copy2(md_path, dest_md)
        if Path(html_path).exists():
            shutil.copy2(html_path, dest_html)

        # Format data for API response
        rankings_list = []
        for _, row in rankings.iterrows():
            rankings_list.append({
                'rank': int(row['rank']),
                'name': row['sector_name'],
                'ticker': row['ticker'],
                'score': float(row['composite_score']),
                'rs_20d': float(row['rs_20d'] * 100),  # Convert to percentage
                'rs_60d': float(row['rs_60d'] * 100),
                'momentum': float(row['momentum_score'] * 100),
                'signal': row['signal'],
                'price': float(row['adjusted_close'])
            })

        # Calculate portfolio allocation
        top_5 = rankings.head(5)
        total_score = top_5['composite_score'].sum()

        portfolio = {
            'top_5': [],
            'bottom_3': []
        }

        for _, row in top_5.iterrows():
            allocation = (row['composite_score'] / total_score) * 100
            portfolio['top_5'].append({
                'name': row['sector_name'],
                'ticker': row['ticker'],
                'allocation': round(allocation, 1)
            })

        bottom_3 = rankings.tail(3)
        for _, row in bottom_3.iterrows():
            portfolio['bottom_3'].append({
                'name': row['sector_name'],
                'ticker': row['ticker']
            })

        return {
            'success': True,
            'rankings': rankings_list,
            'rotation_map': quadrants,
            'portfolio': portfolio,
            'report_path': f'/api/report/{dest_html.name}',
            'report_md_path': f'/api/report/{dest_md.name}',
            'timestamp': datetime.now().isoformat()
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise Exception(f"Sector analysis failed: {str(e)}")
