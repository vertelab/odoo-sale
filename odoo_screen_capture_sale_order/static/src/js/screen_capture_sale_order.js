odoo.define("odoo_screen_capture_sale_order.screen_capture_sale_order", function (require) {
    "use strict";

    var publicWidget = require('web.public.widget')

    publicWidget.registry.screenCaptureSaleOrder = publicWidget.Widget.extend({
        selector: '#wrapwrap',
        read_events: {
            'click .o_download_btn': '_fetch_pdf',
        },

        _fetch_pdf: function () {
            const element = document.querySelector('#portal_sale_content')
            const title_element = document.querySelector('.my-0')

            let title = ""
            let formatted_title = title_element.textContent.trim().split('\n')
            let i = 0

            for (i in formatted_title) {
                if (i > 0) {
                    title += " "
                }
                title += formatted_title[i].trim()
            }

            let width = element.offsetWidth * 1.65;
            let height = element.offsetHeight * 1.25;
            let opt = {
                margin: 25,
                filename: title,
                image: { type: 'jpeg', quality: 0.98 },
                html2canvas: { scale: 1 },
                jsPDF: { unit: 'px', format: [width, height], orientation: 'portrait' }
            };

            html2pdf().set(opt).from(element).toContainer().toCanvas().toImg().toPdf().save()
        }
    })
})