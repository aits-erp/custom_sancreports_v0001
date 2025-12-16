import frappe


def execute(filters=None):
    columns = get_columns()
    data = get_data()
    return columns, data


def get_columns():
    return [
        {
            "label": "Purchase Receipt No",
            "fieldname": "purchase_receipt",
            "fieldtype": "Link",
            "options": "Purchase Receipt",
            "width": 180,
        },
        {
            "label": "Posting Date",
            "fieldname": "posting_date",
            "fieldtype": "Date",
            "width": 120,
        },
        {
            "label": "Supplier Name",
            "fieldname": "supplier_name",
            "fieldtype": "Data",
            "width": 220,
        },
        {
            "label": "GRN Rate (USD)",
            "fieldname": "grn_rate_usd",
            "fieldtype": "Float",
            "width": 150,
        },
        {
            "label": "GRN Total (INR)",
            "fieldname": "grn_total_inr",
            "fieldtype": "Currency",
            "width": 180,
        },
        {
            "label": "LCV",
            "fieldname": "lcv",
            "fieldtype": "Currency",
            "width": 160,
        },
        {
            "label": "Total Landed Cost (INR)",
            "fieldname": "total_landed_cost",
            "fieldtype": "Currency",
            "width": 200,
        },
    ]


def get_data():
    query = """
        SELECT
            pr.name AS purchase_receipt,
            pr.posting_date,
            pr.supplier_name,

            ROUND(
                SUM(pri.rate * pri.qty) / NULLIF(SUM(pri.qty), 0),
                2
            ) AS grn_rate_usd,

            pr.base_grand_total AS grn_total_inr,

            -- LCV from applicable_charges
            COALESCE(SUM(pri.applicable_charges), 0) AS lcv,

            -- Total Landed Cost = GRN Total + LCV
            pr.base_grand_total + COALESCE(SUM(pri.applicable_charges), 0)
                AS total_landed_cost

        FROM
            `tabPurchase Receipt` pr

        INNER JOIN
            `tabPurchase Receipt Item` pri
            ON pri.parent = pr.name

        WHERE
            pr.docstatus = 1

        GROUP BY
            pr.name,
            pr.posting_date,
            pr.supplier_name,
            pr.base_grand_total

        ORDER BY
            pr.posting_date DESC
    """

    return frappe.db.sql(query, as_dict=True)
