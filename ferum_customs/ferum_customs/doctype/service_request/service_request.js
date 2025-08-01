// ferum_customs/ferum_customs/doctype/service_request/service_request.js
/**
 * Client script for DocType "Service Request".
 * Contains common logic for filtering engineers and specific form actions.
 */

/// <reference path="../../../typings/frappe.d.ts" />

frappe.ui.form.on("Service Request", {
	/**
	 * Handler for the change event of 'service_object_link'.
	 * Requests engineers and sets filter for 'assigned_engineer'.
	 */
	service_object_link(frm) {
		const engineer_field = "assigned_engineer";

		if (!frm.doc.service_object_link) {
			frm.set_value(engineer_field, null);
			frm.set_query(engineer_field, null);
			frm.refresh_field(engineer_field);
			return;
		}

		frm.dashboard.set_indicator(__("Loading engineers..."), "blue");

		frappe.call({
			method: "ferum_customs.custom_logic.service_request_hooks.get_engineers_for_object",
			args: { service_object_name: frm.doc.service_object_link },
			callback(r) {
				frm.dashboard.clear_indicator();
				if (r.message && Array.isArray(r.message)) {
					if (r.message.length > 0) {
						frm.set_query(engineer_field, function () {
							return { filters: [["User", "name", "in", r.message]] };
						});

						if (
							frm.doc[engineer_field] &&
							!r.message.includes(frm.doc[engineer_field])
						) {
							frm.set_value(engineer_field, null);
						} else if (r.message.length === 1 && !frm.doc[engineer_field]) {
							frm.set_value(engineer_field, r.message[0]);
						}
					} else {
						frm.set_query(engineer_field, function () {
							return {
								filters: [
									["User", "name", "in", ["NON_EXISTENT_USER_SO_LIST_IS_EMPTY"]],
								],
							};
						});
						frm.set_value(engineer_field, null);
						frappe.show_alert(
							{
								message: __("No engineers found for this service object."),
								indicator: "info",
							},
							5
						);
					}
				} else {
					frm.set_query(engineer_field, function () {
						return { filters: [["User", "name", "in", []]] };
					});
					frm.set_value(engineer_field, null);
					frappe.show_alert(
						{
							message: __("Failed to retrieve a valid list of engineers from the server."),
							indicator: "warning",
						},
						7
					);
				}
				frm.refresh_field(engineer_field);
			},
			error(r) {
				frm.dashboard.clear_indicator();
				console.error("Error retrieving engineer list:", r);
				frm.set_query(engineer_field, null);
				frm.set_value(engineer_field, null);
				frm.refresh_field(engineer_field);
				frappe.show_alert(
					{
						message: __("An error occurred while retrieving the engineer list from the server."),
						indicator: "error",
					},
					7
				);
			},
		});
	},

	refresh(frm) {
		// Common logic: setting add_fetch and engineer filters
		frm.add_fetch("service_object_link", "linked_service_project", "project");

		if (frm.doc.service_object_link && !frm.is_new()) {
			const engineer_field = "assigned_engineer";
			if (frm.fields_dict[engineer_field] && !frm.fields_dict[engineer_field].get_query()) {
				frm.trigger("service_object_link");
			}
		}

		// Specific actions for service_request form
		if (frm.doc.docstatus === 0 && frm.doc.status === "Open") {
			frm.add_custom_button(
				__("Assign Engineer (SR Specific)"),
				() => {
					frappe.msgprint(
						__("Logic for assigning an engineer specific to the service_request form...")
					);
				},
				__("Actions")
			);
		}

		if (frm.doc.docstatus === 1 && frm.doc.status === "Completed") {
			frappe.db &&
				frm.add_custom_button(
					__("Create Service Report"),
					() => {
						frappe.new_doc("Service Report", {
							service_request: frm.doc.name,
							customer: frm.doc.custom_customer,
						});
					},
					__("Create")
				);
		}
	},

	validate(frm) {
		// Implement validation logic or remove if not needed
		return true;
	},
});
