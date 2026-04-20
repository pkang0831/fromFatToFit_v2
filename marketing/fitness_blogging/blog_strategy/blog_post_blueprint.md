# Blog Post Blueprint

Structure used for all owned-site drafts since post 1.

## File Header (front matter, meaning-based filename)

```
# Title (human-facing)

**SEO Title**: ...
**Meta Description**: ... (150–160 chars)
**Primary Keyword**: ...
**Secondary Keywords**: ...
**Category**: <one of 10>
**Format**: personal_story | deep_dive | myth_buster | qa | progress_update
**Claim Class**: 1 | 2 | 3 | 4
**Slug**: kebab-case
**Suggested Internal Links**: [2–3 existing slugs]
**Hero Image**: /founder/<filename>.jpg
**Hero Alt**: ...
**Inline Image Plan**:
  - path: /founder/...
    placement: after opening section | after section 2 | before close
    anchor: "<specific sentence fragment>"
    why here: ...
```

## Body Structure

1. **Opening** (2–4 short paragraphs): one observation, concrete.
2. **Principle section**: the flip / the reframe / the claim.
3. **Mechanism section**: why it happens (behavioral or physiological).
4. **Application section**: what to do with this.
5. **Close**: one image or one line that echoes the opening.

## Length
- 450–900 words body.
- No minimum. Don't pad.

## Tone Rules
- See style_guide.md.

## Image Rules
- Hero: per blog_cover_mapping taxonomy.
- Inline: 1–2 per post, anchored to specific sentences.
- No decorative stock.

## CTA
- Owned-site: one sentence mentioning Devenira app near the close.
- Medium variant: omit or soften to URL only.

## Pre-Flight Checklist (mandatory before marking `publish_ready`)

Run `writer_pre_flight_class_checklist.md` before saving any draft. It catches:
- claim-class undercalibration (Rule 2 corrective, introduced post-batch-13)
- banned phrases
- broken internal-link slugs
- broken hero/inline image paths
- 5-adjacent hero rule violations
- image-pool saturation (Rule T2)
- intra-batch hero/inline cross-role conflicts (Rule 8)

The reviewer subagent assumes this checklist has been run. Skipping it generates avoidable revise verdicts.
