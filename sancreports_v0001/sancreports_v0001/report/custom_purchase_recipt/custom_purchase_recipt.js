frappe.query_reports["Custom Purchase recipt"] = {
    filters: [
        { fieldname: "from_date", label: "From Date", fieldtype: "Date" },
        { fieldname: "to_date", label: "To Date", fieldtype: "Date" },
        {
            fieldname: "supplier",
            label: "Supplier",
            fieldtype: "Link",
            options: "Supplier",
        },
    ],

    formatter(value, row, column, data, default_formatter) {
        value = default_formatter(value, row, column, data);

        // 🔹 GRN Drill-down
        if (column.fieldname === "grn_total" && data) {
            return `
                <a href="javascript:void(0)"
                   class="grn-drill"
                   data-pr="${data.purchase_receipt}">
                   ${value}
                </a>`;
        }

        // 🔹 LCV Drill-down
        if (column.fieldname === "lcv" && data && data.lcv > 0) {
            return `
                <a href="javascript:void(0)"
                   class="lcv-drill"
                   data-pr="${data.purchase_receipt}">
                   ${value}
                </a>`;
        }

        // Highlight total
        if (column.fieldname === "total_landed_cost") {
            return `<b>${value}</b>`;
        }

        return value;
    },

    onload() {

        // 🔹 GRN click
        $(document).on("click", ".grn-drill", function () {
            let pr = $(this).data("pr");

            frappe.call({
                method:
                    "sancreports_v0001.sancreports_v0001.report.custom_purchase_recipt.custom_purchase_recipt.get_item_wise_grn",
                args: { purchase_receipt: pr },
                callback(r) {
                    if (!r.message || !r.message.length) {
                        frappe.msgprint("No items found.");
                        return;
                    }

                    let rows = r.message.map(d => `
                        <tr>
                            <td>${d.item_code}</td>
                            <td>${d.item_name || ""}</td>
                            <td style="text-align:right">${d.qty}</td>
                            <td style="text-align:right">${d.rate}</td>
                            <td style="text-align:right">${d.amount}</td>
                        </tr>`).join("");

                    frappe.msgprint({
                        title: `Item-wise GRN (${pr})`,
                        message: `
                            <table class="table table-bordered">
                                <thead>
                                    <tr>
                                        <th>Item</th>
                                        <th>Name</th>
                                        <th>Qty</th>
                                        <th>Rate</th>
                                        <th>Amount</th>
                                    </tr>
                                </thead>
                                <tbody>${rows}</tbody>
                            </table>
                        `,
                        wide: true,
                    });
                },
            });
        });

        // 🔹 LCV click
        $(document).on("click", ".lcv-drill", function () {
            let pr = $(this).data("pr");

            frappe.call({
                method:
                    "sancreports_v0001.sancreports_v0001.report.custom_purchase_recipt.custom_purchase_recipt.get_item_wise_lcv",
                args: { purchase_receipt: pr },
                callback(r) {
                    if (!r.message || !r.message.length) {
                        frappe.msgprint("No LCV found.");
                        return;
                    }

                    let rows = r.message.map(d => `
                        <tr>
                            <td>${d.item_code}</td>
                            <td>${d.item_name || ""}</td>
                            <td style="text-align:right">${d.qty}</td>
                            <td style="text-align:right">${d.applicable_charges}</td>
                        </tr>`).join("");

                    frappe.msgprint({
                        title: `Item-wise LCV (${pr})`,
                        message: `
                            <table class="table table-bordered">
                                <thead>
                                    <tr>
                                        <th>Item</th>
                                        <th>Name</th>
                                        <th>Qty</th>
                                        <th>Applicable Charges</th>
                                    </tr>
                                </thead>
                                <tbody>${rows}</tbody>
                            </table>
                        `,
                        wide: true,
                    });
                },
            });
        });
    },
};
