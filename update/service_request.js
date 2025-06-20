// ferum_customs/ferum_customs/doctype/service_request/service_request.js
/**
 * Клиентский скрипт для DocType "Service Request".
 * Содержит общую логику фильтрации инженеров и специфичные действия формы.
 */

/// <reference path="../../../typings/frappe.d.ts" />

frappe.ui.form.on('Service Request', {

    /**
     * Обработчик изменения поля 'service_object_link'.
     * Запрашивает инженеров и устанавливает фильтр для 'assigned_engineer'.
     */
    service_object_link(frm) {
        const engineer_field = 'assigned_engineer';

        if (!frm.doc.service_object_link) {
            frm.set_value(engineer_field, null);
            frm.set_query(engineer_field, null);
            frm.refresh_field(engineer_field);
            return;
        }

        frm.dashboard.set_indicator(__('Загрузка инженеров...'), 'blue');

        frappe.call({
            method: 'ferum_customs.custom_logic.service_request_hooks.get_engineers_for_object',
            args: { service_object_name: frm.doc.service_object_link },
            callback(r) {
                frm.dashboard.clear_indicator();
                if (r.message && Array.isArray(r.message)) {
                    if (r.message.length > 0) {
                        frm.set_query(engineer_field, function() {
                            return { filters: [['User', 'name', 'in', r.message]] };
                        });

                        if (frm.doc[engineer_field] && !r.message.includes(frm.doc[engineer_field])) {
                            frm.set_value(engineer_field, null);
                        } else if (r.message.length === 1 && !frm.doc[engineer_field]) {
                            frm.set_value(engineer_field, r.message[0]);
                        }
                    } else {
                        frm.set_query(engineer_field, function() {
                            return { filters: [['User', 'name', 'in', ['NON_EXISTENT_USER_SO_LIST_IS_EMPTY']]] };
                        });
                        frm.set_value(engineer_field, null);
                        frappe.show_alert({ message: __('Инженеры для данного объекта обслуживания не найдены.'), indicator: 'info' }, 5);
                    }
                } else {
                    frm.set_query(engineer_field, function() { return { filters: [['User', 'name', 'in', []]] }; });
                    frm.set_value(engineer_field, null);
                    frappe.show_alert({ message: __('Не удалось получить корректный список инженеров от сервера.'), indicator: 'warning' }, 7);
                }
                frm.refresh_field(engineer_field);
            },
            error(r) {
                frm.dashboard.clear_indicator();
                console.error('Ошибка при получении списка инженеров:', r);
                frm.set_query(engineer_field, null);
                frm.set_value(engineer_field, null);
                frm.refresh_field(engineer_field);
                frappe.show_alert({ message: __('Произошла ошибка при получении списка инженеров с сервера.'), indicator: 'error' }, 7);
            }
        });
    },

    refresh(frm) {
        // Общая логика: установка add_fetch и фильтра инженеров
        frm.add_fetch('service_object_link', 'linked_service_project', 'project');

        if (frm.doc.service_object_link && !frm.is_new()) {
            const engineer_field = 'assigned_engineer';
            if (frm.fields_dict[engineer_field] && !frm.fields_dict[engineer_field].get_query()) {
                frm.trigger('service_object_link');
            }
        }

        // Специфичные действия формы service_request
        if (frm.doc.docstatus === 0 && frm.doc.status === 'Открыта') {
            frm.add_custom_button(__('Назначить инженера (SR Specific)'), () => {
                frappe.msgprint(__('Логика назначения инженера, специфичная для формы service_request...'));
            }, __('Действия'));
        }

        if (frm.doc.docstatus === 1 && frm.doc.status === 'Выполнена') {
            frappe.db && frm.add_custom_button(__('Создать Акт выполненных работ'), () => {
                frappe.new_doc('Service Report', {
                    service_request: frm.doc.name,
                    customer: frm.doc.custom_customer
                });
            }, __('Создать'));
        }
    },

    validate(frm) {
        // console.log("service_request DocType-specific JS: Client-side validation...");
        return true;
    }
});
