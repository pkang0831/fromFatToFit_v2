"""
Weight Tracking and Goal Projection Service
Handles weight/body fat logging, moving averages, and goal projections
"""
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import date, timedelta
from decimal import Decimal
from ..database import get_supabase
from ..schemas.weight_schemas import (
    WeightLogCreate,
    WeightLogUpdate,
    WeightLogResponse,
    GoalUpdate,
    GoalProjectionResponse,
    MovingAveragePoint,
    ProjectionPoint
)

logger = logging.getLogger(__name__)


class WeightTrackingService:
    """Service for weight tracking and goal projections"""
    
    # Scientific constants
    BASE_CALORIES_PER_KG = 7700  # Traditional rule: 1 kg ≈ 7700 kcal
    ADAPTATION_RATE = 0.10  # 10% metabolic adaptation after extended deficit
    ADAPTATION_THRESHOLD_DAYS = 28  # 4 weeks
    PREDICTION_VARIANCE = 0.15  # ±15% prediction variance for best/worst case
    
    @staticmethod
    async def create_weight_log(user_id: str, log_data: WeightLogCreate) -> WeightLogResponse:
        """Create or update a weight log entry"""
        try:
            supabase = get_supabase()
            
            log_dict = {
                "user_id": user_id,
                "date": log_data.date.isoformat(),
                "weight_kg": float(log_data.weight_kg),
                "body_fat_percentage": float(log_data.body_fat_percentage) if log_data.body_fat_percentage else None,
                "notes": log_data.notes
            }
            
            # Check if log already exists for this date
            existing = supabase.table("weight_logs")\
                .select("id")\
                .eq("user_id", user_id)\
                .eq("date", log_data.date.isoformat())\
                .execute()
            
            if existing.data:
                # Update existing log
                result = supabase.table("weight_logs")\
                    .update({
                        "weight_kg": float(log_data.weight_kg),
                        "body_fat_percentage": float(log_data.body_fat_percentage) if log_data.body_fat_percentage else None,
                        "notes": log_data.notes
                    })\
                    .eq("id", existing.data[0]["id"])\
                    .execute()
            else:
                # Insert new log
                result = supabase.table("weight_logs").insert(log_dict).execute()
            
            if not result.data:
                raise ValueError("Failed to create weight log")
            
            return WeightLogResponse(**result.data[0])
            
        except Exception as e:
            logger.error(f"Error creating weight log: {e}")
            raise
    
    @staticmethod
    async def get_weight_logs(user_id: str, days: int = 30) -> List[WeightLogResponse]:
        """Get weight logs for specified number of days"""
        try:
            supabase = get_supabase()
            
            start_date = (date.today() - timedelta(days=days)).isoformat()
            
            result = supabase.table("weight_logs")\
                .select("*")\
                .eq("user_id", user_id)\
                .gte("date", start_date)\
                .order("date", desc=True)\
                .execute()
            
            return [WeightLogResponse(**log) for log in result.data]
            
        except Exception as e:
            logger.error(f"Error fetching weight logs: {e}")
            raise
    
    @staticmethod
    async def update_weight_log(user_id: str, log_id: str, update_data: WeightLogUpdate) -> WeightLogResponse:
        """Update an existing weight log"""
        try:
            supabase = get_supabase()
            
            update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
            
            if "weight_kg" in update_dict:
                update_dict["weight_kg"] = float(update_dict["weight_kg"])
            if "body_fat_percentage" in update_dict:
                update_dict["body_fat_percentage"] = float(update_dict["body_fat_percentage"])
            
            result = supabase.table("weight_logs")\
                .update(update_dict)\
                .eq("id", log_id)\
                .eq("user_id", user_id)\
                .execute()
            
            if not result.data:
                raise ValueError("Weight log not found")
            
            return WeightLogResponse(**result.data[0])
            
        except Exception as e:
            logger.error(f"Error updating weight log: {e}")
            raise
    
    @staticmethod
    async def delete_weight_log(user_id: str, log_id: str) -> bool:
        """Delete a weight log"""
        try:
            supabase = get_supabase()
            
            result = supabase.table("weight_logs")\
                .delete()\
                .eq("id", log_id)\
                .eq("user_id", user_id)\
                .execute()
            
            return True
            
        except Exception as e:
            logger.error(f"Error deleting weight log: {e}")
            raise
    
    @staticmethod
    async def update_goals(user_id: str, goals: GoalUpdate) -> Dict[str, Any]:
        """Update user's weight and body fat goals"""
        try:
            supabase = get_supabase()
            
            update_dict = {}
            if goals.target_weight_kg is not None:
                update_dict["target_weight_kg"] = float(goals.target_weight_kg)
            if goals.target_body_fat_percentage is not None:
                update_dict["target_body_fat_percentage"] = float(goals.target_body_fat_percentage)
            
            result = supabase.table("user_profiles")\
                .update(update_dict)\
                .eq("user_id", user_id)\
                .execute()
            
            if not result.data:
                raise ValueError("User profile not found")
            
            return result.data[0]
            
        except Exception as e:
            logger.error(f"Error updating goals: {e}")
            raise
    
    @staticmethod
    def calculate_moving_average(data: List[Tuple[date, float]], window: int = 3) -> Dict[date, float]:
        """Calculate moving average for a dataset"""
        if len(data) < window:
            return {}
        
        # Sort by date
        sorted_data = sorted(data, key=lambda x: x[0])
        
        moving_averages = {}
        for i in range(window - 1, len(sorted_data)):
            window_data = sorted_data[i - window + 1:i + 1]
            avg = sum(val for _, val in window_data) / window
            moving_averages[sorted_data[i][0]] = round(avg, 2)
        
        return moving_averages
    
    @staticmethod
    def calculate_energy_density(body_fat_percentage: Optional[float]) -> float:
        """
        Calculate energy density based on body fat percentage (Forbes equation)
        
        Research shows that energy required per kg weight loss varies with body composition:
        - Higher body fat = more energy per kg (closer to pure fat: 9 kcal/g)
        - Lower body fat = less energy per kg (more lean tissue loss: ~1.8 kcal/g)
        
        Formula: Energy Density = 1020 / (1 - (body_fat_% / 100))
        
        Args:
            body_fat_percentage: Current body fat percentage (0-100)
            
        Returns:
            Energy density in kcal/kg
        """
        if body_fat_percentage and 5 <= body_fat_percentage <= 50:
            # Forbes equation for energy density based on body composition
            energy_density = 1020 / (1 - (body_fat_percentage / 100))
            # Clamp to reasonable range
            return max(6000, min(10000, energy_density))
        
        # Default to traditional 7700 kcal/kg if no body fat data
        return WeightTrackingService.BASE_CALORIES_PER_KG
    
    @staticmethod
    def calculate_metabolic_adaptation(days_in_deficit: int) -> float:
        """
        Calculate metabolic adaptation factor based on deficit duration
        
        Research (Hall et al., The Lancet 2011) shows:
        - Metabolism slows down during extended calorie restriction
        - Adaptation begins around 4 weeks
        - Can reach 10-15% reduction after 8-12 weeks
        - This is why weight loss plateaus over time
        
        Args:
            days_in_deficit: Number of days user has been in calorie deficit
            
        Returns:
            Adaptation factor (1.0 = no adaptation, 0.9 = 10% reduction)
        """
        if days_in_deficit < WeightTrackingService.ADAPTATION_THRESHOLD_DAYS:
            # No adaptation in first 4 weeks
            return 1.0
        
        # Progressive adaptation over 8 weeks (28-84 days)
        days_over_threshold = days_in_deficit - WeightTrackingService.ADAPTATION_THRESHOLD_DAYS
        adaptation_progress = min(days_over_threshold / 56, 1.0)  # 56 days = 8 weeks
        
        # Linear adaptation up to 10%
        adaptation_amount = adaptation_progress * WeightTrackingService.ADAPTATION_RATE
        
        return 1.0 - adaptation_amount
    
    @staticmethod
    async def get_goal_projection(user_id: str, days_history: int = 30) -> GoalProjectionResponse:
        """
        Calculate goal projection based on current trends
        
        Uses:
        - 3-day moving average to smooth out daily fluctuations
        - Recent calorie deficit to estimate rate of weight loss
        - Scientific formula: 1 kg body weight ≈ 7700 kcal
        """
        try:
            supabase = get_supabase()
            
            # Get user profile with goals
            profile_result = supabase.table("user_profiles")\
                .select("weight_kg, target_weight_kg, target_body_fat_percentage")\
                .eq("user_id", user_id)\
                .execute()
            
            if not profile_result.data:
                raise ValueError("User profile not found")
            
            profile = profile_result.data[0]
            current_weight = float(profile.get("weight_kg", 70.0))
            target_weight = profile.get("target_weight_kg")
            target_body_fat = profile.get("target_body_fat_percentage")
            
            # Get weight logs (include today)
            start_date = (date.today() - timedelta(days=days_history)).isoformat()
            end_date = date.today().isoformat()
            
            logs_result = supabase.table("weight_logs")\
                .select("*")\
                .eq("user_id", user_id)\
                .gte("date", start_date)\
                .lte("date", end_date)\
                .order("date", desc=False)\
                .execute()
            
            logs = logs_result.data
            
            logger.info(f"Fetched {len(logs)} weight logs from {start_date} to {end_date}")
            
            # Prepare historical data
            weight_data = [(date.fromisoformat(log["date"]), float(log["weight_kg"])) for log in logs]
            body_fat_data = [
                (date.fromisoformat(log["date"]), float(log["body_fat_percentage"]))
                for log in logs if log.get("body_fat_percentage")
            ]
            
            # Calculate moving averages
            weight_ma = WeightTrackingService.calculate_moving_average(weight_data, window=3)
            body_fat_ma = WeightTrackingService.calculate_moving_average(body_fat_data, window=3) if body_fat_data else {}
            
            # Get most recent values
            if not weight_data:
                # No weight logs, use profile weight
                most_recent_weight = current_weight
                most_recent_body_fat = None
                moving_avg_weight = current_weight
                moving_avg_body_fat = None
            else:
                most_recent_weight = weight_data[-1][1]
                most_recent_body_fat = body_fat_data[-1][1] if body_fat_data else None
                moving_avg_weight = list(weight_ma.values())[-1] if weight_ma else most_recent_weight
                moving_avg_body_fat = list(body_fat_ma.values())[-1] if body_fat_ma else None
            
            # Calculate daily rate of change from recent trend (last 7 days)
            recent_weight_data = [w for w in weight_data if w[0] >= date.today() - timedelta(days=7)]
            
            if len(recent_weight_data) >= 3:  # Need at least 3 points for reliable trend
                # Linear regression or simple slope
                first_weight = recent_weight_data[0][1]
                last_weight = recent_weight_data[-1][1]
                days_diff = (recent_weight_data[-1][0] - recent_weight_data[0][0]).days
                
                if days_diff > 0:
                    daily_weight_change = (last_weight - first_weight) / days_diff
                    
                    # Sanity check: Max realistic change is ~1.5kg/week = ~0.21kg/day
                    # If losing weight: daily_weight_change should be negative
                    # If gaining weight: daily_weight_change should be positive
                    MAX_DAILY_CHANGE = 0.3  # kg/day (very aggressive but possible)
                    
                    if abs(daily_weight_change) > MAX_DAILY_CHANGE:
                        logger.warning(
                            f"Unrealistic weight change detected: {daily_weight_change:.2f} kg/day. "
                            f"Ignoring trend data and using calorie-based prediction instead."
                        )
                        daily_weight_change = 0.0  # Ignore unrealistic trend
                else:
                    daily_weight_change = 0.0
            else:
                # Not enough data points for reliable trend
                daily_weight_change = 0.0
                logger.info(f"Insufficient weight data ({len(recent_weight_data)} points). Need at least 3 for trend analysis.")
            
            # Calculate body fat rate of change
            recent_bf_data = [bf for bf in body_fat_data if bf[0] >= date.today() - timedelta(days=7)]
            daily_body_fat_change = None
            
            if len(recent_bf_data) >= 2:
                first_bf = recent_bf_data[0][1]
                last_bf = recent_bf_data[-1][1]
                days_diff = (recent_bf_data[-1][0] - recent_bf_data[0][0]).days
                
                if days_diff > 0:
                    daily_body_fat_change = (last_bf - first_bf) / days_diff
            
            # Get average daily deficit from analytics (last 7 days)
            from .analytics import get_calorie_balance_trend
            calorie_trend = await get_calorie_balance_trend(user_id, days=7)
            avg_daily_deficit = calorie_trend["summary"]["avg_deficit"]
            
            # Calculate days in deficit (estimate from first log)
            if weight_data:
                days_in_deficit = (date.today() - weight_data[0][0]).days
            else:
                days_in_deficit = 0
            
            # Calculate improved energy density based on body fat
            energy_density = WeightTrackingService.calculate_energy_density(moving_avg_body_fat)
            
            # Calculate metabolic adaptation
            adaptation_factor = WeightTrackingService.calculate_metabolic_adaptation(days_in_deficit)
            
            logger.info(
                f"Projection parameters: energy_density={energy_density:.0f} kcal/kg, "
                f"adaptation_factor={adaptation_factor:.2f}, days_in_deficit={days_in_deficit}"
            )
            
            # Build historical trend data
            historical_data = []
            for log in logs:
                log_date = date.fromisoformat(log["date"])
                historical_data.append(MovingAveragePoint(
                    date=log_date,
                    weight_kg=float(log["weight_kg"]),
                    body_fat_percentage=float(log["body_fat_percentage"]) if log.get("body_fat_percentage") else None,
                    moving_avg_weight=weight_ma.get(log_date, float(log["weight_kg"])),
                    moving_avg_body_fat=body_fat_ma.get(log_date) if log.get("body_fat_percentage") else None
                ))
            
            logger.info(f"Built {len(historical_data)} historical data points")
            for point in historical_data:
                logger.info(f"  - {point.date}: {point.weight_kg} kg (MA: {point.moving_avg_weight})")
            
            # Calculate projection
            projection_data = []
            estimated_days_to_goal = None
            estimated_goal_date = None
            on_track = True
            message = "Keep up the good work!"
            
            if target_weight is not None:
                target_weight = float(target_weight)
                weight_difference = target_weight - moving_avg_weight
                
                # Method 1: Use actual weight change rate if available (and realistic)
                if abs(daily_weight_change) > 0.001:
                    # User has a measurable and realistic trend
                    weekly_change = abs(daily_weight_change) * 7
                    
                    if weight_difference > 0 and daily_weight_change > 0:
                        # Need to gain weight and currently gaining
                        estimated_days_to_goal = int(weight_difference / daily_weight_change)
                        message = f"📈 Gaining at {weekly_change:.1f}kg/week. On track to goal!"
                    elif weight_difference < 0 and daily_weight_change < 0:
                        # Need to lose weight and currently losing
                        estimated_days_to_goal = int(abs(weight_difference / daily_weight_change))
                        
                        # Provide context about the rate
                        if weekly_change > 1.0:
                            message = f"⚠️ Losing {weekly_change:.1f}kg/week - very fast! Healthy rate: 0.5-1kg/week."
                            on_track = True  # Still on track, just warning
                        elif weekly_change < 0.25:
                            message = f"🐌 Losing {weekly_change:.1f}kg/week - slow but steady wins the race!"
                        else:
                            message = f"✅ Losing {weekly_change:.1f}kg/week - perfect pace!"
                    else:
                        # Moving in wrong direction
                        on_track = False
                        if weight_difference < 0:
                            message = "⚠️ Weight is increasing but goal is to lose. Check your calorie intake!"
                        else:
                            message = "⚠️ Weight is decreasing but goal is to gain. Increase your calorie intake!"
                
                # Method 2: Improved deficit-based estimation
                elif abs(avg_daily_deficit) > 50:
                    # Apply metabolic adaptation to deficit
                    adjusted_deficit = avg_daily_deficit * adaptation_factor
                    
                    # Use improved energy density (considers body fat %)
                    kg_per_day = adjusted_deficit / energy_density
                    
                    logger.info(
                        f"Deficit-based prediction: raw_deficit={avg_daily_deficit:.1f}, "
                        f"adjusted_deficit={adjusted_deficit:.1f}, kg_per_day={kg_per_day:.4f}"
                    )
                    
                    if abs(kg_per_day) > 0.001:
                        if weight_difference < 0 and kg_per_day > 0:
                            # Need to lose, deficit supports it
                            estimated_days_to_goal = int(abs(weight_difference / kg_per_day))
                            
                            # Provide realistic message based on rate
                            weekly_loss = abs(kg_per_day) * 7
                            if weekly_loss > 1.0:
                                message = f"⚠️ Rapid weight loss ({weekly_loss:.1f}kg/week). Consider slowing down for health."
                            elif weekly_loss < 0.25:
                                message = f"Slow but steady progress ({weekly_loss:.1f}kg/week). Stay consistent!"
                            else:
                                message = f"Healthy pace ({weekly_loss:.1f}kg/week). Keep it up!"
                                
                        elif weight_difference > 0 and kg_per_day < 0:
                            # Need to gain, surplus supports it
                            estimated_days_to_goal = int(abs(weight_difference / kg_per_day))
                            weekly_gain = abs(kg_per_day) * 7
                            message = f"Gaining at {weekly_gain:.1f}kg/week. On track to goal!"
                        else:
                            on_track = False
                            if weight_difference < 0:
                                message = "You're in calorie surplus but need to lose weight. Increase deficit."
                            else:
                                message = "You're in calorie deficit but need to gain weight. Increase surplus."
                
                else:
                    # No significant deficit
                    if len(weight_data) < 3:
                        message = "⚠️ Not enough weight logs. Record weight for at least 3 days!"
                    elif abs(avg_daily_deficit) < 50:
                        message = "⚠️ No calorie deficit detected. Log your food intake and workouts!"
                    else:
                        message = "Not enough data to project. Keep logging weight and food!"
                
                # Generate projection data with best/worst case scenarios
                if estimated_days_to_goal and estimated_days_to_goal > 0:
                    estimated_goal_date = date.today() + timedelta(days=estimated_days_to_goal)
                    
                    # Cap projection at 180 days for display
                    projection_days = min(estimated_days_to_goal, 180)
                    
                    # Calculate daily rate for projection
                    if daily_weight_change != 0:
                        # Using actual measured weight change (already has correct sign)
                        base_kg_per_day = daily_weight_change
                    else:
                        # Using calorie-based prediction
                        # Deficit > 0 means losing weight (negative change)
                        # Deficit < 0 (surplus) means gaining weight (positive change)
                        adjusted_deficit = avg_daily_deficit * adaptation_factor
                        base_kg_per_day = -(adjusted_deficit / energy_density)  # Negative for weight loss
                    
                    for i in range(1, projection_days + 1, 7):  # Weekly points
                        projection_date = date.today() + timedelta(days=i)
                        
                        # Calculate progressive adaptation for future days
                        future_days_in_deficit = days_in_deficit + i
                        future_adaptation = WeightTrackingService.calculate_metabolic_adaptation(
                            future_days_in_deficit
                        )
                        
                        # Adjust rate based on future adaptation
                        if daily_weight_change == 0:
                            # For calorie-based, apply progressive adaptation
                            future_adjusted_deficit = avg_daily_deficit * future_adaptation
                            # Negative because deficit means weight loss
                            adjusted_kg_per_day = -(future_adjusted_deficit / energy_density)
                        else:
                            # For trend-based, assume rate continues (already correct sign)
                            adjusted_kg_per_day = base_kg_per_day
                        
                        # Project weight with adaptation
                        projected_weight = moving_avg_weight + (adjusted_kg_per_day * i)
                        
                        # Project body fat (if applicable)
                        projected_body_fat = None
                        if moving_avg_body_fat and daily_body_fat_change:
                            projected_body_fat = moving_avg_body_fat + (daily_body_fat_change * i)
                            projected_body_fat = max(3, min(60, projected_body_fat))  # Realistic bounds
                        
                        is_goal_reached = (
                            (weight_difference < 0 and projected_weight <= target_weight) or
                            (weight_difference > 0 and projected_weight >= target_weight)
                        )
                        
                        projection_data.append(ProjectionPoint(
                            date=projection_date,
                            projected_weight=round(projected_weight, 1),
                            projected_body_fat=round(projected_body_fat, 1) if projected_body_fat else None,
                            is_goal_reached=is_goal_reached
                        ))
                        
                        if is_goal_reached:
                            break
            
            else:
                message = "Set a target weight to see projections!"
            
            # Add scientific context to message if using advanced model
            if moving_avg_body_fat and energy_density != WeightTrackingService.BASE_CALORIES_PER_KG:
                message += f" (Using body composition-adjusted model: {energy_density:.0f} kcal/kg)"
            
            if adaptation_factor < 1.0:
                adaptation_pct = (1.0 - adaptation_factor) * 100
                message += f" Metabolic adaptation: {adaptation_pct:.0f}% slower metabolism."
            
            return GoalProjectionResponse(
                current_weight=round(most_recent_weight, 1),
                current_body_fat=round(most_recent_body_fat, 1) if most_recent_body_fat else None,
                target_weight=round(target_weight, 1) if target_weight else None,
                target_body_fat=round(target_body_fat, 1) if target_body_fat else None,
                moving_avg_weight=round(moving_avg_weight, 1),
                moving_avg_body_fat=round(moving_avg_body_fat, 1) if moving_avg_body_fat else None,
                daily_weight_change=round(daily_weight_change, 3),
                daily_body_fat_change=round(daily_body_fat_change, 3) if daily_body_fat_change else None,
                avg_daily_deficit=round(avg_daily_deficit, 1),
                estimated_days_to_goal=estimated_days_to_goal,
                estimated_goal_date=estimated_goal_date,
                historical_data=historical_data,
                projection_data=projection_data,
                on_track=on_track,
                message=message
            )
            
        except Exception as e:
            logger.error(f"Error calculating goal projection: {e}")
            raise
