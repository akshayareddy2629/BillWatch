#!/usr/bin/env python3
"""
AWS Cost Widget - Desktop application for monitoring AWS spending.

A minimal, cross-platform widget that displays:
- Month-to-date AWS costs
- Budget progress with color-coded thresholds
- Top 5 spending services

Run with: python main.py
"""

import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import load_config
from cost_fetcher import fetch_simulated_costs, fetch_aws_costs
from widget import AWSCostWidget
from scheduler import UpdateScheduler


def show_error_dialog(title: str, message: str) -> None:
    """Show an error dialog using tkinter."""
    import tkinter as tk
    from tkinter import messagebox      
    
    root = tk.Tk()
    root.withdraw()  # Hide main window
    messagebox.showerror(title, message)
    root.destroy()


def main() -> None:
    """Initialize and run the AWS Cost Widget application."""
    # Load configuration
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')
    if not os.path.exists(config_path):
        config_path = 'config.json'
    
    config = load_config(config_path)
    
    # Select data fetcher based on configuration
    if config.use_simulated_data:
        fetcher = fetch_simulated_costs
        print("Using simulated cost data")
    else:
        # Test AWS credentials before starting
        try:
            fetch_aws_costs()
            fetcher = fetch_aws_costs
            print("Connected to AWS Cost Explorer")
        except Exception as e:
            error_msg = str(e)
            print(f"AWS Error: {error_msg}")
            
            # Show error and offer to use simulated data
            show_error_dialog(
                "AWS Credentials Error",
                f"{error_msg}\n\n"
                "The widget will use simulated data instead.\n"
                "To use real AWS data, configure your credentials and restart."
            )
            fetcher = fetch_simulated_costs
    
    # Create and configure widget
    try:
        widget = AWSCostWidget(config)
    except Exception as e:
        show_error_dialog("Widget Error", f"Failed to create widget: {e}")
        sys.exit(1)
    
    # Create scheduler and start updates
    scheduler = UpdateScheduler(widget, fetcher, config.refresh_interval)
    scheduler.start()
    
    print(f"AWS Cost Widget started (refresh every {config.refresh_interval}s)")
    print("Drag to move, click X to close")
    
    # Run the widget
    try:
        widget.run()
    except KeyboardInterrupt:
        print("\nShutting down...")



if __name__ == "__main__":
    main()
