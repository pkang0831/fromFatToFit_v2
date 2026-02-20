import logging
from typing import Dict, Any
import math

logger = logging.getLogger(__name__)


def calculate_percentile(body_fat: float, age: int, gender: str, ethnicity: str) -> Dict[str, Any]:
    """
    Calculate body fat percentile based on demographic data
    
    This uses simplified reference data. In production, you'd use actual
    CDC/WHO reference tables or research data.
    
    Args:
        body_fat: Body fat percentage
        age: User's age
        gender: User's gender (male/female)
        ethnicity: User's ethnicity
        
    Returns:
        Dictionary with percentile data and distribution info
    """
    try:
        # Simplified reference data (mean and std dev for body fat %)
        # In production, use actual demographic tables
        reference_data = {
            "male": {
                "18-29": {"mean": 18, "std": 6},
                "30-39": {"mean": 20, "std": 6},
                "40-49": {"mean": 22, "std": 6},
                "50+": {"mean": 24, "std": 6}
            },
            "female": {
                "18-29": {"mean": 25, "std": 7},
                "30-39": {"mean": 27, "std": 7},
                "40-49": {"mean": 29, "std": 7},
                "50+": {"mean": 31, "std": 7}
            }
        }
        
        # Determine age group
        if age < 30:
            age_group = "18-29"
        elif age < 40:
            age_group = "30-39"
        elif age < 50:
            age_group = "40-49"
        else:
            age_group = "50+"
        
        # Get reference stats
        gender_key = gender.lower()
        if gender_key not in reference_data:
            gender_key = "male"  # Default
            
        ref = reference_data[gender_key][age_group]
        mean = ref["mean"]
        std = ref["std"]
        
        # Calculate z-score
        z_score = (body_fat - mean) / std
        
        # Calculate percentile (using cumulative distribution function)
        # Approximation of normal CDF
        # This gives us what % of people have body fat below you
        percentile_below = 50 * (1 + math.erf(z_score / math.sqrt(2)))
        percentile_below = max(1, min(99, percentile_below))  # Clamp between 1-99
        
        # For body fat, lower is better
        # Calculate what % of people you're better than (have higher BF than you)
        better_than_percent = 100 - percentile_below
        
        # Generate rank text (clearer expression)
        if better_than_percent >= 90:
            rank_text = f"Top {100 - better_than_percent:.0f}% (Elite)"
        elif better_than_percent >= 75:
            rank_text = f"Top {100 - better_than_percent:.0f}% (Excellent)"
        elif better_than_percent >= 50:
            rank_text = f"Top {100 - better_than_percent:.0f}% (Above Average)"
        elif better_than_percent >= 25:
            rank_text = f"Top {100 - better_than_percent:.0f}% (Average)"
        else:
            rank_text = f"Bottom {better_than_percent:.0f}% (Needs Improvement)"
        
        # Generate distribution data for bell curve visualization
        distribution_data = {
            "mean": mean,
            "std": std,
            "user_value": body_fat,
            "better_than_percent": better_than_percent,
            "comparison_group": f"{gender}, {age_group} years",
            "ranges": [
                {"label": "Excellent", "min": 0, "max": mean - 2*std},
                {"label": "Good", "min": mean - 2*std, "max": mean - std},
                {"label": "Average", "min": mean - std, "max": mean + std},
                {"label": "Below Average", "min": mean + std, "max": mean + 2*std},
                {"label": "Poor", "min": mean + 2*std, "max": 50}
            ]
        }
        
        return {
            "percentile": better_than_percent,
            "rank_text": rank_text,
            "comparison_group": f"{gender}, {age_group} years, {ethnicity}",
            "distribution_data": distribution_data
        }
        
    except Exception as e:
        logger.error(f"Error calculating percentile: {e}")
        raise


def estimate_transformation_timeline(current_bf: float, target_bf: float, is_aggressive: bool = False) -> int:
    """
    Estimate weeks needed for body fat reduction
    
    Args:
        current_bf: Current body fat %
        target_bf: Target body fat %
        is_aggressive: Whether using aggressive approach
        
    Returns:
        Estimated weeks
    """
    bf_reduction = current_bf - target_bf
    
    # Healthy fat loss: 0.5-1% body fat per month
    # Aggressive: 1-1.5% per month
    if is_aggressive:
        rate_per_month = 1.25
    else:
        rate_per_month = 0.75
    
    months = bf_reduction / rate_per_month
    weeks = int(months * 4.33)  # Average weeks per month
    
    return max(4, weeks)  # Minimum 4 weeks


def generate_recommendations(body_fat: float, gender: str) -> list:
    """
    Generate personalized recommendations based on body fat percentage
    
    Args:
        body_fat: Current body fat %
        gender: User's gender
        
    Returns:
        List of recommendations
    """
    recommendations = []
    
    # Gender-specific ranges
    if gender.lower() == "male":
        if body_fat < 10:
            recommendations = [
                "You're at a very lean level - ensure adequate nutrition for health",
                "Consider reverse dieting if you've been in a deficit long-term",
                "Focus on maintaining muscle mass"
            ]
        elif body_fat < 15:
            recommendations = [
                "You're in an athletic range - great work!",
                "Focus on performance and maintaining current habits",
                "Consider a slight calorie surplus if building muscle"
            ]
        elif body_fat < 20:
            recommendations = [
                "You're in a healthy range",
                "Small calorie deficit (300-500 kcal) for fat loss",
                "Prioritize protein (0.8-1g per lb bodyweight)"
            ]
        else:
            recommendations = [
                "Focus on sustainable calorie deficit (500-750 kcal)",
                "Aim for 0.5-1% bodyweight loss per week",
                "Increase protein intake and start resistance training"
            ]
    else:  # female
        if body_fat < 18:
            recommendations = [
                "You're at an athletic level - monitor health markers",
                "Ensure menstrual cycle regularity",
                "Focus on nutrient-dense foods"
            ]
        elif body_fat < 25:
            recommendations = [
                "You're in an athletic to healthy range",
                "Maintenance or small deficit depending on goals",
                "Balance cardio and strength training"
            ]
        elif body_fat < 32:
            recommendations = [
                "You're in a healthy range",
                "Moderate calorie deficit if fat loss is desired",
                "Focus on building healthy habits"
            ]
        else:
            recommendations = [
                "Start with moderate calorie deficit (300-500 kcal)",
                "Focus on whole foods and regular movement",
                "Consider working with a coach or nutritionist"
            ]
    
    return recommendations
