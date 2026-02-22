-- Food Cache: stores foods found via external APIs (Open Food Facts)
-- so repeat searches are instant instead of 10-13s API calls

-- 1) Extension first (needed for trigram index)
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- 2) Table
CREATE TABLE IF NOT EXISTS food_cache (
    id TEXT PRIMARY KEY,                        -- e.g. "off_3017620422003"
    food_name TEXT NOT NULL,
    brand TEXT DEFAULT '',
    barcode TEXT DEFAULT '',
    calories REAL DEFAULT 0,
    protein REAL DEFAULT 0,
    carbs REAL DEFAULT 0,
    fat REAL DEFAULT 0,
    fiber REAL DEFAULT 0,
    sugar REAL DEFAULT 0,
    sodium REAL DEFAULT 0,
    serving_size TEXT DEFAULT '100g',
    image_url TEXT DEFAULT '',
    source TEXT DEFAULT 'openfoodfacts',
    nutriscore TEXT DEFAULT '',
    search_terms TEXT[] DEFAULT '{}',           -- which queries led to this item
    hit_count INTEGER DEFAULT 1,                -- popularity tracking
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3) Indexes (after extension + table)
CREATE INDEX IF NOT EXISTS idx_food_cache_name_trgm 
    ON food_cache USING gin (food_name gin_trgm_ops);

CREATE INDEX IF NOT EXISTS idx_food_cache_search_terms 
    ON food_cache USING gin (search_terms);

-- 4) RLS
ALTER TABLE food_cache ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone can read food cache"
    ON food_cache FOR SELECT
    TO authenticated
    USING (true);

CREATE POLICY "Service role can manage food cache"
    ON food_cache FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);
