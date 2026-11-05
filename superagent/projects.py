from dataclasses import dataclass


@dataclass(frozen=True)
class Project:
    key: str
    name: str
    repository: str
    owner_account: str
    mission: str


PROJECTS = (
    Project("clinic", "Clinic ERP", "senthilsrinivasanmuthaiyan/clinic", "senthilsrinivasanmuthaiyan", "Clinic operations, appointments, patient portal, clinical workflows, billing and tenant isolation."),
    Project("school", "School ERP", "senthilsrinivasanmuthaiyan/school", "senthilsrinivasanmuthaiyan", "Admissions, students, parents, attendance, fees, transport, learning and school administration."),
    Project("jewel-pos", "Jewel POS ERP", "senthilsrinivasanmuthaiyan/jewel-pos", "senthilsrinivasanmuthaiyan", "Jewellery POS, metal rates, purity, tagged inventory, job work, accounting and GST workflows."),
    Project("universal-pos", "Universal POS ERP", "senthilsrinivasanmuthaiyan/universal-pos", "senthilsrinivasanmuthaiyan", "Multi-industry POS, barcode, checkout, inventory, purchasing, returns, reports and offline readiness."),
    Project("manufacturing", "Manufacturing ERP", "senthilsrinivasanmuthaiyan/manufacturing", "senthilsrinivasanmuthaiyan", "BOM, production planning, work orders, procurement, quality, maintenance and traceable stock."),
    Project("chitfund", "Chit Fund ERP", "senthilsrinivasanmuthaiyan/chitfund", "senthilsrinivasanmuthaiyan", "Schemes, members, collections, auctions, payouts, agent settlement, accounting and audit."),
    Project("onepass", "OnePass", "senthilsrinivasanmuthaiyan/onepass", "senthilsrinivasanmuthaiyan", "Consumer marketplace, merchant portal, bookings, membership, loyalty and local discovery."),
    Project("saas-admin", "SaaS Admin", "senthilsrinivasanmuthaiyan/sassadmin", "senthilsrinivasanmuthaiyan", "Central multi-product control plane, tenant provisioning, plans, entitlements, identity and operations."),
    Project("travel", "Travel", "senthilsrinivasanmuthaiyan1/travel", "senthilsrinivasanmuthaiyan1", "Tamil Nadu travel marketplace, providers, itineraries, bookings, payments and traveller experience."),
    Project("transport-fleet", "Transport Fleet ERP", "senthilsrinivasanmuthaiyan1/transport-fleet", "senthilsrinivasanmuthaiyan1", "Fleet, vehicles, drivers, trips, dispatch, GPS, maintenance, compliance and transport billing."),
    Project("retail", "Retail ERP", "senthilsrinivasanmuthaiyan1/retail", "senthilsrinivasanmuthaiyan1", "Retail and quick-commerce, catalog, POS, inventory, procurement, customer app and fulfilment."),
)


def get_project(key: str) -> Project | None:
    return next((project for project in PROJECTS if project.key == key), None)
