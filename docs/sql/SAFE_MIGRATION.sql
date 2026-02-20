-- ===================================================================
-- 🚀 SAFE MIGRATION (중복 방지)
-- ===================================================================
-- 이 파일은 중복 삽입을 방지합니다
-- ===================================================================

-- Step 1: Add MET values to exercise library
ALTER TABLE exercise_library 
ADD COLUMN IF NOT EXISTS met_value DECIMAL(4,1) DEFAULT 5.0,
ADD COLUMN IF NOT EXISTS exercise_type TEXT DEFAULT 'strength' CHECK (exercise_type IN ('cardio', 'strength', 'flexibility', 'sports'));

-- Add unique constraint on name (if not exists)
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'exercise_library_name_key'
    ) THEN
        ALTER TABLE exercise_library ADD CONSTRAINT exercise_library_name_key UNIQUE (name);
    END IF;
END $$;

-- Update existing strength exercises
UPDATE exercise_library SET met_value = 6.0, exercise_type = 'strength' WHERE name = 'Barbell Back Squat';
UPDATE exercise_library SET met_value = 6.0, exercise_type = 'strength' WHERE name = 'Bench Press';
UPDATE exercise_library SET met_value = 6.0, exercise_type = 'strength' WHERE name = 'Deadlift';
UPDATE exercise_library SET met_value = 8.0, exercise_type = 'strength' WHERE name = 'Pull-ups';
UPDATE exercise_library SET met_value = 6.0, exercise_type = 'strength' WHERE name = 'Overhead Press';
UPDATE exercise_library SET met_value = 5.0, exercise_type = 'strength' WHERE name = 'Dumbbell Row';
UPDATE exercise_library SET met_value = 8.0, exercise_type = 'strength' WHERE name = 'Push-ups';
UPDATE exercise_library SET met_value = 5.0, exercise_type = 'strength' WHERE name = 'Lunges';
UPDATE exercise_library SET met_value = 4.0, exercise_type = 'strength' WHERE name = 'Plank';
UPDATE exercise_library SET met_value = 6.0, exercise_type = 'strength' WHERE name = 'Romanian Deadlift';

-- Step 2: Add calories field to workout_logs
ALTER TABLE workout_logs 
ADD COLUMN IF NOT EXISTS calories_burned DECIMAL(6,1) DEFAULT 0.0;

