-- Devenira Blog Publishing Setup (posts 30-44)
-- Generated 2026-04-17 per Plan Section 16 expansion (approved-post 40 trigger, batch 10 close)
-- Idempotency: uses existing "Devenira Blog" calendar + list from earlier setup. Run only once.

set scheduleData to {¬
    {"2026-05-14", "the-scale-lies-differently-in-the-morning-than-in-the-evening", "The Scale Lies Differently in the Morning Than in the Evening"}, ¬
    {"2026-05-15", "sleep-debt-ruins-a-week-of-dieting-in-three-nights", "Sleep Debt Ruins a Week of Dieting in Three Nights"}, ¬
    {"2026-05-16", "the-quiet-role-vegetables-play-in-staying-full", "The Quiet Role Vegetables Play in Staying Full"}, ¬
    {"2026-05-17", "how-do-i-stop-a-binge-from-becoming-a-binge-week", "How Do I Stop a Binge From Becoming a Binge Week"}, ¬
    {"2026-05-18", "you-look-different-to-other-people-before-yourself", "You Look Different to Other People Before Yourself"}, ¬
    {"2026-05-19", "the-first-week-of-any-diet-is-the-most-misleading-one", "The First Week of Any Diet Is the Most Misleading One"}, ¬
    {"2026-05-20", "losing-weight-is-not-the-same-as-getting-leaner", "Losing Weight Is Not the Same as Getting Leaner"}, ¬
    {"2026-05-21", "why-people-gain-more-back-than-they-lost", "Why People Gain More Back Than They Lost"}, ¬
    {"2026-05-22", "how-do-i-eat-normally-at-social-events", "How Do I Eat Normally at Social Events"}, ¬
    {"2026-05-23", "the-kind-of-person-who-stays-at-their-goal-weight", "The Kind of Person Who Stays at Their Goal Weight"}, ¬
    {"2026-05-24", "why-you-stop-losing-weight-around-month-three", "Why You Stop Losing Weight Around Month Three"}, ¬
    {"2026-05-25", "am-i-actually-hungry-or-am-i-bored", "Am I Actually Hungry or Am I Bored"}, ¬
    {"2026-05-26", "how-much-protein-do-i-actually-need-to-lose-fat", "How Much Protein Do I Actually Need to Lose Fat"}, ¬
    {"2026-05-27", "why-your-workouts-feel-harder-when-youre-dieting", "Why Your Workouts Feel Harder When You Are Dieting"}, ¬
    {"2026-05-28", "why-your-strength-increases-before-your-shape-changes", "Why Your Strength Increases Before Your Shape Changes"} ¬
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

return "Done. 15 Calendar events + 15 Reminders created in Devenira Blog for posts 30-44."
