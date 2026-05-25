"""
Foreign Trade MCP Engine

Role:
Central execution engine for foreign trade business actions.

Responsibilities:
- Parse and route actions to correct domain handlers
- Normalize Chinese field names to English before dispatching
- Provide unified error handling and result wrapping

Architecture Position:
  MCP Tool → Engine.execute() → ActionHandler → Repository → DB

Strict Rules:
- Engine does NO business logic
- Engine does NO constraint checking (delegated to actions)
- Engine does NO state validation (delegated to actions)

AI Extension Guidance:
- Add new domains via register()
- Add field normalization mappings in _normalize_fields()
"""

from typing import Any, Dict, Optional
from runtime.action_registry import ActionRegistry


# Chinese → English field name normalization map
_FIELD_NORMALIZE = {
    # Customer / Lead
    "公司名称": "company_name",
    "联系人": "contact_name",
    "电话": "phone",
    "手机": "mobile",
    "邮箱": "email",
    "邮件": "email",
    "国家": "country",
    "来源渠道": "source_channel",
    "业务类型": "business_type",
    "官网": "website",
    "备注": "notes",
    "发信时间": "send_time_window",
    "联系状态": "contact_status",
    "下次跟进日期": "next_follow_up_date",
    "跟进记录": "follow_up_records",
    "创建时间": "created_at",
    "更新时间": "updated_at",
    # Email
    "第1次发送时间": "first_sent_time",
    "第1次主题": "first_subject",
    "第1次状态": "first_status",
    "发件邮箱": "from_email",
    "来源": "source",
    "状态": "status",
    "客户ID": "customer_id",
    # Aliases
    "邮箱": "to_email",  # Excel 邮箱 column = recipient address
    "邮件": "to_email",
}


class Engine:
    """Main engine for executing foreign trade actions."""

    def __init__(self):
        self.registry = ActionRegistry()
        self._register_actions()

    def _register_actions(self):
        """Register all available actions."""
        from runtime.lead_actions import LeadActions
        from runtime.customer_actions import CustomerActions
        from runtime.email_actions import EmailActions

        self.registry.register("lead", LeadActions())
        self.registry.register("customer", CustomerActions())
        self.registry.register("email", EmailActions())

    def _normalize_fields(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize Chinese field names to English."""
        if not params:
            return params
        normalized = {}
        for k, v in params.items():
            if k in _FIELD_NORMALIZE:
                normalized[_FIELD_NORMALIZE[k]] = v
            else:
                normalized[k] = v
        return normalized

    def execute(self, action: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute an action by name (domain.action format) or by action name only.

        Args:
            action: Either 'domain.action' string, or just 'action_name'.
            params: Optional parameters for the action.

        Returns:
            {"success": True, "result": {...}} or {"success": False, "error": "..."}
        """
        try:
            # Normalize field names before dispatch
            params = self._normalize_fields(params or {})

            domain, action_name = self._parse_action(action)
            handler = self.registry.get_handler(domain, action_name)
            if handler is None:
                return {
                    "success": False,
                    "error": f"Unknown action: {domain}.{action_name}"
                }

            result = handler(params)
            return {
                "success": True,
                "result": result
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _parse_action(self, action: str):
        """Parse 'domain.action' or 'action' into (domain, action)."""
        if '.' in action:
            parts = action.split('.', 1)
            return parts[0], parts[1]
        for domain, actions in self.registry.list_all().items():
            if action in actions:
                return domain, action
        return 'unknown', action

    def list_actions(self) -> Dict[str, list]:
        """List all registered actions."""
        return self.registry.list_all()
