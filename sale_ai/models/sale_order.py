# -*- coding: utf-8 -*-
"""sale.order — OKF-indexerbar (sale_ai).

`sale-ai-bridge`: en offert ÄR kunskap — vad kunden beställde, till vilket
pris, med vilka villkor. Men den syns inte i minnet utan denna brygga.

SCOPE: `company` — en offert är företagets kunskap, inte säljarens. Access
följer orderns läsrätt (via `_resolve_visible_sources` i kärnan).

RADERNA: `sale.order.line` indexeras INTE separat. De bärs av orderns
sammanfattning. Tjugo rader gånger tiotusen ordrar = tvåhundratusen
koncept av brus.

KONTRAKTET (verifierat mot ai_okf_mixin.py 2026-11-19):
  `_okf_concept_key(lang=None, owner_id=None)` — default `<modell>,<id>`
  `_okf_owner_vals()` — exakt EN ägare
  `_okf_summary_source(owner_vals=None)` — sammanfattningen
  `_okf_dirty_fields()` — fält vars ändring gör OKF-fälten inaktuella
  `_okf_artifact_type()` — bryggans egen typ
  `_okf_skip_reason()` — None = indexera

The model owns its SOURCES; `ai.okf.mixin` owns the fields and the flag.
"""

from odoo import models, fields


class SaleOrder(models.Model):
    _name = 'sale.order'
    _inherit = ['sale.order', 'ai.okf.mixin']

    # OKF-taggar: egen relationstabell (en many2many kan inte ligga på en
    # abstrakt mixin — den ger samma tabell för alla ärvande modeller).
    okf_tags = fields.Many2many(
        'ai.okf.tag', 'sale_order_okf_tag_rel', 'res_id', 'tag_id',
        string='OKF Tags')

    # ── Källor ─────────────────────────────────────────────────────────
    #
    # `okf_body`  generisk: `name` + `client_order_ref` + `note`
    # `okf_tags`  egen relationstabell ovan
    # `okf_links` generisk: `partner_id` (res.partner bär mixinen via
    #             base_ai), `company_id`

    def _okf_artifact_type(self):
        """Bryggans egen typ (okf-mixin D12)."""
        return 'sale_order'

    def _okf_summary_source(self, owner_vals=None):
        """Kund, status, belopp, valuta, datum och radsammanfattning.

        Deterministisk och gratis — ingen LLM behövs för att veta att en
        offerta sammanfattas av kund, belopp och rader.
        """
        self.ensure_one()
        parts = []
        if self.partner_id:
            parts.append(self.partner_id.display_name)
        if self.state:
            selection = dict(self._fields['state'].selection)
            parts.append(selection.get(self.state, self.state))
        if self.amount_total:
            currency = self.currency_id.name or ''
            parts.append('%s %s' % (self.amount_total, currency))
        if self.date_order:
            parts.append(str(self.date_order)[:10])
        if self.order_line:
            kinds = {}
            for line in self.order_line:
                key = line.product_id.type if line.product_id else 'other'
                kinds[key] = kinds.get(key, 0) + 1
            parts.append('%d rader (%s)' % (
                len(self.order_line),
                ', '.join('%d st %s' % (n, k) for k, n in kinds.items())))
        return ' — '.join(parts) if parts else None

    def _okf_dirty_fields(self):
        """Fält vars ändring gör OKF-fälten inaktuella.

        state/amount_total/partner_id ändrar sammanfattningen. Interna
        noteringar säger inget om kunskapen och ska inte flagga.
        """
        return {'state', 'amount_total', 'partner_id', 'currency_id',
                'date_order', 'order_line', 'active'}

    def _okf_skip_reason(self):
        """Annullerad order = "tomt just nu", inte "tomt för alltid".

        Konceptet arkiveras via retention, inte genom att hoppas över här.
        """
        return None

    # ── Registrering (okf-mixin D11) ───────────────────────────────────

    def _register_hook(self):
        """Registrera modellen för dirty-indexering.

        Registrering, inte överridning: `_okf_indexable_models()` är en
        `@api.model` på en abstrakt modell.
        """
        res = super()._register_hook()
        self.env['ai.okf.mixin']._okf_register_indexable('sale.order')
        return res
