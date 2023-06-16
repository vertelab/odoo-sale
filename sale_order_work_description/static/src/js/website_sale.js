odoo.define('sale_order_webshop_description.website_sale', function (require) {
    'use strict';

    var ajax = require('web.ajax');
    var core = require('web.core');
    var publicWidget = require('web.public.widget');
    require('website_sale.website_sale');
    const wUtils = require('website.utils');

    var _t = core._t;

    publicWidget.registry.WebsiteSale.include({

        _handleAdd: function ($form) {
            var self = this;
            this.$form = $form;

            var productSelector = [
                'input[type="hidden"][name="product_id"]',
                'input[type="radio"][name="product_id"]:checked'
            ];

            var productReady = this.selectOrCreateProduct(
                $form,
                parseInt($form.find(productSelector.join(', ')).first().val(), 10),
                $form.find('.product_template_id').val(),
                false
            );

            return productReady.then(function (productId) {
                $form.find(productSelector.join(', ')).val(productId);

                self.rootProduct = {
                    product_id: productId,
                    quantity: parseFloat($form.find('input[name="add_qty"]').val() || 1),
                    product_custom_attribute_values: self.getCustomVariantValues($form.find('.js_product')),
                    variant_values: self.getSelectedVariantValues($form.find('.js_product')),
                    no_variant_attribute_values: self.getNoVariantAttributeValues($form.find('.js_product')),
                    work_description: $form.find('textarea[name="work_description"]').val()
                };

                return self._onProductReady();
            });
        },

        _submitForm: function () {
            let params = this.rootProduct;
            params.add_qty = params.quantity;

            params.product_custom_attribute_values = JSON.stringify(params.product_custom_attribute_values);
            params.no_variant_attribute_values = JSON.stringify(params.no_variant_attribute_values);

            if (this.isBuyNow) {
                params.express = true;
            }

            if( params.work_description.trim().length === 0 ) {
                return alert("Enter Work Description")
            }

            return wUtils.sendRequest('/shop/cart/update', params);
        },

    })


})
