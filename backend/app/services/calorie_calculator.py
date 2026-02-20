"""
Calorie Calculator Service
Calculates calories burned during exercises based on user profile and exercise data
"""
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class CalorieCalculator:
    """
    Calculate calories burned for different types of exercises
    
    Uses MET (Metabolic Equivalent of Task) values and user profile data
    """
    
    @staticmethod
    def calculate_cardio_calories(
        met_value: float,
        weight_kg: float,
        duration_minutes: int
    ) -> float:
        """
        Calculate calories burned for cardio/time-based exercises
        
        Formula: Calories = MET × weight(kg) × time(hours)
        
        Args:
            met_value: Metabolic Equivalent of Task (exercise intensity)
            weight_kg: User's weight in kilograms
            duration_minutes: Exercise duration in minutes
            
        Returns:
            Estimated calories burned
            
        Example:
            Running (MET 8.0), 70kg person, 30 minutes
            = 8.0 × 70 × 0.5 = 280 calories
        """
        if duration_minutes <= 0 or weight_kg <= 0 or met_value <= 0:
            return 0.0
        
        duration_hours = duration_minutes / 60.0
        calories = met_value * weight_kg * duration_hours
        
        return round(calories, 1)
    
    @staticmethod
    def calculate_strength_calories(
        met_value: float,
        weight_kg: float,
        sets: List[Dict],
        duration_minutes: Optional[int] = None
    ) -> float:
        """
        Calculate calories burned for strength/resistance training
        
        Uses hybrid approach:
        1. Base calories from MET and estimated duration
        2. Additional calories from work performed (sets × reps × weight)
        
        Args:
            met_value: MET value for the exercise (typically 5.0-8.0)
            weight_kg: User's body weight in kg
            sets: List of sets with reps and weight
                  [{"reps": 10, "weight": 50}, ...]
            duration_minutes: Total duration (optional, estimated if not provided)
            
        Returns:
            Estimated calories burned
            
        Example:
            Bench Press (MET 6.0), 70kg person
            3 sets: [10 reps × 60kg, 8 reps × 60kg, 6 reps × 60kg]
            Duration: 15 minutes
            = Base (6.0 × 70 × 0.25) + Work bonus = ~115 calories
        """
        if weight_kg <= 0 or met_value <= 0 or not sets:
            return 0.0
        
        # Estimate duration if not provided
        # Average: 2-3 minutes per set (including rest)
        if duration_minutes is None:
            duration_minutes = len(sets) * 2.5
        
        # Base calories from MET
        duration_hours = duration_minutes / 60.0
        base_calories = met_value * weight_kg * duration_hours
        
        # Additional calories from work performed
        # Formula: (total volume in kg) × 0.00175 × body weight
        # This is a simplified approximation
        total_volume = sum(s.get('reps', 0) * s.get('weight', 0) for s in sets)
        work_calories = total_volume * 0.00175 * weight_kg
        
        # Combine and apply efficiency factor (strength training is ~70% efficient)
        total_calories = (base_calories + work_calories) * 0.7
        
        return round(total_calories, 1)
    
    @staticmethod
    def calculate_bmr(
        weight_kg: float,
        height_cm: float,
        age: int,
        gender: str
    ) -> float:
        """
        Calculate Basal Metabolic Rate (BMR) using Mifflin-St Jeor Equation
        
        This is used for more accurate calorie calculations
        
        Args:
            weight_kg: Weight in kilograms
            height_cm: Height in centimeters
            age: Age in years
            gender: 'male' or 'female'
            
        Returns:
            BMR in calories per day
        """
        # Mifflin-St Jeor Equation
        if gender.lower() == 'male':
            bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5
        else:  # female
            bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161
        
        return round(bmr, 1)
    
    @staticmethod
    def calculate_tdee(
        weight_kg: float,
        height_cm: float,
        age: int,
        gender: str,
        activity_level: str = 'moderate'
    ) -> float:
        """
        Calculate Total Daily Energy Expenditure (TDEE)
        
        TDEE = BMR × Activity Factor
        
        Activity Factors:
        - sedentary: 1.2 (little or no exercise)
        - light: 1.375 (light exercise 1-3 days/week)
        - moderate: 1.55 (moderate exercise 3-5 days/week)
        - active: 1.725 (hard exercise 6-7 days/week)
        - very_active: 1.9 (very hard exercise & physical job)
        
        Args:
            weight_kg: Weight in kilograms
            height_cm: Height in centimeters
            age: Age in years
            gender: 'male' or 'female'
            activity_level: Activity level category
            
        Returns:
            TDEE in calories per day
        """
        # Calculate BMR
        bmr = CalorieCalculator.calculate_bmr(weight_kg, height_cm, age, gender)
        
        # Activity factors
        activity_factors = {
            'sedentary': 1.2,
            'light': 1.375,
            'moderate': 1.55,
            'active': 1.725,
            'very_active': 1.9
        }
        
        # Get activity factor (default to moderate if not found)
        factor = activity_factors.get(activity_level.lower(), 1.55)
        
        # Calculate TDEE
        tdee = bmr * factor
        
        return round(tdee, 1)

    @staticmethod
    def adjust_for_gender_age(
        base_calories: float,
        age: int,
        gender: str
    ) -> float:
        """
        Adjust calorie burn based on gender and age
        
        Women typically burn ~10% fewer calories than men
        Metabolism decreases ~2% per decade after 30
        
        Args:
            base_calories: Base calorie calculation
            age: User's age
            gender: 'male' or 'female'
            
        Returns:
            Adjusted calories
        """
        adjusted = base_calories
        
        # Gender adjustment
        if gender.lower() == 'female':
            adjusted *= 0.9
        
        # Age adjustment (after 30)
        if age > 30:
            decades_over_30 = (age - 30) / 10
            reduction = decades_over_30 * 0.02
            adjusted *= (1 - reduction)
        
        return round(adjusted, 1)
    
    @classmethod
    def calculate_exercise_calories(
        cls,
        exercise_type: str,
        met_value: float,
        user_profile: Dict,
        duration_minutes: Optional[int] = None,
        sets: Optional[List[Dict]] = None
    ) -> Dict[str, float]:
        """
        Main method to calculate calories for any exercise
        
        Args:
            exercise_type: 'cardio', 'strength', 'flexibility', 'sports'
            met_value: MET value from exercise library
            user_profile: Dict with 'weight_kg', 'height_cm', 'age', 'gender'
            duration_minutes: Duration for cardio exercises
            sets: Sets data for strength exercises
            
        Returns:
            {
                'calories_burned': float,
                'calories_adjusted': float (with gender/age adjustment),
                'calculation_method': str
            }
        """
        weight_kg = user_profile.get('weight_kg', 70.0)
        height_cm = user_profile.get('height_cm', 170.0)
        age = user_profile.get('age', 30)
        gender = user_profile.get('gender', 'male')
        
        # Calculate base calories
        if exercise_type == 'cardio':
            if not duration_minutes or duration_minutes <= 0:
                return {
                    'calories_burned': 0.0,
                    'calories_adjusted': 0.0,
                    'calculation_method': 'error: duration required for cardio'
                }
            
            base_calories = cls.calculate_cardio_calories(
                met_value, weight_kg, duration_minutes
            )
            method = f'cardio_met_{met_value}'
            
        elif exercise_type == 'strength':
            if not sets or len(sets) == 0:
                return {
                    'calories_burned': 0.0,
                    'calories_adjusted': 0.0,
                    'calculation_method': 'error: sets required for strength'
                }
            
            base_calories = cls.calculate_strength_calories(
                met_value, weight_kg, sets, duration_minutes
            )
            method = f'strength_met_{met_value}_sets_{len(sets)}'
            
        else:  # flexibility, sports - use time-based
            if not duration_minutes or duration_minutes <= 0:
                duration_minutes = 30  # Default estimate
            
            base_calories = cls.calculate_cardio_calories(
                met_value, weight_kg, duration_minutes
            )
            method = f'{exercise_type}_met_{met_value}'
        
        # Apply gender and age adjustments
        adjusted_calories = cls.adjust_for_gender_age(
            base_calories, age, gender
        )
        
        return {
            'calories_burned': base_calories,
            'calories_adjusted': adjusted_calories,
            'calculation_method': method
        }


