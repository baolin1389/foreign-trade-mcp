"""
Foreign Trade MCP — CLI Entry Point
===================================
Usage:
    python main.py list_leads
    python main.py create_lead --company "ACME GmbH" --name "John" --email "john@acme.de" --country Germany
    python main.py qualify_lead --id lead_xxx --score 75
    python main.py convert_lead --id lead_xxx
    python main.py list_customers
    python main.py create_customer --company "ACME GmbH" --country Germany
    python main.py list_email_records
    python main.py send_email --customer cust_xxx --to test@example.com --from eric@seporange.com.cn --subject "Hello"
"""

import argparse
import sys
import os
from pathlib import Path

# Add project root
sys.path.insert(0, str(Path(__file__).parent))

from infrastructure.database import init_db
from runtime.engine import Engine


def main():
    parser = argparse.ArgumentParser(description="Foreign Trade MCP CLI")
    sub = parser.add_subparsers(dest="command", help="Available commands")

    # list_leads
    p = sub.add_parser("list_leads", help="List leads")
    p.add_argument("--page", type=int, default=1)
    p.add_argument("--page_size", type=int, default=20)
    p.add_argument("--status", help="Filter by status")
    p.add_argument("--country", help="Filter by country")

    # create_lead
    p = sub.add_parser("create_lead", help="Create a lead")
    p.add_argument("--company", required=True, help="Company name")
    p.add_argument("--name", required=True, help="Contact name")
    p.add_argument("--email", required=True, help="Contact email")
    p.add_argument("--country", required=True, help="Country")
    p.add_argument("--phone", help="Phone number")
    p.add_argument("--source", help="Lead source")

    # get_lead
    p = sub.add_parser("get_lead", help="Get a lead")
    p.add_argument("--id", required=True, help="Lead ID")

    # update_lead
    p = sub.add_parser("update_lead", help="Update a lead")
    p.add_argument("--id", required=True, help="Lead ID")
    p.add_argument("--status", help="New status")
    p.add_argument("--notes", help="Notes")

    # qualify_lead
    p = sub.add_parser("qualify_lead", help="Qualify a lead")
    p.add_argument("--id", required=True, help="Lead ID")
    p.add_argument("--score", type=int, required=True, help="Qualification score (>=60)")
    p.add_argument("--notes", help="Notes")

    # reject_lead
    p = sub.add_parser("reject_lead", help="Reject a lead")
    p.add_argument("--id", required=True, help="Lead ID")
    p.add_argument("--reason", help="Rejection reason")

    # convert_lead
    p = sub.add_parser("convert_lead", help="Convert lead to customer")
    p.add_argument("--id", required=True, help="Lead ID")

    # list_customers
    p = sub.add_parser("list_customers", help="List customers")
    p.add_argument("--page", type=int, default=1)
    p.add_argument("--page_size", type=int, default=20)
    p.add_argument("--status", help="Filter by contact_status")
    p.add_argument("--country", help="Filter by country")

    # create_customer
    p = sub.add_parser("create_customer", help="Create a customer")
    p.add_argument("--company", required=True, help="Company name")
    p.add_argument("--country", required=True, help="Country")
    p.add_argument("--name", help="Contact name")
    p.add_argument("--email", help="Contact email")
    p.add_argument("--phone", help="Phone")
    p.add_argument("--type", dest="business_type", help="Business type")
    p.add_argument("--source", dest="source_channel", help="Source channel")
    p.add_argument("--notes", help="Notes")

    # get_customer
    p = sub.add_parser("get_customer", help="Get a customer")
    p.add_argument("--id", required=True, help="Customer ID")

    # update_customer
    p = sub.add_parser("update_customer", help="Update a customer")
    p.add_argument("--id", required=True, help="Customer ID")
    p.add_argument("--status", help="New contact_status")
    p.add_argument("--notes", help="Notes")

    # list_email_records
    p = sub.add_parser("list_email_records", help="List email records")
    p.add_argument("--page", type=int, default=1)
    p.add_argument("--page_size", type=int, default=20)
    p.add_argument("--customer", help="Filter by customer_id")
    p.add_argument("--status", help="Filter by status")

    # send_email
    p = sub.add_parser("send_email", help="Send email")
    p.add_argument("--customer", required=True, help="Customer ID")
    p.add_argument("--to", required=True, help="Recipient email")
    p.add_argument("--from", dest="from_email", required=True, help="Sender email")
    p.add_argument("--subject", required=True, help="Email subject")
    p.add_argument("--body", help="Email body")

    # list_actions
    sub.add_parser("list_actions", help="List all available actions")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    os.chdir(Path(__file__).parent)
    init_db()
    engine = Engine()

    # Route command
    if args.command == "list_leads":
        params = {"page": args.page, "page_size": args.page_size}
        if args.status:
            params["status"] = args.status
        if args.country:
            params["country"] = args.country
        result = engine.execute("lead.list_leads", params)

    elif args.command == "create_lead":
        params = {
            "company_name": args.company,
            "contact_name": args.name,
            "contact_email": args.email,
            "country": args.country,
        }
        if args.phone:
            params["contact_phone"] = args.phone
        if args.source:
            params["source"] = args.source
        result = engine.execute("lead.create_lead", params)

    elif args.command == "get_lead":
        result = engine.execute("lead.get_lead", {"lead_id": args.id})

    elif args.command == "update_lead":
        params = {"lead_id": args.id}
        if args.status:
            params["status"] = args.status
        if args.notes:
            params["qualification_notes"] = args.notes
        result = engine.execute("lead.update_lead", params)

    elif args.command == "qualify_lead":
        params = {"lead_id": args.id, "qualification_score": args.score}
        if args.notes:
            params["qualification_notes"] = args.notes
        result = engine.execute("lead.qualify_lead", params)

    elif args.command == "reject_lead":
        params = {"lead_id": args.id}
        if args.reason:
            params["qualification_notes"] = args.reason
        result = engine.execute("lead.reject_lead", params)

    elif args.command == "convert_lead":
        result = engine.execute("lead.convert_lead", {"lead_id": args.id})

    elif args.command == "list_customers":
        params = {"page": args.page, "page_size": args.page_size}
        if args.status:
            params["contact_status"] = args.status
        if args.country:
            params["country"] = args.country
        result = engine.execute("customer.list_customers", params)

    elif args.command == "create_customer":
        params = {"company_name": args.company, "country": args.country}
        if args.name:
            params["contact_name"] = args.name
        if args.email:
            params["contact_email"] = args.email
        if args.phone:
            params["contact_phone"] = args.phone
        if args.business_type:
            params["business_type"] = args.business_type
        if args.source_channel:
            params["source_channel"] = args.source_channel
        if args.notes:
            params["notes"] = args.notes
        result = engine.execute("customer.create_customer", params)

    elif args.command == "get_customer":
        result = engine.execute("customer.get_customer", {"customer_id": args.id})

    elif args.command == "update_customer":
        params = {"customer_id": args.id}
        if args.status:
            params["contact_status"] = args.status
        if args.notes:
            params["notes"] = args.notes
        result = engine.execute("customer.update_customer", params)

    elif args.command == "list_email_records":
        params = {"page": args.page, "page_size": args.page_size}
        if args.customer:
            params["customer_id"] = args.customer
        if args.status:
            params["status"] = args.status
        result = engine.execute("email.list_email_records", params)

    elif args.command == "send_email":
        params = {
            "customer_id": args.customer,
            "to_email": args.to,
            "from_email": args.from_email,
            "subject": args.subject,
        }
        if args.body:
            params["body"] = args.body
        result = engine.execute("email.send_email", params)

    elif args.command == "list_actions":
        import json
        print(json.dumps(engine.list_actions(), indent=2, ensure_ascii=False))
        return

    else:
        result = {"success": False, "error": f"Unknown command: {args.command}"}

    # Output
    if result.get("success"):
        import json
        print(json.dumps(result.get("result"), indent=2, ensure_ascii=False))
    else:
        print(f"ERROR: {result.get('error')}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()