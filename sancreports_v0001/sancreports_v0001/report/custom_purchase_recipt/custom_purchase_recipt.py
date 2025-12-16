import frappe


def execute(filters=None):
    return get_columns(), get_data(filters or {})


def get_columns():
    return [
        {
            "label": "Purchase Receipt",
            "fieldname": "purchase_receipt",
            "fieldtype": "Link",
            "options": "Purchase Receipt",
            "width": 160,
        },
        {
            "label": "Posting Date",
            "fieldname": "posting_date",
            "fieldtype": "Date",
            "width": 120,
        },
        {
            "label": "Supplier",
            "fieldname": "supplier",
            "fieldtype": "Data",
            "width": 220,
        },
        {
            "label": "GRN Total (USD)",
            "fieldname": "grn_total_usd",
            "fieldtype": "Currency",
            "width": 150,
        },
        {
            "label": "GRN Total (INR)",
            "fieldname": "grn_total_inr",
            "fieldtype": "Currency",
            "width": 150,
        },
        {
            "label": "LCV",
            "fieldname": "lcv",
            "fieldtype": "Currency",
            "width": 120,
        },
        {
            "label": "Total Landed Cost (INR)",
            "fieldname": "total_landed_cost",
            "fieldtype": "Currency",
            "width": 180,
        },
    ]


def get_data(filters):
    conditions = ""
    values = {}

    if filters.get("from_date"):
        conditions += " AND pr.posting_date >= %(from_date)s"
        values["from_date"] = filters["from_date"]

    if filters.get("to_date"):
        conditions += " AND pr.posting_date <= %(to_date)s"
        values["to_date"] = filters["to_date"]

    if filters.get("supplier"):
        conditions += " AND pr.supplier = %(supplier)s"
        values["supplier"] = filters["supplier"]

    query = f"""
        SELECT
            pr.name AS purchase_receipt,
            pr.posting_date,
            pr.supplier_name AS supplier,

            pr.grand_total AS grn_total_usd,
            pr.base_grand_total AS grn_total_inr,

            COALESCE(SUM(lci.applicable_charges), 0) AS lcv,

            pr.base_grand_total
            + COALESCE(SUM(lci.applicable_charges), 0)
                AS total_landed_cost

        FROM
            `tabPurchase Receipt` pr

        LEFT JOIN
            `tabLanded Cost Item` lci
            ON lci.receipt_document = pr.name
            AND lci.docstatus = 1

        WHERE
            pr.docstatus = 1
            {conditions}

        GROUP BY
            pr.name,
            pr.posting_date,
            pr.supplier_name,
            pr.grand_total,
            pr.base_grand_total

        ORDER BY
            pr.posting_date DESC
    """

    return frappe.db.sql(query, values, as_dict=True)


# 🔹 DRILL-DOWN 1: ITEM-WISE GRN (USD)
@frappe.whitelist()
def get_item_wise_grn(purchase_receipt):
    return frappe.db.sql("""
        SELECT
            item_code,
            item_name,
            qty,
            rate,
            amount
        FROM
            `tabPurchase Receipt Item`
        WHERE
            parent = %s
            AND docstatus = 1
        ORDER BY
            idx
    """, purchase_receipt, as_dict=True)


# 🔹 DRILL-DOWN 2: ITEM-WISE LCV
@frappe.whitelist()
def get_item_wise_lcv(purchase_receipt):
    return frappe.db.sql("""
        SELECT
            item_code,
            item_name,
            qty,
            applicable_charges
        FROM
            `tabLanded Cost Item`
        WHERE
            receipt_document = %s
            AND docstatus = 1
        ORDER BY
            item_code
    """, purchase_receipt, as_dict=True)
