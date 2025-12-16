import frappe


def execute(filters=None):
    return get_columns(), get_data(filters)


def get_columns():
    return [
        {
            "label": "Purchase Receipt",
            "fieldname": "purchase_receipt",
            "fieldtype": "Link",
            "options": "Purchase Receipt",
            "width": 170,
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
            "label": "GRN Total (INR)",
            "fieldname": "grn_total",
            "fieldtype": "Currency",
            "width": 160,
        },
        {
            "label": "LCV",
            "fieldname": "lcv",
            "fieldtype": "Currency",
            "width": 140,
        },
        {
            "label": "Total Landed Cost",
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
        values["from_date"] = filters.get("from_date")

    if filters.get("to_date"):
        conditions += " AND pr.posting_date <= %(to_date)s"
        values["to_date"] = filters.get("to_date")

    if filters.get("supplier"):
        conditions += " AND pr.supplier = %(supplier)s"
        values["supplier"] = filters.get("supplier")

    query = f"""
        SELECT
            pr.name AS purchase_receipt,
            pr.posting_date,
            pr.supplier_name AS supplier,

            pr.base_grand_total AS grn_total,

            -- ✅ LCV from Landed Cost Item (CONFIRMED)
            COALESCE(SUM(lci.applicable_charges), 0) AS lcv,

            -- ✅ Total Landed Cost
            pr.base_grand_total + COALESCE(SUM(lci.applicable_charges), 0)
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
            pr.base_grand_total

        ORDER BY
            pr.posting_date DESC
    """

    return frappe.db.sql(query, values, as_dict=True)
