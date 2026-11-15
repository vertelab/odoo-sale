# odoo-sale — gren 19.0

> **Denna gren är avsiktligt tom.** Modulerna är INTE portade till Odoo 19.
> Grenen finns så att dev-miljöer (`hansolo19`) kan klona den utan att falla,
> men den påstår ingenting om att koden är portad.

## Baseline

| | |
|---|---|
| Källa | `20.0` |
| Moduler | **7** |
| Grenar i repot | `12.0`, `12.0-af`, `12.0-test`, `14.0`, `14.0-attachment-id`, `14.0-compatibility`, `14.0-license`, `16.0`, `17.0`, `18.0`, `20.0`, `8.0`, `9.0`, `Dev-12.0-Fenix-Sprint-02`, `Dev-12.0-Fenix-Sprint-02-AFC-3350`, `master`, `master10`, `master9`, `sale-customer-portal-access`, `sale_order_deadline_task`, `sale_order_import-migration-14.0`, `sale_order_phone_number`, `try_translation_fix` |

## Moduler

- `odoo_screen_capture_sale_order`
- `sale_clear_warning`
- `sale_hr_validation`
- `sale_set_dimensions`
- `sale_setup_cost`
- `sale_sign_bankid`
- `sale_vrtl_sign`

## Blockerare

**1 externa beroenden saknas** i Odoo 19-kärnan och OCA 19.0:

| Beroende | Behövs av |
|---|---|
| `sale_tier_validation` | `sale_hr_validation` |

### Prioritering

Ett beroende som blockerar många moduler ger mest nytta att lösa först:

- `sale_tier_validation` — frisläpper **1** modul(er)

## Nästa steg

Portering sker på `*-pfile`-maskin med versionsagnostisk kod
(`.p.py` / `.p.xml`). Se `/skill:odoo-pfiles`.
