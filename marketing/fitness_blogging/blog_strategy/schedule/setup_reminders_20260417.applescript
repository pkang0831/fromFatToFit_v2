-- Devenira Blog Publishing Setup (posts 20-29)
-- Run once to populate Calendar events + Reminders
-- Idempotency: uses "Devenira Blog" calendar + list; re-running this file duplicates entries, so run only once.

set scheduleData to {¬
    {"2026-05-04", "exercise-isnt-shrinking-you-the-way-you-expected", "Exercise Is Not Shrinking You the Way You Expected"}, ¬
    {"2026-05-05", "the-unglamorous-middle-of-transformation", "The Unglamorous Middle of a Transformation"}, ¬
    {"2026-05-06", "is-it-bloat-or-is-it-fat", "Is It Bloat or Is It Fat"}, ¬
    {"2026-05-07", "a-plateau-is-a-data-point-not-a-failure", "A Plateau Is a Data Point, Not a Failure"}, ¬
    {"2026-05-08", "the-body-looks-different-from-behind", "The Body Looks Different From Behind"}, ¬
    {"2026-05-09", "progress-update-3-past-the-messy-middle", "Progress Update 3: Past the Messy Middle"}, ¬
    {"2026-05-10", "when-the-workout-becomes-therapy-not-punishment", "When the Workout Becomes Therapy, Not Punishment"}, ¬
    {"2026-05-11", "hunger-in-maintenance-is-different-from-hunger-on-a-diet", "Hunger in Maintenance Is Different from Hunger on a Diet"}, ¬
    {"2026-05-12", "the-friend-who-never-diets-and-never-gains", "The Friend Who Never Diets and Never Gains"}, ¬
    {"2026-05-13", "how-do-you-know-when-youve-reached-your-set-point", "How Do You Know When You Have Reached Your Set Point"} ¬
}

-- === Calendar Events ===
tell application "Calendar"
    activate
    -- Ensure target calendar exists
    try
        set targetCal to first calendar whose name is "Devenira Blog"
    on error
        set targetCal to make new calendar with properties {name:"Devenira Blog"}
    end try
    repeat with entry in scheduleData
        set dateString to item 1 of entry
        set slugValue to item 2 of entry
        set titleValue to item 3 of entry
        -- Parse date (YYYY-MM-DD), set start to 09:00, end to 09:15
        set yearPart to (text 1 thru 4 of dateString) as integer
        set monthPart to (text 6 thru 7 of dateString) as integer
        set dayPart to (text 9 thru 10 of dateString) as integer
        set startDate to current date
        set year of startDate to yearPart
        set month of startDate to monthPart
        set day of startDate to dayPart
        set hours of startDate to 9
        set minutes of startDate to 0
        set seconds of startDate to 0
        set endDate to startDate + (15 * minutes)
        tell targetCal
            make new event with properties {summary:"Publish: " & titleValue, start date:startDate, end date:endDate, description:"Slug: " & slugValue & linefeed & "Medium package: marketing/fitness_blogging/blog_strategy/medium_launch/"}
        end tell
    end repeat
end tell

-- === Reminders ===
tell application "Reminders"
    activate
    try
        set targetList to first list whose name is "Devenira Blog"
    on error
        set targetList to make new list with properties {name:"Devenira Blog"}
    end try
    repeat with entry in scheduleData
        set dateString to item 1 of entry
        set slugValue to item 2 of entry
        set titleValue to item 3 of entry
        set yearPart to (text 1 thru 4 of dateString) as integer
        set monthPart to (text 6 thru 7 of dateString) as integer
        set dayPart to (text 9 thru 10 of dateString) as integer
        set dueDate to current date
        set year of dueDate to yearPart
        set month of dueDate to monthPart
        set day of dueDate to dayPart
        set hours of dueDate to 8
        set minutes of dueDate to 0
        set seconds of dueDate to 0
        tell targetList
            make new reminder with properties {name:"Publish: " & slugValue & " → Medium + SNS", due date:dueDate, body:"Title: " & titleValue & linefeed & "1. Publish to Medium (09:00)" & linefeed & "2. Share to SNS (11:00)" & linefeed & "3. Log URL in wave_01_tracker.md"}
        end tell
    end repeat
end tell

return "Done. 10 Calendar events + 10 Reminders created in 'Devenira Blog'."
