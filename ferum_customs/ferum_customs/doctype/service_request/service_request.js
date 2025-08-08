frappe.ui.form.on('ServiceRequest', {
    refresh: function(frm) {
        if (!frm.is_new()) {
            frm.add_custom_button(__('Create Service Report'), function() {
                frappe.new_doc('ServiceReport', {
                    service_request: frm.doc.name
                });
            }, __('Create'));
        }
    },
    service_object: function(frm) {
        if (frm.doc.service_object) {
            frappe.call({
                method: 'frappe.client.get',
                args: {
                    doctype: 'ServiceObject',
                    name: frm.doc.service_object
                },
                callback: function(r) {
                    if (r.message) {
                        frm.set_value('customer', r.message.customer);
                    }
                }
            });
        }
    }
});