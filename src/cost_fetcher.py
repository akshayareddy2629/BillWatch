"""Cost data fetching for AWS Cost Widget."""

import random
from dataclasses import dataclass
from datetime import datetime
from typing import List, Tuple, Optional

# AWS service names for simulation
AWS_SERVICES = [
    "Amazon EC2", "Amazon S3", "Amazon RDS", "AWS Lambda",
    "Amazon CloudFront", "Amazon DynamoDB", "Amazon ECS",
    "Amazon SQS", "Amazon SNS", "AWS Fargate", "Amazon EKS",
    "Amazon ElastiCache", "Amazon Redshift", "AWS Glue"
]


@dataclass
class CostData:
    """Container for AWS cost information."""
    month_to_date: float
    top_services: List[Tuple[str, float]]
    last_updated: datetime


def format_currency(amount: float) -> str:
    """
    Format amount as currency string with $ symbol and 2 decimal places.
    
    Args:
        amount: The amount to format
        
    Returns:
        Formatted string like "$123.45"
    """
    return f"${amount:.2f}"


def get_top_services(services: List[Tuple[str, float]], limit: int = 5) -> List[Tuple[str, float]]:
    """
    Get top N services sorted by cost in descending order.
    
    Args:
        services: List of (service_name, cost) tuples
        limit: Maximum number of services to return
        
    Returns:
        Up to `limit` services sorted by cost descending
    """
    sorted_services = sorted(services, key=lambda x: x[1], reverse=True)
    return sorted_services[:limit]


def fetch_simulated_costs() -> CostData:
    """
    Generate simulated cost data for testing/demo purposes.
    
    Returns:
        CostData with random but realistic values
    """
    # Generate random MTD cost between $10 and $500
    mtd = random.uniform(10.0, 500.0)
    
    # Generate random costs for 5-10 services
    num_services = random.randint(5, 10)
    selected_services = random.sample(AWS_SERVICES, num_services)
    
    # Distribute costs (some services cost more than others)
    service_costs = []
    remaining = mtd
    for i, service in enumerate(selected_services):
        if i == len(selected_services) - 1:
            cost = remaining
        else:
            # Random portion of remaining cost
            cost = random.uniform(0, remaining * 0.6)
            remaining -= cost
        service_costs.append((service, round(cost, 2)))
    
    top_services = get_top_services(service_costs)
    
    return CostData(
        month_to_date=round(mtd, 2),
        top_services=top_services,
        last_updated=datetime.now()
    )


def fetch_aws_costs() -> CostData:
    """
    Fetch real cost data from AWS Cost Explorer API.
    
    Returns:
        CostData with actual AWS spending information
        
    Raises:
        Exception: If AWS credentials are missing or invalid
    """
    try:
        import boto3
        from datetime import date
        
        # Create Cost Explorer client
        client = boto3.client('ce')
        
        # Get current month date range
        today = date.today()
        start_date = today.replace(day=1).isoformat()
        end_date = today.isoformat()
        
        # Fetch month-to-date costs
        response = client.get_cost_and_usage(
            TimePeriod={
                'Start': start_date,
                'End': end_date
            },
            Granularity='MONTHLY',
            Metrics=['UnblendedCost'],
            GroupBy=[
                {'Type': 'DIMENSION', 'Key': 'SERVICE'}
            ]
        )
        
        # Parse response
        service_costs = []
        total_cost = 0.0
        
        for result in response.get('ResultsByTime', []):
            for group in result.get('Groups', []):
                service_name = group['Keys'][0]
                cost = float(group['Metrics']['UnblendedCost']['Amount'])
                if cost > 0:
                    service_costs.append((service_name, round(cost, 2)))
                    total_cost += cost
        
        top_services = get_top_services(service_costs)
        
        return CostData(
            month_to_date=round(total_cost, 2),
            top_services=top_services,
            last_updated=datetime.now()
        )
        
    except ImportError:
        raise Exception("boto3 is required for AWS integration. Install with: pip install boto3")
    except Exception as e:
        error_msg = str(e)
        if "credentials" in error_msg.lower() or "NoCredentialsError" in error_msg:
            raise Exception(
                "AWS credentials not found. Please configure credentials:\n"
                "1. Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables, or\n"
                "2. Configure ~/.aws/credentials file, or\n"
                "3. Use AWS IAM role if running on EC2"
            )
        raise
