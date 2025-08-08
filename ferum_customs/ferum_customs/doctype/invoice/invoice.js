frappe.ui.form.on('Invoice', {
    refresh: function(frm) {
        if (frm.doc.status === 'New') {
            frm.add_custom_button(__('Set as Awaiting Payment'), function() {
                frm.call('set_as_awaiting_payment');
            }, __('Actions'));
        }
        if (frm.doc.status === 'Awaiting Payment') {
            frm.add_custom_button(__('Set as Paid'), function() {
                frm.call('set_as_paid');
            }, __('Actions'));
        }
    }
});
