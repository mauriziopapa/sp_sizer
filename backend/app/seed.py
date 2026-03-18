from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext

from app.config import settings
from app.models import (
    User, SizerSection, SizerFactor, ScoreRange, GovernanceRule, RiskFlag,
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECTIONS = [
    {"code": "BUSINESS", "name": "Sezione Business",
     "description": "Owner: Account Manager | Da completare prima del Gate G1",
     "owner_role": "AM", "display_order": 1},
    {"code": "TECNICO", "name": "Sezione Tecnica",
     "description": "Owner: TL (tecnica) + QO (testing) + PM (delivery) | Da completare prima del Gate G1",
     "owner_role": "TL + QO + PM", "display_order": 2},
]

FACTORS = [
    # Business (C01-C08)
    {"section": "BUSINESS", "code": "C01", "name": "Dimensione cliente",
     "question": "Quanto è grande e strategico l'account?",
     "weight": 3, "owner_role": "AM", "display_order": 1,
     "score_labels": {"1": "Micro/startup", "2": "PMI piccola", "3": "PMI media", "4": "Corporate", "5": "Enterprise/Multinazionale"}},
    {"section": "BUSINESS", "code": "C02", "name": "Criticità business",
     "question": "Cosa succede se il progetto fallisce o si blocca?",
     "weight": 5, "owner_role": "AM", "display_order": 2,
     "score_labels": {"1": "Nessun impatto", "2": "Impatto limitato", "3": "Impatto medio", "4": "Impatto alto", "5": "Business critico/revenue a rischio"}},
    {"section": "BUSINESS", "code": "C03", "name": "Urgency / deadline",
     "question": "Esiste una deadline non negoziabile (go-live, compliance, evento)?",
     "weight": 4, "owner_role": "AM", "display_order": 3,
     "score_labels": {"1": "Nessuna deadline", "2": "Data orientativa", "3": "Deadline importante", "4": "Deadline contrattuale", "5": "Deadline legale/regolatoria"}},
    {"section": "BUSINESS", "code": "C04", "name": "Numero stakeholder attivi",
     "question": "Quante persone hanno potere decisionale lato cliente?",
     "weight": 4, "owner_role": "AM", "display_order": 4,
     "score_labels": {"1": "1 persona", "2": "2 persone", "3": "3-4 persone", "4": "5-6 persone", "5": ">6 persone + Steering"}},
    {"section": "BUSINESS", "code": "C05", "name": "Disponibilità cliente",
     "question": "Il cliente ha tempo per approvare, testare e partecipare alle sessioni?",
     "weight": 4, "owner_role": "AM", "display_order": 5,
     "score_labels": {"1": "Alta disponibilità", "2": "Buona", "3": "Media", "4": "Limitata", "5": "Molto limitata/asincrona forzata"}},
    {"section": "BUSINESS", "code": "C06", "name": "Vincoli compliance / security",
     "question": "Esistono vincoli regolatori, audit, GDPR, ISO o security rilevanti?",
     "weight": 4, "owner_role": "AM", "display_order": 6,
     "score_labels": {"1": "Nessuno", "2": "Minimi", "3": "Presenti e gestibili", "4": "Rilevanti", "5": "Stringenti/certificazioni obbligatorie"}},
    {"section": "BUSINESS", "code": "C07", "name": "Fixed Price",
     "question": "Il contratto è a prezzo fisso?",
     "weight": 3, "owner_role": "AM", "display_order": 7,
     "score_labels": {"1": "T&M puro", "2": "T&M con cap", "3": "Misto", "4": "Prevalentemente FP", "5": "Fixed Price stretto"}},
    {"section": "BUSINESS", "code": "C08", "name": "Budget stimato",
     "question": "Qual è l'ordine di grandezza del valore contrattuale?",
     "weight": 4, "owner_role": "AM", "display_order": 8,
     "score_labels": {"1": "<5k€", "2": "5–15k€", "3": "15–40k€", "4": "40–100k€", "5": ">100k€"}},
    # Tecnici (T01-T08)
    {"section": "TECNICO", "code": "T01", "name": "Numero integrazioni esterne",
     "question": "Quante API/sistemi esterni devono essere connessi?",
     "weight": 5, "owner_role": "TL", "sub_area": "AREA TECNICA", "display_order": 1,
     "score_labels": {"1": "0 integrazioni", "2": "1", "3": "2-3", "4": "4-5", "5": ">5 o architettura event-driven"}},
    {"section": "TECNICO", "code": "T02", "name": "Migrazione dati",
     "question": "È prevista migrazione dati? Qual è la qualità dei dati sorgente?",
     "weight": 4, "owner_role": "TL", "sub_area": "AREA TECNICA", "display_order": 2,
     "score_labels": {"1": "No migrazione", "2": "Dati puliti, volume basso", "3": "Pulizia necessaria", "4": "Qualità scarsa", "5": "Qualità scarsa + volume alto"}},
    {"section": "TECNICO", "code": "T03", "name": "Custom dev / automazioni",
     "question": "Quanto sviluppo custom o quante automazioni complesse sono previste?",
     "weight": 4, "owner_role": "TL", "sub_area": "AREA TECNICA", "display_order": 3,
     "score_labels": {"1": "Solo configurazione", "2": "Custom minimo", "3": "Custom moderato", "4": "Custom esteso", "5": "Custom critico + automazioni complesse"}},
    {"section": "TECNICO", "code": "T04", "name": "Impatto architetturale",
     "question": "Il progetto impatta l'architettura esistente o richiede pattern multi-ambiente?",
     "weight": 4, "owner_role": "TL", "sub_area": "AREA TECNICA", "display_order": 4,
     "score_labels": {"1": "Nessun impatto", "2": "Modifica marginale", "3": "Estensione architettura", "4": "Redesign parziale", "5": "Redesign significativo"}},
    {"section": "TECNICO", "code": "T08", "name": "Rischio tecnico complessivo",
     "question": "Qual è la valutazione globale del rischio tecnico?",
     "weight": 5, "owner_role": "TL", "sub_area": "AREA TECNICA", "display_order": 5,
     "score_labels": {"1": "Tecnologia consolidata", "2": "Rischio basso", "3": "Rischio medio", "4": "Incertezze significative", "5": "Alto rischio + dipendenze critiche"}},
    {"section": "TECNICO", "code": "T05", "name": "Necessità testing esteso",
     "question": "I test richiedono regression, performance, UAT esteso o certificazioni?",
     "weight": 3, "owner_role": "QO", "sub_area": "AREA QUALITÀ", "display_order": 6,
     "score_labels": {"1": "Solo smoke test", "2": "Test funzionali base", "3": "Test strutturati", "4": "Regression + performance", "5": "Certificazione/compliance testing"}},
    {"section": "TECNICO", "code": "T06", "name": "Numero release / sprint pianificati",
     "question": "Quante release/sprint sono previste nel piano di delivery?",
     "weight": 3, "owner_role": "PM", "sub_area": "AREA DELIVERY", "display_order": 7,
     "score_labels": {"1": "1 release unica", "2": "2 release", "3": "3-4 release", "4": "5-7 release", "5": ">7 release o continuous delivery"}},
    {"section": "TECNICO", "code": "T07", "name": "Numero team / ruoli coinvolti",
     "question": "Quanti ruoli diversi (interni + cliente) sono attivamente coinvolti?",
     "weight": 3, "owner_role": "PM", "sub_area": "AREA DELIVERY", "display_order": 8,
     "score_labels": {"1": "1-2 persone", "2": "3 persone", "3": "4-5 persone", "4": "6-8 persone", "5": ">8 persone o team distribuiti"}},
]

SCORE_RANGES = [
    {"size_code": "SMALL", "size_label": "SMALL — Governance leggera ma completa",
     "min_score": 0, "max_score": 40, "color": "#22C55E", "emoji": "🟢", "display_order": 1},
    {"size_code": "PMI", "size_label": "PMI — Governance standard strutturata",
     "min_score": 41, "max_score": 70, "color": "#F59E0B", "emoji": "🟡", "display_order": 2},
    {"size_code": "ENTERPRISE", "size_label": "ENTERPRISE — Governance completa e formalizzata",
     "min_score": 71, "max_score": 100, "color": "#EF4444", "emoji": "🔴", "display_order": 3},
]

GOVERNANCE_RULES = [
    {"element": "Baseline", "size": "SMALL", "value": "Sintetica 2-5 pag."},
    {"element": "Baseline", "size": "PMI", "value": "Completa"},
    {"element": "Baseline", "size": "ENTERPRISE", "value": "Estesa + versionata"},
    {"element": "SAL", "size": "SMALL", "value": "Asincrono 1x/sett"},
    {"element": "SAL", "size": "PMI", "value": "Meeting settimanale"},
    {"element": "SAL", "size": "ENTERPRISE", "value": "Meeting + Executive"},
    {"element": "Testbook", "size": "SMALL", "value": "Essenziale"},
    {"element": "Testbook", "size": "PMI", "value": "Strutturato"},
    {"element": "Testbook", "size": "ENTERPRISE", "value": "Esteso + RTM"},
    {"element": "Contingency", "size": "SMALL", "value": "10%"},
    {"element": "Contingency", "size": "PMI", "value": "15%"},
    {"element": "Contingency", "size": "ENTERPRISE", "value": "20%"},
    {"element": "CAPA", "size": "SMALL", "value": "Solo se deviazioni"},
    {"element": "CAPA", "size": "PMI", "value": "Tracciata"},
    {"element": "CAPA", "size": "ENTERPRISE", "value": "Formale"},
    {"element": "WOW items", "size": "SMALL", "value": "1 item"},
    {"element": "WOW items", "size": "PMI", "value": "1-2 items"},
    {"element": "WOW items", "size": "ENTERPRISE", "value": "2 + CSAT milestone"},
    {"element": "Escalation", "size": "SMALL", "value": "L1-L2"},
    {"element": "Escalation", "size": "PMI", "value": "L1-L2"},
    {"element": "Escalation", "size": "ENTERPRISE", "value": "L1-L2-L3"},
    {"element": "Steering", "size": "SMALL", "value": "\u2014"},
    {"element": "Steering", "size": "PMI", "value": "\u2014"},
    {"element": "Steering", "size": "ENTERPRISE", "value": "Obbligatorio"},
    {"element": "RAID", "size": "SMALL", "value": "\u2014"},
    {"element": "RAID", "size": "PMI", "value": "Opzionale"},
    {"element": "RAID", "size": "ENTERPRISE", "value": "Obbligatorio"},
    {"element": "COO/SPO", "size": "SMALL", "value": "Su soglia"},
    {"element": "COO/SPO", "size": "PMI", "value": "Su soglia"},
    {"element": "COO/SPO", "size": "ENTERPRISE", "value": "Strutturale"},
]

RISK_FLAGS = [
    {"code": "RF01", "label": "Fixed Price + Alta complessità",
     "description": "Rischio margine elevato — contingency 20% minimo",
     "condition_logic": {"factors": [{"code": "C07", "operator": ">=", "value": 4}, {"code": "T03", "operator": ">=", "value": 4}], "logic": "AND"},
     "severity": "CRITICAL", "display_order": 1},
    {"code": "RF02", "label": "Deadline non negoziabile + Integrazioni >3",
     "description": "Rischio timeline — commit date da validare con TL",
     "condition_logic": {"factors": [{"code": "C03", "operator": ">=", "value": 4}, {"code": "T01", "operator": ">=", "value": 4}], "logic": "AND"},
     "severity": "CRITICAL", "display_order": 2},
    {"code": "RF03", "label": "Stakeholder >4 + CPO non identificato",
     "description": "Rischio governance — nominare CPO prima di G2",
     "condition_logic": {"factors": [{"code": "C04", "operator": ">=", "value": 4}], "logic": "AND"},
     "severity": "WARNING", "display_order": 3},
    {"code": "RF04", "label": "Dati scarsa qualità + Migrazione prevista",
     "description": "Rischio delivery — discovery tecnica approfondita",
     "condition_logic": {"factors": [{"code": "T02", "operator": ">=", "value": 4}], "logic": "AND"},
     "severity": "WARNING", "display_order": 4},
    {"code": "RF05", "label": "Compliance rilevante + Custom dev esteso",
     "description": "Rischio qualità — testbook esteso obbligatorio",
     "condition_logic": {"factors": [{"code": "C06", "operator": ">=", "value": 4}, {"code": "T03", "operator": ">=", "value": 4}], "logic": "AND"},
     "severity": "CRITICAL", "display_order": 5},
]


async def seed_database(db: AsyncSession) -> None:
    """Seed database with initial data if empty. Idempotent."""
    # Check if already seeded
    result = await db.execute(select(SizerSection).limit(1))
    if result.scalar_one_or_none() is not None:
        return

    # Create admin user
    admin = User(
        username=settings.ADMIN_USERNAME,
        email=settings.ADMIN_EMAIL,
        hashed_password=pwd_context.hash(settings.ADMIN_PASSWORD),
        role="ADMIN",
    )
    db.add(admin)

    # Create sections
    section_map = {}
    for s in SECTIONS:
        section = SizerSection(**s)
        db.add(section)
        section_map[s["code"]] = section
    await db.flush()

    # Create factors and compute max_score_theoretical
    section_max_scores: dict[str, int] = {}
    for f_data in FACTORS:
        section_code = f_data.pop("section")
        factor = SizerFactor(section_id=section_map[section_code].id, **f_data)
        db.add(factor)
        f_data["section"] = section_code  # restore
        max_contrib = f_data["weight"] * 5
        section_max_scores[section_code] = section_max_scores.get(section_code, 0) + max_contrib

    # Update theoretical max scores
    for code, max_score in section_max_scores.items():
        section_map[code].max_score_theoretical = max_score

    # Create score ranges
    range_map = {}
    for sr in SCORE_RANGES:
        score_range = ScoreRange(**sr)
        db.add(score_range)
        range_map[sr["size_code"]] = score_range
    await db.flush()

    # Create governance rules
    for idx, gr in enumerate(GOVERNANCE_RULES):
        rule = GovernanceRule(
            element=gr["element"],
            score_range_id=range_map[gr["size"]].id,
            value=gr["value"],
            display_order=idx + 1,
        )
        db.add(rule)

    # Create risk flags
    for rf in RISK_FLAGS:
        flag = RiskFlag(**rf)
        db.add(flag)

    await db.commit()
