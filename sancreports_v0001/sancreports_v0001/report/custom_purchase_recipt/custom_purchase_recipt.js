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

        // 🔹 GRN USD → Item-wise GRN drill-down
        if (column.fieldname === "grn_total_usd" && data) {
            return `
                <a href="javascript:void(0)"
                   class="grn-drilldown"
                   data-pr="${data.purchase_receipt}">
                   ${value}
                </a>
            `;
        }

        // 🔹 LCV → Item-wise LCV drill-down
        if (column.fieldname === "lcv" && data && data.lcv > 0) {
            return `
                <a href="javascript:void(0)"
                   class="lcv-drilldown"
                   data-pr="${data.purchase_receipt}">
                   ${value}
                </a>
            `;
        }

        // Highlight total landed cost
        if (column.fieldname === "total_landed_cost") {
            return `<b>${value}</b>`;
        }

        return value;
    },

    onload: function () {

        // 🔹 GRN ITEM POPUP
        $(document).on("click", ".grn-drilldown", function () {
            let pr = $(this).data("pr");

            frappe.call({
                method: "sancreports_v0001.sancreports_v0001.report.custom_purchase_recipt.custom_purchase_recipt.get_item_wise_grn",
                args: { purchase_receipt: pr },
                callback: function (r) {
                    let rows = r.message.map(d => `
                        <tr>
                            <td>${d.item_code}</td>
                            <td>${d.item_name || ""}</td>
                            <td align="right">${d.qty}</td>
                            <td align="right">${d.rate}</td>
                            <td align="right">${d.amount}</td>
                        </tr>
                    `).join("");

                    frappe.msgprint({
                        title: `Item-wise GRN (${pr})`,
                        message: `
                            <table class="table table-bordered">
                                <thead>
                                    <tr>
                                        <th>Item Code</th>
                                        <th>Item Name</th>
                                        <th>Qty</th>
                                        <th>Rate (USD)</th>
                                        <th>Amount (USD)</th>
                                    </tr>
                                </thead>
                                <tbody>${rows}</tbody>
                            </table>
                        `,
                        wide: true
                    });
                }
            });
        });

        // 🔹 LCV ITEM POPUP
        $(document).on("click", ".lcv-drilldown", function () {
            let pr = $(this).data("pr");

            frappe.call({
                method: "sancreports_v0001.sancreports_v0001.report.custom_purchase_recipt.custom_purchase_recipt.get_item_wise_lcv",
                args: { purchase_receipt: pr },
                callback: function (r) {
                    let rows = r.message.map(d => `
                        <tr>
                            <td>${d.item_code}</td>
                            <td>${d.item_name || ""}</td>
                            <td align="right">${d.qty}</td>
                            <td align="right">${d.applicable_charges}</td>
                        </tr>
                    `).join("");

                    frappe.msgprint({
                        title: `Item-wise LCV (${pr})`,
                        message: `
                            <table class="table table-bordered">
                                <thead>
                                    <tr>
                                        <th>Item Code</th>
                                        <th>Item Name</th>
                                        <th>Qty</th>
                                        <th>Applicable Charges</th>
                                    </tr>
                                </thead>
                                <tbody>${rows}</tbody>
                            </table>
                        `,
                        wide: true
                    });
                }
            });
        });
    }
};
