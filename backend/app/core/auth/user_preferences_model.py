"""User Preferences Model for PostgreSQL."""
import asyncpg
import json
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.config import settings


class UserPreferencesModel:
    """Database model for user preferences."""
    
    def __init__(self):
        self.table_name = "user_preferences"
    
    async def get_connection(self):
        """Get database connection."""
        return await asyncpg.connect(settings.postgres.url)
    
    async def initialize(self):
        """Initialize the database table."""
        conn = await self.get_connection()
        try:
            await conn.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.table_name} (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    preferred_colors TEXT[] DEFAULT '{{}}',
                    preferred_fabrics TEXT[] DEFAULT '{{}}',
                    preferred_styles TEXT[] DEFAULT '{{}}',
                    preferred_occasions TEXT[] DEFAULT '{{}}',
                    body_type VARCHAR(50),
                    fit_preference VARCHAR(50),
                    size_preference VARCHAR(10),
                    budget_min DECIMAL(10, 2),
                    budget_max DECIMAL(10, 2),
                    budget_currency VARCHAR(3) DEFAULT 'USD',
                    language_preference VARCHAR(10) DEFAULT 'en',
                    notification_preferences JSONB DEFAULT '{{}}',
                    preferred_brands TEXT[] DEFAULT '{{}}',
                    avoid_colors TEXT[] DEFAULT '{{}}',
                    avoid_fabrics TEXT[] DEFAULT '{{}}',
                    interaction_count INTEGER DEFAULT 0,
                    last_interaction TIMESTAMP,
                    preference_confidence FLOAT DEFAULT 0.0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create index
            try:
                await conn.execute(f"""
                    CREATE INDEX IF NOT EXISTS idx_{self.table_name}_user_id 
                    ON {self.table_name}(user_id)
                """)
            except Exception:
                pass
                
        finally:
            await conn.close()
    
    async def create_preferences(self, user_id: str) -> str:
        """Create default preferences for a user."""
        conn = await self.get_connection()
        try:
            result = await conn.fetchval(
                f"""
                INSERT INTO {self.table_name} (user_id)
                VALUES ($1)
                RETURNING id
                """,
                user_id
            )
            return str(result)
        finally:
            await conn.close()
    
    async def get_preferences(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user preferences."""
        conn = await self.get_connection()
        try:
            row = await conn.fetchrow(
                f"""
                SELECT * FROM {self.table_name} WHERE user_id = $1
                """,
                user_id
            )
            if row:
                return dict(row)
            return None
        finally:
            await conn.close()
    
    async def update_preferences(
        self,
        user_id: str,
        preferred_colors: Optional[List[str]] = None,
        preferred_fabrics: Optional[List[str]] = None,
        preferred_styles: Optional[List[str]] = None,
        preferred_occasions: Optional[List[str]] = None,
        body_type: Optional[str] = None,
        fit_preference: Optional[str] = None,
        size_preference: Optional[str] = None,
        budget_min: Optional[float] = None,
        budget_max: Optional[float] = None,
        budget_currency: Optional[str] = None,
        language_preference: Optional[str] = None,
        preferred_brands: Optional[List[str]] = None,
        avoid_colors: Optional[List[str]] = None,
        avoid_fabrics: Optional[List[str]] = None,
        notification_preferences: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Update user preferences."""
        conn = await self.get_connection()
        try:
            # Build dynamic update query
            updates = []
            values = []
            param_count = 1
            
            if preferred_colors is not None:
                updates.append(f"preferred_colors = ${param_count}")
                values.append(preferred_colors)
                param_count += 1
            
            if preferred_fabrics is not None:
                updates.append(f"preferred_fabrics = ${param_count}")
                values.append(preferred_fabrics)
                param_count += 1
            
            if preferred_styles is not None:
                updates.append(f"preferred_styles = ${param_count}")
                values.append(preferred_styles)
                param_count += 1
            
            if preferred_occasions is not None:
                updates.append(f"preferred_occasions = ${param_count}")
                values.append(preferred_occasions)
                param_count += 1
            
            if body_type is not None:
                updates.append(f"body_type = ${param_count}")
                values.append(body_type)
                param_count += 1
            
            if fit_preference is not None:
                updates.append(f"fit_preference = ${param_count}")
                values.append(fit_preference)
                param_count += 1
            
            if size_preference is not None:
                updates.append(f"size_preference = ${param_count}")
                values.append(size_preference)
                param_count += 1
            
            if budget_min is not None:
                updates.append(f"budget_min = ${param_count}")
                values.append(budget_min)
                param_count += 1
            
            if budget_max is not None:
                updates.append(f"budget_max = ${param_count}")
                values.append(budget_max)
                param_count += 1
            
            if budget_currency is not None:
                updates.append(f"budget_currency = ${param_count}")
                values.append(budget_currency)
                param_count += 1
            
            if language_preference is not None:
                updates.append(f"language_preference = ${param_count}")
                values.append(language_preference)
                param_count += 1
            
            if preferred_brands is not None:
                updates.append(f"preferred_brands = ${param_count}")
                values.append(preferred_brands)
                param_count += 1
            
            if avoid_colors is not None:
                updates.append(f"avoid_colors = ${param_count}")
                values.append(avoid_colors)
                param_count += 1
            
            if avoid_fabrics is not None:
                updates.append(f"avoid_fabrics = ${param_count}")
                values.append(avoid_fabrics)
                param_count += 1
            
            if notification_preferences is not None:
                updates.append(f"notification_preferences = ${param_count}")
                values.append(json.dumps(notification_preferences))
                param_count += 1
            
            if not updates:
                return await self.get_preferences(user_id)
            
            # Add user_id to values
            values.append(user_id)
            
            query = f"""
                UPDATE {self.table_name}
                SET {', '.join(updates)}
                WHERE user_id = ${param_count}
                RETURNING *
            """
            
            row = await conn.fetchrow(query, *values)
            return dict(row) if row else None
        finally:
            await conn.close()
    
    async def increment_interaction(self, user_id: str) -> None:
        """Increment interaction count."""
        conn = await self.get_connection()
        try:
            await conn.execute(
                f"""
                UPDATE {self.table_name}
                SET interaction_count = interaction_count + 1,
                    last_interaction = CURRENT_TIMESTAMP
                WHERE user_id = $1
                """,
                user_id
            )
        finally:
            await conn.close()
    
    async def update_confidence(self, user_id: str, confidence: float) -> None:
        """Update preference confidence score."""
        conn = await self.get_connection()
        try:
            await conn.execute(
                f"""
                UPDATE {self.table_name}
                SET preference_confidence = $2
                WHERE user_id = $1
                """,
                user_id, confidence
            )
        finally:
            await conn.close()
    
    async def delete_preferences(self, user_id: str) -> bool:
        """Delete user preferences."""
        conn = await self.get_connection()
        try:
            result = await conn.execute(
                f"DELETE FROM {self.table_name} WHERE user_id = $1",
                user_id
            )
            return result != "DELETE 0"
        finally:
            await conn.close()
    
    async def get_recommendation_filters(self, user_id: str) -> Dict[str, Any]:
        """Get filters for product recommendations based on user preferences."""
        prefs = await self.get_preferences(user_id)
        if not prefs:
            return {}
        
        filters = {}
        
        # Positive filters
        if prefs.get("preferred_colors"):
            filters["colors"] = prefs["preferred_colors"]
        
        if prefs.get("preferred_fabrics"):
            filters["fabrics"] = prefs["preferred_fabrics"]
        
        if prefs.get("preferred_styles"):
            filters["styles"] = prefs["preferred_styles"]
        
        if prefs.get("preferred_occasions"):
            filters["occasions"] = prefs["preferred_occasions"]
        
        if prefs.get("preferred_brands"):
            filters["brands"] = prefs["preferred_brands"]
        
        # Negative filters
        if prefs.get("avoid_colors"):
            filters["exclude_colors"] = prefs["avoid_colors"]
        
        if prefs.get("avoid_fabrics"):
            filters["exclude_fabrics"] = prefs["avoid_fabrics"]
        
        # Budget
        if prefs.get("budget_min"):
            filters["price_min"] = float(prefs["budget_min"])
        
        if prefs.get("budget_max"):
            filters["price_max"] = float(prefs["budget_max"])
        
        # Body type
        if prefs.get("body_type"):
            filters["body_type"] = prefs["body_type"]
        
        # Fit preference
        if prefs.get("fit_preference"):
            filters["fit"] = prefs["fit_preference"]
        
        return filters


# Singleton instance
user_preferences_db = UserPreferencesModel()
