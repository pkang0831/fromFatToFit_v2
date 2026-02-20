"""
Caching layer for user food preferences
Improves performance by reducing database queries
"""
from typing import Optional, Dict
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class PreferenceCache:
    """
    In-memory cache for user preferences
    
    In production, replace with Redis for:
    - Distributed caching across multiple servers
    - Persistent cache across restarts
    - TTL (time-to-live) management
    - Cache invalidation strategies
    """
    
    def __init__(self, ttl_minutes: int = 30):
        self.cache: Dict[str, Dict] = {}
        self.timestamps: Dict[str, datetime] = {}
        self.ttl = timedelta(minutes=ttl_minutes)
    
    def get(self, user_id: str) -> Optional[Dict]:
        """Get cached preferences for a user"""
        if user_id not in self.cache:
            return None
        
        # Check if cache is still valid
        timestamp = self.timestamps.get(user_id)
        if timestamp and datetime.now() - timestamp > self.ttl:
            # Cache expired
            self.invalidate(user_id)
            return None
        
        logger.debug(f"Cache HIT for user {user_id}")
        return self.cache[user_id]
    
    def set(self, user_id: str, preferences: Dict):
        """Cache preferences for a user"""
        self.cache[user_id] = preferences
        self.timestamps[user_id] = datetime.now()
        logger.debug(f"Cache SET for user {user_id}")
    
    def invalidate(self, user_id: str):
        """Invalidate cache for a user"""
        if user_id in self.cache:
            del self.cache[user_id]
        if user_id in self.timestamps:
            del self.timestamps[user_id]
        logger.debug(f"Cache INVALIDATE for user {user_id}")
    
    def clear_all(self):
        """Clear entire cache"""
        self.cache.clear()
        self.timestamps.clear()
        logger.info("Cache CLEARED")


# Global cache instance
# In production, use Redis with redis-py or aioredis
preference_cache = PreferenceCache(ttl_minutes=30)


async def get_cached_preferences(db_client, user_id: str) -> Dict:
    """
    Get user preferences with caching
    
    Usage in services:
        from app.services.preference_cache import get_cached_preferences
        prefs = await get_cached_preferences(supabase, user_id)
    """
    # Try cache first
    cached = preference_cache.get(user_id)
    if cached is not None:
        return cached
    
    # Cache miss - fetch from database
    try:
        result = db_client.table('user_food_preferences').select('*').eq(
            'user_id', user_id
        ).execute()
        
        if result.data and len(result.data) > 0:
            prefs = result.data[0]
            preferences = {
                'favorite_foods': prefs.get('favorite_foods', []),
                'disliked_foods': prefs.get('disliked_foods', []),
                'allergies': prefs.get('allergies', []),
                'dietary_restrictions': prefs.get('dietary_restrictions', []),
                'avoid_high_sodium': prefs.get('avoid_high_sodium', False),
                'avoid_high_sugar': prefs.get('avoid_high_sugar', False),
                'prefer_high_protein': prefs.get('prefer_high_protein', False)
            }
        else:
            # Default empty preferences
            preferences = {
                'favorite_foods': [],
                'disliked_foods': [],
                'allergies': [],
                'dietary_restrictions': [],
                'avoid_high_sodium': False,
                'avoid_high_sugar': False,
                'prefer_high_protein': False
            }
        
        # Cache the result
        preference_cache.set(user_id, preferences)
        logger.debug(f"Cache MISS for user {user_id} - fetched from DB")
        
        return preferences
        
    except Exception as e:
        logger.error(f"Error fetching preferences: {e}")
        return {
            'favorite_foods': [],
            'disliked_foods': [],
            'allergies': [],
            'dietary_restrictions': [],
            'avoid_high_sodium': False,
            'avoid_high_sugar': False,
            'prefer_high_protein': False
        }


async def invalidate_user_cache(user_id: str):
    """
    Invalidate cache when user updates preferences
    
    Call this after updating preferences:
        await invalidate_user_cache(user_id)
    """
    preference_cache.invalidate(user_id)


# === Redis Implementation Example ===
# Uncomment and use in production with Redis installed

"""
import redis.asyncio as redis
import json

redis_client = redis.Redis(
    host='localhost',
    port=6379,
    db=0,
    decode_responses=True
)

async def get_cached_preferences_redis(db_client, user_id: str) -> Dict:
    '''Get user preferences with Redis caching'''
    cache_key = f"user_prefs:{user_id}"
    
    # Try Redis cache
    cached = await redis_client.get(cache_key)
    if cached:
        logger.debug(f"Redis cache HIT for user {user_id}")
        return json.loads(cached)
    
    # Fetch from DB
    result = db_client.table('user_food_preferences').select('*').eq(
        'user_id', user_id
    ).execute()
    
    preferences = {...}  # Same logic as above
    
    # Cache in Redis with 30 minute expiry
    await redis_client.setex(
        cache_key,
        1800,  # 30 minutes
        json.dumps(preferences)
    )
    
    return preferences

async def invalidate_user_cache_redis(user_id: str):
    '''Invalidate Redis cache'''
    cache_key = f"user_prefs:{user_id}"
    await redis_client.delete(cache_key)
"""
