"""Design agent for customizing chat appearance."""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class DesignStyle(Enum):
    """Design style options."""
    MODERN = "modern"
    CLASSIC = "classic"
    MINIMALIST = "minimalist"
    GAMING = "gaming"
    PROFESSIONAL = "professional"


@dataclass
class ChatTheme:
    """Chat theme configuration."""
    primary_color: str
    secondary_color: str
    background_color: str
    text_color: str
    font_family: str
    border_radius: str
    dark_mode: bool = False
    custom_css: Optional[str] = None


class DesignAgent:
    """Design agent for chat customization."""
    
    # Predefined themes
    THEMES = {
        DesignStyle.MODERN: ChatTheme(
            primary_color="#6366f1",
            secondary_color="#8b5cf6",
            background_color="#ffffff",
            text_color="#1f2937",
            font_family="Inter, sans-serif",
            border_radius="16px",
            dark_mode=False
        ),
        DesignStyle.CLASSIC: ChatTheme(
            primary_color="#3b82f6",
            secondary_color="#60a5fa",
            background_color="#f9fafb",
            text_color="#374151",
            font_family="Roboto, sans-serif",
            border_radius="8px",
            dark_mode=False
        ),
        DesignStyle.MINIMALIST: ChatTheme(
            primary_color="#000000",
            secondary_color="#333333",
            background_color="#ffffff",
            text_color="#000000",
            font_family="Arial, sans-serif",
            border_radius="0px",
            dark_mode=False
        ),
        DesignStyle.GAMING: ChatTheme(
            primary_color="#10b981",
            secondary_color="#f59e0b",
            background_color="#111827",
            text_color="#f3f4f6",
            font_family="Orbitron, sans-serif",
            border_radius="4px",
            dark_mode=True
        ),
        DesignStyle.PROFESSIONAL: ChatTheme(
            primary_color="#1e40af",
            secondary_color="#3b82f6",
            background_color="#ffffff",
            text_color="#1e293b",
            font_family="Lato, sans-serif",
            border_radius="12px",
            dark_mode=False
        )
    }
    
    def __init__(self):
        """Initialize the design agent."""
        self.current_theme = self.THEMES[DesignStyle.MODERN]
        logger.info("Design agent initialized")
    
    async def process(
        self,
        request: str,
        entities: Optional[List[Dict]] = None
    ) -> Dict[str, Any]:
        """Process a design request."""
        try:
            # Extract style from request
            style = self._extract_style(request)
            
            # Generate theme
            theme = self._generate_theme(style, entities)
            
            # Generate CSS
            css_vars = self._generate_css(theme)
            
            return {
                "style": style.value,
                "theme": {
                    "primary_color": theme.primary_color,
                    "secondary_color": theme.secondary_color,
                    "background_color": theme.background_color,
                    "text_color": theme.text_color,
                    "font_family": theme.font_family,
                    "border_radius": theme.border_radius,
                    "dark_mode": theme.dark_mode
                },
                "css_variables": css_vars,
                "preview_url": None
            }
        except Exception as e:
            logger.error(f"Design processing error: {e}")
            return {"error": str(e)}
    
    def _extract_style(self, request: str) -> DesignStyle:
        """Extract desired style from request."""
        request_lower = request.lower()
        
        style_keywords = {
            DesignStyle.MODERN: ["modern", "contemporary", "new"],
            DesignStyle.CLASSIC: ["classic", "traditional", "standard"],
            DesignStyle.MINIMALIST: ["minimal", "simple", "clean", "minimalist"],
            DesignStyle.GAMING: ["gaming", "game", "gamer", "neon", "dark"],
            DesignStyle.PROFESSIONAL: ["professional", "business", "corporate"]
        }
        
        for style, keywords in style_keywords.items():
            for keyword in keywords:
                if keyword in request_lower:
                    return style
        
        return DesignStyle.MODERN  # Default
    
    def _generate_theme(
        self,
        style: DesignStyle,
        entities: Optional[List[Dict]] = None
    ) -> ChatTheme:
        """Generate a theme based on style and entities."""
        base_theme = self.THEMES[style]
        
        # Apply customizations from entities
        if entities:
            for entity in entities:
                if entity.get("type") == "color":
                    # Apply custom color
                    base_theme.primary_color = entity.get("value", base_theme.primary_color)
        
        return base_theme
    
    def _generate_css(self, theme: ChatTheme) -> Dict[str, str]:
        """Generate CSS variables from theme."""
        return {
            "--primary-color": theme.primary_color,
            "--secondary-color": theme.secondary_color,
            "--background-color": theme.background_color,
            "--text-color": theme.text_color,
            "--font-family": theme.font_family,
            "--border-radius": theme.border_radius,
            "--dark-mode": str(theme.dark_mode).lower()
        }
    
    def get_presets(self) -> List[Dict[str, Any]]:
        """Get available design presets."""
        return [
            {
                "id": style.value,
                "name": style.value.title(),
                "description": self._get_style_description(style),
                "preview_colors": [
                    theme.primary_color,
                    theme.secondary_color,
                    theme.background_color
                ]
            }
            for style, theme in self.THEMES.items()
        ]
    
    def _get_style_description(self, style: DesignStyle) -> str:
        """Get description for a style."""
        descriptions = {
            DesignStyle.MODERN: "Clean and contemporary design with rounded corners",
            DesignStyle.CLASSIC: "Traditional chat bubble design",
            DesignStyle.MINIMALIST: "Simple and focused with no distractions",
            DesignStyle.GAMING: "Dark mode with neon accents for gamers",
            DesignStyle.PROFESSIONAL: "Business-appropriate design for work"
        }
        return descriptions.get(style, "Custom design")
    
    def apply_theme(self, theme: ChatTheme) -> None:
        """Apply a theme to the chat."""
        self.current_theme = theme
        logger.info(f"Applied theme: {theme.primary_color}")


# Export agent instance
design_agent = DesignAgent()