-- Step 3: Add 27 cardio exercises (with duplicate check)
INSERT INTO exercise_library (name, category, muscle_groups, form_instructions, difficulty, met_value, exercise_type) 
SELECT * FROM (VALUES
-- Running/Jogging
('Treadmill Running', 'Cardio', ARRAY['Legs', 'Cardiovascular'], 'Set treadmill to desired speed. Maintain upright posture, land mid-foot, swing arms naturally. Start with 5-10 min warm-up at slower pace. Gradually increase speed. Cool down for 5 min.', 'beginner', 9.0, 'cardio'),
('Outdoor Running', 'Cardio', ARRAY['Legs', 'Cardiovascular'], 'Run at comfortable pace outdoors. Keep shoulders relaxed, eyes forward. Land mid-foot with each stride. Maintain steady breathing rhythm. Start with 20-30 min sessions.', 'beginner', 9.0, 'cardio'),
('Sprint Intervals', 'Cardio', ARRAY['Legs', 'Cardiovascular'], 'Alternate between high-intensity sprints (30 sec) and recovery jogs (90 sec). Repeat 6-10 times. Push hard during sprints, recover fully during jogs. Excellent for fat burning.', 'advanced', 14.0, 'cardio'),
-- Cycling
('Stationary Bike', 'Cardio', ARRAY['Legs', 'Cardiovascular'], 'Adjust seat so knee has slight bend at bottom. Maintain steady cadence (80-100 RPM). Keep core engaged, shoulders relaxed. Vary resistance for intensity. Great low-impact cardio option.', 'beginner', 6.8, 'cardio'),
('Outdoor Cycling', 'Cardio', ARRAY['Legs', 'Cardiovascular'], 'Cycle at moderate to high intensity outdoors. Maintain proper bike posture, engage core. Use gears appropriately for terrain. Excellent endurance builder and calorie burner.', 'intermediate', 8.0, 'cardio'),
('Spin Class', 'Cardio', ARRAY['Legs', 'Cardiovascular'], 'Follow instructor-led cycling workout with varied resistance and speed. Stand and sit intervals, climbs, and sprints. High-intensity group cardio session.', 'intermediate', 8.5, 'cardio'),
-- Elliptical
('Elliptical Machine', 'Cardio', ARRAY['Legs', 'Arms', 'Cardiovascular'], 'Stand upright, grip handles lightly. Push and pull with legs in smooth motion. Engage core throughout. Low-impact alternative to running. Adjust resistance and incline for intensity.', 'beginner', 5.0, 'cardio'),
-- Rowing
('Rowing Machine', 'Cardio', ARRAY['Back', 'Legs', 'Arms', 'Core', 'Cardiovascular'], 'Start with legs bent, arms extended. Push with legs first, then lean back slightly, finally pull handle to chest. Reverse the motion smoothly. Full-body cardio workout.', 'intermediate', 7.0, 'cardio'),
-- Swimming
('Swimming Laps', 'Cardio', ARRAY['Full Body', 'Cardiovascular'], 'Swim continuous laps using freestyle, breaststroke, or backstroke. Maintain steady breathing rhythm. Excellent low-impact full-body cardio. Great for joint health and endurance.', 'intermediate', 8.0, 'cardio'),
('Aqua Aerobics', 'Cardio', ARRAY['Full Body', 'Cardiovascular'], 'Perform aerobic exercises in water. Low-impact, high resistance. Great for all fitness levels. Reduces joint stress while building cardiovascular fitness.', 'beginner', 4.0, 'cardio'),
-- Jump Rope
('Jump Rope', 'Cardio', ARRAY['Legs', 'Shoulders', 'Cardiovascular'], 'Jump continuously with rope. Land on balls of feet, keep jumps low. Start with 30 sec intervals. Work up to longer duration. Excellent for coordination and cardio conditioning.', 'intermediate', 12.0, 'cardio'),
-- HIIT
('Burpees', 'Cardio', ARRAY['Full Body', 'Cardiovascular'], 'Start standing, drop to plank, do push-up, jump feet to hands, explosive jump up. High-intensity full-body movement. Modify by removing push-up or jump for easier version.', 'advanced', 10.0, 'cardio'),
('Mountain Climbers', 'Cardio', ARRAY['Core', 'Shoulders', 'Legs', 'Cardiovascular'], 'Start in plank position. Alternate bringing knees to chest rapidly. Keep core tight, hips level. High-intensity cardio and core workout.', 'intermediate', 8.0, 'cardio'),
('Jumping Jacks', 'Cardio', ARRAY['Full Body', 'Cardiovascular'], 'Start standing, jump feet out while raising arms overhead. Jump back to start. Maintain steady rhythm. Classic cardio warm-up exercise. Modify to low-impact by stepping instead.', 'beginner', 8.0, 'cardio'),
('Box Jumps', 'Cardio', ARRAY['Legs', 'Cardiovascular'], 'Stand facing sturdy box. Jump explosively onto box, landing softly with both feet. Step down. Builds power and cardiovascular fitness. Start with lower height.', 'advanced', 12.0, 'cardio'),
('High Knees', 'Cardio', ARRAY['Legs', 'Core', 'Cardiovascular'], 'Run in place, bringing knees up to hip level with each step. Pump arms vigorously. Maintain fast pace. Great cardio warm-up or HIIT exercise.', 'intermediate', 8.5, 'cardio'),
-- Walking
('Brisk Walking', 'Cardio', ARRAY['Legs', 'Cardiovascular'], 'Walk at fast pace (3-4 mph). Maintain upright posture, swing arms naturally. Great low-impact cardio option for beginners or active recovery.', 'beginner', 4.5, 'cardio'),
('Incline Walking', 'Cardio', ARRAY['Legs', 'Glutes', 'Cardiovascular'], 'Walk on incline (treadmill or hills). Increases intensity without running. Great for building leg strength while doing cardio. Engage glutes on incline.', 'beginner', 5.5, 'cardio'),
-- Stair Climbing
('Stair Climber Machine', 'Cardio', ARRAY['Legs', 'Glutes', 'Cardiovascular'], 'Climb continuous stairs on machine. Keep posture upright, avoid leaning on handles. Great for leg and glute conditioning with cardio benefits.', 'intermediate', 9.0, 'cardio'),
('Stair Running', 'Cardio', ARRAY['Legs', 'Cardiovascular'], 'Run up stairs at fast pace. Walk down for recovery. Repeat. High-intensity leg and cardio workout. Builds power and endurance.', 'advanced', 15.0, 'cardio'),
-- Dance/Aerobics
('Zumba', 'Cardio', ARRAY['Full Body', 'Cardiovascular'], 'Follow dance-based cardio workout with Latin music. Combines cardio, coordination, and fun. Great for burning calories while enjoying movement.', 'beginner', 7.5, 'cardio'),
('Dance Cardio', 'Cardio', ARRAY['Full Body', 'Cardiovascular'], 'Follow choreographed dance movements at cardio pace. Improves coordination, burns calories, and builds cardiovascular endurance. Fun alternative to traditional cardio.', 'beginner', 7.0, 'cardio'),
('Step Aerobics', 'Cardio', ARRAY['Legs', 'Cardiovascular'], 'Perform choreographed movements stepping on and off elevated platform. Adjustable intensity with platform height. Classic cardio workout.', 'intermediate', 8.0, 'cardio'),
-- Battle Ropes/Functional
('Battle Ropes', 'Cardio', ARRAY['Arms', 'Shoulders', 'Core', 'Cardiovascular'], 'Create waves with heavy ropes using alternating arm movements. High-intensity upper body and core cardio. Work for 30 sec intervals with rest.', 'advanced', 10.0, 'cardio'),
('Kettlebell Swings', 'Cardio', ARRAY['Legs', 'Glutes', 'Core', 'Cardiovascular'], 'Hinge at hips, swing kettlebell between legs then up to shoulder height using hip thrust. Powerful cardio and strength combo. Keep back flat, core tight.', 'intermediate', 8.0, 'strength'),
-- Sports
('Basketball', 'Cardio', ARRAY['Full Body', 'Cardiovascular'], 'Play basketball for cardio benefits. Combines running, jumping, and coordination. Great for building cardiovascular endurance through sport.', 'intermediate', 6.5, 'sports'),
('Tennis', 'Cardio', ARRAY['Full Body', 'Cardiovascular'], 'Play tennis for cardiovascular fitness. Combines sprints, lateral movement, and coordination. Excellent for building agility and endurance.', 'intermediate', 8.0, 'sports'),
('Soccer/Football', 'Cardio', ARRAY['Legs', 'Cardiovascular'], 'Play soccer for cardio workout. Continuous running with sprints and changes in direction. Builds cardiovascular endurance and leg strength.', 'intermediate', 10.0, 'sports')
) AS v(name, category, muscle_groups, form_instructions, difficulty, met_value, exercise_type)
WHERE NOT EXISTS (
    SELECT 1 FROM exercise_library WHERE exercise_library.name = v.name
);
