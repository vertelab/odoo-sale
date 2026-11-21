# -*- coding: utf-8 -*-
"""Tester för sale_ai — kontext, resolver och OKF-kontrakt.

Körs med `checkmodule -d <testdb> -m sale_ai -l test`.
"""

from odoo.tests.common import TransactionCase


class TestSaleAIContext(TransactionCase):
    """Sessionens domänkontext."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({'name': 'Testkund AB'})
        cls.order = cls.env['sale.order'].create({
            'partner_id': cls.partner.id,
        })

    def _new_session(self):
        return self.env['ai.coworker.session'].create({
            'init_type': 'web_ui',
        })

    def test_capture_context_sets_order_and_partner(self):
        """_capture_context sätter order_id och härleder partner."""
        session = self._new_session()
        session._capture_context(order=self.order)
        self.assertEqual(session.order_id, self.order)
        self.assertEqual(session.partner_id, self.partner)

    def test_capture_context_keeps_existing_partner(self):
        """En satt partner skrivs inte över av en order med annan kund."""
        other = self.env['res.partner'].create({'name': 'Annan kund'})
        session = self._new_session()
        session.partner_id = other
        session._capture_context(order=self.order)
        self.assertEqual(session.order_id, self.order)
        self.assertEqual(session.partner_id, other,
                         'en satt partner ska behållas')

    def test_resolver_sets_partner_from_order(self):
        """sale_partner-resolvern härleder kund ur ordern."""
        from odoo.addons.sale_ai.models.ai_coworker_session import (
            _sale_partner_strategy)
        session = self._new_session()
        session.order_id = self.order
        session.partner_id = False
        _sale_partner_strategy(session)
        self.assertEqual(session.partner_id, self.partner)

    def test_resolver_does_not_guess(self):
        """Utan order sätts ingen partner."""
        from odoo.addons.sale_ai.models.ai_coworker_session import (
            _sale_partner_strategy)
        session = self._new_session()
        session.partner_id = False
        _sale_partner_strategy(session)
        self.assertFalse(session.partner_id)

    def test_auto_capture_from_so_number(self):
        """'SO<nummer>' i prompten fångas till order."""
        session = self._new_session()
        session._session_auto_capture('Titta på %s tack' % self.order.name)
        self.assertEqual(session.order_id, self.order)

    def test_auto_capture_does_not_overwrite(self):
        """Senast arbetad kontext vinner — en satt order skrivs inte över."""
        other = self.env['sale.order'].create({'partner_id': self.partner.id})
        session = self._new_session()
        session.order_id = other
        session._session_auto_capture('Titta på %s' % self.order.name)
        self.assertEqual(session.order_id, other)


class TestSaleOrderOKF(TransactionCase):
    """OKF-kontraktet på sale.order."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env['res.partner'].create({'name': 'OKF-kund AB'})
        cls.product = cls.env['product.product'].create({
            'name': 'Testtjänst',
            'type': 'service',
            'list_price': 1000.0,
        })
        cls.order = cls.env['sale.order'].create({
            'partner_id': cls.partner.id,
            'order_line': [(0, 0, {
                'product_id': cls.product.id,
                'product_uom_qty': 2,
                'price_unit': 1000.0,
            })],
        })

    def test_concept_key_is_stable(self):
        """Nyckeln är <modell>,<id> och ändras inte med innehållet."""
        key_before = self.order._okf_concept_key()
        self.assertEqual(key_before, 'sale.order,%s' % self.order.id)
        self.order.write({'client_order_ref': 'NY-REF'})
        self.assertEqual(self.order._okf_concept_key(), key_before)

    def test_artifact_type(self):
        """Bryggans egen artefakttyp."""
        self.assertEqual(self.order._okf_artifact_type(), 'sale_order')

    def test_owner_is_company(self):
        """Offerten ägs av bolaget."""
        vals = self.order._okf_owner_vals()
        self.assertEqual(vals.get('owner_company_id'),
                         self.env.company.id)

    def test_summary_names_customer_and_amount(self):
        """Sammanfattningen bär kund, status och belopp."""
        summary = self.order._okf_summary_source()
        self.assertIn('OKF-kund AB', summary)
        # Beloppet är amount_total (inkl. skatt), formaterat som det står
        self.assertIn(str(self.order.amount_total), summary)
        self.assertIn(self.order.currency_id.name, summary)

    def test_summary_carries_lines(self):
        """Radsammanfattningen ingår — raderna indexeras inte separat."""
        summary = self.order._okf_summary_source()
        self.assertIn('1 rader', summary)

    def test_dirty_fields(self):
        """state/amount_total/partner_id är dirty-fält."""
        fields = self.order._okf_dirty_fields()
        for name in ('state', 'amount_total', 'partner_id'):
            self.assertIn(name, fields)

    def test_register_hook_registers_sale_order(self):
        """_register_hook anropar _okf_register_indexable('sale.order').

        Testet anropar hooken explicit: i en testtransaktion har modellen
        redan laddats, så hooken har redan kört (eller inte) — att läsa
        listan prövar då laddningsordningen, inte koden. Verifierat i
        drift 2026-11-20: `_OKF_EXTRA_INDEXABLE == ['sale.order']` efter
        en riktig modulladdning.
        """
        from odoo.addons.ai_agent_core.models.ai_okf_mixin import (
            _OKF_EXTRA_INDEXABLE)
        before = list(_OKF_EXTRA_INDEXABLE)
        self.order._register_hook()
        self.assertIn('sale.order', _OKF_EXTRA_INDEXABLE)
        # städa så testet inte läcker till andra tester
        if 'sale.order' not in before:
            _OKF_EXTRA_INDEXABLE.remove('sale.order')

    def test_order_line_not_indexed(self):
        """sale.order.line är INTE registrerad — raderna bärs av ordern."""
        models = self.env['ai.okf.mixin']._okf_indexable_models()
        self.assertNotIn('sale.order.line', models)
