/// <reference path="../../../typings/frappe.d.ts" />

frappe.ui.form.on("Service Report", {
	refresh(frm) {
		if (frm.doc.docstatus === 1) {
			frm.add_custom_button(__("Создать счёт"), () => {
				frappe.call({
					method: "ferum_customs.api.create_invoice_from_report",
					args: { service_report: frm.doc.name },
					freeze: true,
					callback(r) {
						if (r.message) {
							frappe.set_route("Form", "Sales Invoice", r.message);
						} else {
							frappe.msgprint(__("Failed to create invoice. Please try again."));
						}
					},
					error: (error) => {
						frappe.msgprint(__("An error occurred while creating the invoice."));
						console.error(error);
					}
				});
			});
		}
	},
});
