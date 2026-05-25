"""Foreign Trade MCP - Main entry point.

This MCP provides tools for company/professional search and enrichment
via the Prospeo API integration.
"""

import sys
import argparse
from typing import Optional

from mcp.server.fastmcp import FastMCP


# Initialize FastMCP server
mcp = FastMCP("foreign-trade-mcp")

# Import tools to register them with the server
from mcp import tools as mcp_tools


@mcp.tool()
def search_company(name: str) -> dict:
    """Search for a company by name.

    Args:
        name: Company name to search for.

    Returns:
        Search results with company information.
    """
    return mcp_tools.search_company(name)


@mcp.tool()
def enrich_company(
    company_name: str,
    company_website: Optional[str] = None,
    company_linkedin_url: Optional[str] = None,
    company_id: Optional[str] = None
) -> dict:
    """Enrich company data with full profile.

    Args:
        company_name: Name of the company.
        company_website: Optional website domain.
        company_linkedin_url: Optional LinkedIn URL.
        company_id: Optional Prospeo company ID.

    Returns:
        Enriched company profile.
    """
    return mcp_tools.enrich_company(
        company_name=company_name,
        company_website=company_website
    )


@mcp.tool()
def search_person(
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    full_name: Optional[str] = None,
    company_name: Optional[str] = None,
    company_website: Optional[str] = None,
    person_job_title: Optional[str] = None
) -> dict:
    """Search for professionals matching criteria.

    Args:
        first_name: Person's first name.
        last_name: Person's last name.
        full_name: Full name as alternative.
        company_name: Current employer name.
        company_website: Company website domain.
        person_job_title: Job title to search for.

    Returns:
        Search results with person matches.
    """
    return mcp_tools.search_person(
        first_name=first_name,
        last_name=last_name,
        full_name=full_name,
        company_name=company_name,
        company_website=company_website,
        person_job_title=person_job_title
    )


@mcp.tool()
def enrich_person(
    full_name: Optional[str] = None,
    first_name: Optional[str] = None,
    last_name: Optional[str] = None,
    company_name: Optional[str] = None,
    company_website: Optional[str] = None,
    enrich_mobile: bool = False
) -> dict:
    """Enrich person with contact details.

    Args:
        full_name: Full name of person.
        first_name: First name.
        last_name: Last name.
        company_name: Current employer.
        company_website: Company website.
        enrich_mobile: Whether to lookup mobile (costs extra credits).

    Returns:
        Enriched person profile with contact info.
    """
    return mcp_tools.enrich_person(
        full_name=full_name,
        first_name=first_name,
        last_name=last_name,
        company_name=company_name,
        company_website=company_website,
        enrich_mobile=enrich_mobile
    )


@mcp.tool()
def get_account_info() -> dict:
    """Get account status and remaining credits.

    Returns:
        Account information including credits and plan details.
    """
    return mcp_tools.get_account_info()


def main():
    """Main entry point for the foreign trade MCP."""
    parser = argparse.ArgumentParser(
        description="Foreign Trade MCP Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                     Start the MCP server (stdio transport)
  python main.py --info             Show server information
  python main.py --transport sse    Use SSE transport
        """
    )
    parser.add_argument(
        "--info",
        action="store_true",
        help="Show server information and available tools"
    )
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse", "streamable-http"],
        default="stdio",
        help="Transport protocol to use (default: stdio)"
    )
    parser.add_argument(
        "--mount-path",
        default=None,
        help="Mount path for SSE/streamable-http transports"
    )

    args = parser.parse_args()

    if args.info:
        print("Foreign Trade MCP Server")
        print("=" * 40)
        print("Available tools:")
        print("  - search_company    Search for companies by name")
        print("  - enrich_company    Get detailed company profile")
        print("  - search_person     Search for professionals")
        print("  - enrich_person     Get person contact details")
        print("  - get_account_info  Check account credits and status")
        print()
        print(f"Transport: {args.transport}")
        return

    print(f"Starting Foreign Trade MCP Server (transport: {args.transport})...")
    mcp.run(transport=args.transport, mount_path=args.mount_path)


if __name__ == "__main__":
    main()
