# -*- coding: utf-8 -*-
"""Kostnadskontext på ai.coworker.session — domänfält för sale.

`sale-ai-bridge`: `order_id` läggs via arv i bryggan (core förblir
domän-rent). `partner_id`/`pi_session_id`/`cost_context_confirmed` ligger
i ai_agent_core (res.partner = basmodul).

Registrerar även resolver-strategin "sale_partner" i core-registret så
coworkers med `cost_context_partner_strategy = "sale_partner"` får
partnern härledd via order → kund.

Mönstret är project_ai:s (`project_ai/models/ai_coworker_session.py`) —
samma hooks, samma självständighet, samma "senast arbetad kontext vinner".
"""

import logging
import re

from odoo import fields, models

_logger = logging.getLogger(__name__)


def _sale_partner_strategy(session):
    """Resolver: hitta res.partner via order → kund.

    Ingen gissning: saknas order sätts ingen partner. En påhittad kund i
    kostnadskontexten är värre än ingen kund.
    """
    if session.order_id and session.order_id.partner_id:
        session.partner_id = session.order_id.partner_id.id


try:
    from odoo.addons.ai_agent_core.models.ai_session import (
        register_cost_context_strategy)
    register_cost_context_strategy('sale_partner', _sale_partner_strategy)
except Exception as e:  # pragma: no cover — modulordning
    _logger.warning('kunde inte registrera sale_partner-strategi: %s', e)


class AICoworkerSessionSale(models.Model):
    _inherit = 'ai.coworker.session'

    order_id = fields.Many2one(
        'sale.order', string='Offert/Order', index=True,
        ondelete='set null',
        help='Order (sale.order) som sessionen arbetar med. Kund härleds '
             'via ordern.')

    def _capture_context(self, order=None, partner=None, object_ref=None,
                         **kwargs):
        """En enda skrivpunkt för sälj-kostnadskontext.

        Härledning: order_id ← order; partner_id ← order.partner_id.
        Befintliga värden behålls om inget nytt ges ("senast arbetad
        kontext vinner" — inga nollställningar).

        Anropar super() så övriga bryggor (project_ai, prd_ai) samlas i
        MRO-kedjan.
        """
        self.ensure_one()
        vals = {}
        if order:
            o = order if isinstance(order, models.BaseModel) else \
                self.env['sale.order'].browse(int(order))
            if o:
                vals['order_id'] = o.id
                # "Senast arbetad kontext vinner" — men en SAT partner
                # behålls. Att skriva över den vore att tappa en kund som
                # redan bekräftats för sessionen.
                if o.partner_id and not self.partner_id:
                    vals['partner_id'] = o.partner_id.id
        if partner:
            par = partner if isinstance(partner, models.BaseModel) else \
                self.env['res.partner'].browse(int(partner))
            if par:
                vals['partner_id'] = par.id
        if vals:
            self.write(vals)
        return super()._capture_context(object_ref=object_ref)

    def _session_capture_context(self):
        """Core-hook: härled partner via resolver-strategin (sale_ai).

        Självständig (anropar strategin direkt) så den fungerar även om
        coworkerns `cost_context_partner_strategy` inte satts än.
        """
        self.ensure_one()
        try:
            _sale_partner_strategy(self)
        except Exception as e:
            _logger.warning('session capture (sale) failed: %s', e)
        return super()._session_capture_context()

    def _session_auto_capture(self, prompt):
        """Deterministisk kontextfångst ur användarens prompt.

        - `SO<nummer>` / `S0<nummer>` (Odoo:s ordernamn) → order via `name`
        - `offert <id>` / `order <id>` / `#<id>` → order via numeriskt id

        Fångar bara när order saknas ('senast arbetad kontext vinner').
        Tyst no-op vid fel — hooks får aldrig kasta. Anropar super() så
        övriga bryggor också fångas.
        """
        self.ensure_one()
        try:
            text = (prompt or '').strip()
            if not text:
                return super()._session_auto_capture(prompt)
            if not self.order_id:
                # Odoo:s ordernamn: S00042 / SO42
                m = re.search(r'\bS[O0]\s*(\d{2,})\b', text, re.I)
                if m:
                    o = self.env['sale.order'].search(
                        [('name', '=ilike', 'S%' + m.group(1))], limit=1)
                    if not o:
                        o = self.env['sale.order'].search(
                            [('name', '=ilike', 'SO' + m.group(1))], limit=1)
                    if o.exists():
                        self._capture_context(order=o)
                        return super()._session_auto_capture(prompt)
                # Numeriskt id: "offert 42" / "order #42"
                m = re.search(
                    r'(?:offert|order)\s*#?\s*(\d{2,})', text, re.I)
                if m:
                    o = self.env['sale.order'].browse(int(m.group(1)))
                    if o.exists():
                        self._capture_context(order=o)
                        return super()._session_auto_capture(prompt)
        except Exception as e:
            _logger.warning('session auto-capture (sale) failed: %s', e)
        return super()._session_auto_capture(prompt)
