odoo.define("odoo_screen_capture_sale_order.screen_capture_sale_order", function (require) {
    "use strict";

    var publicWidget = require('web.public.widget')

    publicWidget.registry.screenCaptureSaleOrder = publicWidget.Widget.extend({
        selector: '#wrapwrap',
        read_events: {
            'click .o_download_btn': '_fetch_pdf',
        },

        _fetch_pdf: function () {
            const title_element = document.querySelector('.my-0')

            let elems = document.querySelectorAll("#portal_sale_content > div > .card-body > div[data-oe-model='sale.order']") // when there is a user logged in
            if (elems.length === 0) {
                elems = document.querySelectorAll("#portal_sale_content > div > .card-body > .oe_no_empty") // when there is no user logged in
            }

            Array.from(elems).forEach( function (el) {
                const section_div = el.querySelectorAll("section > div.container")

                Array.from(section_div).forEach( function (section_div_el) {
                    section_div_el.classList.remove('container')
                    
                })
            });

            const element = document.querySelector('#portal_sale_content')
            

            let title = ""
            let formatted_title = title_element.textContent.trim().split('\n')
            let i = 0

            for (i in formatted_title) {
                if (i > 0) {
                    title += " "
                }
                title += formatted_title[i].trim()
            }

            const opt = {
                margin: [5, 5, 10, 5], //top, left, buttom, right
                filename: title,
                image: { type: 'jpeg', quality: 0.98 },
                html2canvas: { scale: 1},
                jsPDF: { unit: 'mm', format: ['210', '297'], orientation: 'portrait' },
            };

            html2pdf().set(opt).from(element).toContainer().toCanvas().toImg().toPdf().save()
        }
    })
})
