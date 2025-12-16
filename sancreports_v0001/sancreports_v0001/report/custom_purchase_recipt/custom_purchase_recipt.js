frappe.query_reports["Custom Purchase recipt"] = {
    filters: [
        {
            fieldname: "from_date",
            label: "From Date",
            fieldtype: "Date",
        },
        {
            fieldname: "to_date",
            label: "To Date",
            fieldtype: "Date",
        },
        {
            fieldname: "supplier",
            label: "Supplier",
            fieldtype: "Link",
            options: "Supplier",
        },
    ],

    formatter: function (value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);

        // USD formatting (no ₹ symbol)
        if (column.fieldname === "grn_rate_usd" && data) {
            return `<span style="color:#1f77b4;font-weight:600">$ ${data.grn_rate_usd || 0}</span>`;
        }

        return value;
    },
};
