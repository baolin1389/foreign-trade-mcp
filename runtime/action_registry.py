"""
Action Registry

Central registry for all MCP actions.
Maps domain.action to handler functions.
"""

from typing import Any, Callable, Dict, Optional


class ActionRegistry:
    """Registry for managing and routing actions."""

    def __init__(self):
        self._domains: Dict[str, Any] = {}
        self._actions: Dict[str, Dict[str, Callable]] = {}

    def register(self, domain: str, handler_class: Any) -> None:
        """
        Register a domain with its handler class.

        Args:
            domain: The domain name (e.g., 'lead', 'customer')
            handler_class: The handler class instance
        """
        self._domains[domain] = handler_class
        self._actions[domain] = {}

        # Auto-register methods from the handler class
        for attr_name in dir(handler_class):
            if not attr_name.startswith("_"):
                attr = getattr(handler_class, attr_name)
                if callable(attr):
                    self._actions[domain][attr_name] = attr

    def get_handler(self, domain: str, action: str) -> Optional[Callable]:
        """
        Get a handler for a specific domain and action.

        Args:
            domain: The domain name
            action: The action name

        Returns:
            The handler function or None if not found
        """
        if domain not in self._actions:
            return None
        return self._actions[domain].get(action)

    def list_all(self) -> Dict[str, list]:
        """List all registered domains and their actions."""
        return {
            domain: list(actions.keys())
            for domain, actions in self._actions.items()
        }

    def get_domains(self) -> list:
        """Get list of all registered domains."""
        return list(self._domains.keys())
