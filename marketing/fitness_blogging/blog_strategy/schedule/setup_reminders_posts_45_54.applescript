-- Devenira Blog Publishing Setup (posts 45-54 in publish order = approved-posts 52-61)
-- Generated 2026-04-19 per Plan §18 (60-post checkpoint expansion, batch 12 close)
-- Idempotency: uses existing "Devenira Blog" calendar + list. Run only once.
-- This file extends `setup_reminders_posts_30_44.applescript` by adding the 10 new posts from batches 11-12.

set scheduleData to {¬
    {"2026-05-29", "the-quiet-erosion-of-not-believing-your-progress", "The Quiet Erosion of Not Believing Your Progress"}, ¬
    {"2026-05-30", "progress-photos-can-lie-as-much-as-the-mirror-does", "Progress Photos Can Lie as Much as the Mirror Does"}, ¬
    {"2026-05-31", "is-this-craving-the-food-or-the-deprivation-talking", "Is This Craving the Food or the Deprivation Talking"}, ¬
    {"2026-06-01", "the-same-number-on-the-scale-feels-different-at-30-than-at-20", "The Same Number on the Scale Feels Different at 30 Than at 20"}, ¬
    {"2026-06-02", "the-small-wins-between-progress-updates-are-the-real-program", "The Small Wins Between Progress Updates Are the Real Program"}, ¬
    {"2026-06-03", "the-first-month-of-maintenance-feels-nothing-like-the-diet", "The First Month of Maintenance Feels Nothing Like the Diet"}, ¬
    {"2026-06-04", "why-does-my-hunger-spike-at-night-when-i-was-fine-all-day", "Why Does My Hunger Spike at Night When I Was Fine All Day"}, ¬
    {"2026-06-05", "the-plateau-that-was-actually-an-honesty-problem", "The Plateau That Was Actually an Honesty Problem"}, ¬
    {"2026-06-06", "progress-update-4-the-body-finally-stopped-being-the-loud-thing", "Progress Update 4: The Body Finally Stopped Being the Loud Thing"}, ¬
    {"2026-06-07", "clothes-tell-you-the-truth-the-mirror-cannot", "Clothes Tell You the Truth the Mirror Cannot"} ¬
}

tell application "Calendar"
    activate
    try
        set targetCal to first calendar whose name is "Devenira Blog"
    on error
        set targetCal to make new calendar with properties {name:"Devenira Blog"}
    end try
    repeat with entry in scheduleData
        set dateString to item 1 of entry
        set slugValue to item 2 of entry
        set titleValue to item 3 of entry
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
            make new reminder with properties {name:"Publish: " & slugValue & " → Medium + SNS", due date:dueDate}
        end tell
    end repeat
end tell