# MET Reference Values (Compendium of Physical Activities)
MET_VALUES = {
    # Cardio/Running
    'walking_slow': 2.5,        # 2 mph
    'walking_moderate': 3.5,     # 3 mph
    'walking_brisk': 4.5,        # 4 mph
    'jogging': 7.0,              # 5 mph
    'running_moderate': 9.0,     # 6 mph
    'running_fast': 11.5,        # 7 mph
    'running_very_fast': 14.0,   # 8+ mph
    'sprint': 18.0,
    
    # Cycling
    'cycling_leisure': 4.0,      # <10 mph
    'cycling_moderate': 8.0,     # 12-14 mph
    'cycling_vigorous': 12.0,    # 16+ mph
    'stationary_bike_light': 3.5,
    'stationary_bike_moderate': 6.8,
    'stationary_bike_vigorous': 10.5,
    'spin_class': 8.5,
    
    # Cardio Machines
    'elliptical_moderate': 5.0,
    'elliptical_vigorous': 8.0,
    'stair_climber': 9.0,
    'rowing_moderate': 7.0,
    'rowing_vigorous': 12.0,
    
    # Swimming
    'swimming_leisure': 6.0,
    'swimming_laps_moderate': 8.0,
    'swimming_laps_vigorous': 11.0,
    
    # HIIT
    'burpees': 10.0,
    'mountain_climbers': 8.0,
    'jumping_jacks': 8.0,
    'high_knees': 8.5,
    'jump_rope': 12.0,
    'box_jumps': 12.0,
    
    # Strength Training
    'weightlifting_light': 3.0,
    'weightlifting_moderate': 5.0,
    'weightlifting_vigorous': 6.0,
    'weightlifting_power': 8.0,
    'bodyweight_exercises': 8.0,
    
    # Sports
    'basketball': 6.5,
    'tennis_singles': 8.0,
    'soccer': 10.0,
    'volleyball': 4.0,
    
    # Other
    'yoga': 2.5,
    'pilates': 3.0,
    'zumba': 7.5,
    'dance_cardio': 7.0,
}
