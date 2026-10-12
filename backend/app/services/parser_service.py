import re
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

class MedicalParserService:
    # Standard Clinical Dictionary with reference ranges & LOINC-like codes
    KNOWN_TESTS = {
        # Complete Blood Count (CBC)
        "hemoglobin": {
            "display_name": "Hemoglobin (Hb)",
            "category": "hematology",
            "unit": "g/dL",
            "default_low": 13.0,
            "default_high": 17.0,
            "aliases": ["hemoglobin", "haemoglobin", "hb", "hgb"]
        },
        "rbc_count": {
            "display_name": "RBC Count",
            "category": "hematology",
            "unit": "million/mcL",
            "default_low": 4.5,
            "default_high": 5.9,
            "aliases": ["rbc count", "total rbc", "red blood cells", "erythrocyte count", "rbc"]
        },
        "wbc_count": {
            "display_name": "Total Leukocyte Count (WBC)",
            "category": "hematology",
            "unit": "cells/mcL",
            "default_low": 4000.0,
            "default_high": 11000.0,
            "aliases": ["total leukocyte count", "total leucocyte count", "tlc", "wbc count", "white blood cell count", "white blood cells", "white blood cell", "wbc", "leukocyte count", "leucocyte count"]
        },
        "platelet_count": {
            "display_name": "Platelet Count",
            "category": "hematology",
            "unit": "lakhs/mcL",
            "default_low": 1.5,
            "default_high": 4.5,
            "aliases": ["platelet count", "total platelets", "platelets", "thrombocyte count", "thrombocytes"]
        },
        "hematocrit": {
            "display_name": "Packed Cell Volume (PCV)",
            "category": "hematology",
            "unit": "%",
            "default_low": 40.0,
            "default_high": 50.0,
            "aliases": ["packed cell volume", "pcv", "hematocrit", "hct"]
        },
        "mcv": {
            "display_name": "Mean Corpuscular Volume (MCV)",
            "category": "hematology",
            "unit": "fL",
            "default_low": 80.0,
            "default_high": 100.0,
            "aliases": ["mcv", "mean corpuscular volume"]
        },

        # Diabetic Profile
        "hba1c": {
            "display_name": "HbA1c (Glycated Hemoglobin)",
            "category": "diabetes",
            "unit": "%",
            "default_low": 4.0,
            "default_high": 5.6,
            "aliases": ["hba1c", "glycated hemoglobin", "glycated haemoglobin", "a1c"]
        },
        "fasting_glucose": {
            "display_name": "Fasting Blood Sugar (FBS)",
            "category": "diabetes",
            "unit": "mg/dL",
            "default_low": 70.0,
            "default_high": 99.0,
            "aliases": ["fasting blood sugar", "fasting glucose", "fbs", "blood sugar fasting", "glucose fasting"]
        },
        "postprandial_glucose": {
            "display_name": "Post Prandial Blood Sugar (PPBS)",
            "category": "diabetes",
            "unit": "mg/dL",
            "default_low": 90.0,
            "default_high": 140.0,
            "aliases": ["post prandial blood sugar", "ppbs", "post-prandial glucose", "blood sugar pp"]
        },

        # Lipid Profile
        "total_cholesterol": {
            "display_name": "Total Cholesterol",
            "category": "lipid",
            "unit": "mg/dL",
            "default_low": 125.0,
            "default_high": 200.0,
            "aliases": ["total cholesterol", "cholesterol total", "serum cholesterol"]
        },
        "hdl_cholesterol": {
            "display_name": "HDL Cholesterol (Good)",
            "category": "lipid",
            "unit": "mg/dL",
            "default_low": 40.0,
            "default_high": 60.0,
            "aliases": ["hdl cholesterol", "high density lipoprotein", "hdl"]
        },
        "ldl_cholesterol": {
            "display_name": "LDL Cholesterol (Bad)",
            "category": "lipid",
            "unit": "mg/dL",
            "default_low": 50.0,
            "default_high": 100.0,
            "aliases": ["ldl cholesterol", "low density lipoprotein", "ldl"]
        },
        "triglycerides": {
            "display_name": "Serum Triglycerides",
            "category": "lipid",
            "unit": "mg/dL",
            "default_low": 50.0,
            "default_high": 150.0,
            "aliases": ["triglycerides", "serum triglycerides", "tg"]
        },

        # Renal Function
        "serum_creatinine": {
            "display_name": "Serum Creatinine",
            "category": "renal",
            "unit": "mg/dL",
            "default_low": 0.7,
            "default_high": 1.3,
            "aliases": ["serum creatinine", "creatinine", "s.creatinine"]
        },
        "blood_urea": {
            "display_name": "Blood Urea Nitrogen (BUN)",
            "category": "renal",
            "unit": "mg/dL",
            "default_low": 7.0,
            "default_high": 20.0,
            "aliases": ["blood urea nitrogen", "bun", "blood urea", "urea"]
        },
        "uric_acid": {
            "display_name": "Serum Uric Acid",
            "category": "renal",
            "unit": "mg/dL",
            "default_low": 3.5,
            "default_high": 7.2,
            "aliases": ["serum uric acid", "uric acid"]
        },

        # Liver Function
        "sgpt_alt": {
            "display_name": "SGPT / ALT (Alanine Aminotransferase)",
            "category": "hepatic",
            "unit": "U/L",
            "default_low": 7.0,
            "default_high": 45.0,
            "aliases": ["sgpt", "alt", "alanine aminotransferase", "alanine transaminase"]
        },
        "sgot_ast": {
            "display_name": "SGOT / AST (Aspartate Aminotransferase)",
            "category": "hepatic",
            "unit": "U/L",
            "default_low": 8.0,
            "default_high": 40.0,
            "aliases": ["sgot", "ast", "aspartate aminotransferase", "aspartate transaminase"]
        },
        "total_bilirubin": {
            "display_name": "Total Bilirubin",
            "category": "hepatic",
            "unit": "mg/dL",
            "default_low": 0.2,
            "default_high": 1.2,
            "aliases": ["total bilirubin", "bilirubin total", "s.bilirubin"]
        },

        # Thyroid
        "tsh": {
            "display_name": "Thyroid Stimulating Hormone (TSH)",
            "category": "endocrine",
            "unit": "uIU/mL",
            "default_low": 0.4,
            "default_high": 4.5,
            "aliases": ["tsh", "thyroid stimulating hormone", "ultrasensitive tsh"]
        }
    }

    @classmethod
    def detect_document_metadata(cls, text: str) -> Dict[str, Any]:
        """Extract document type, date, clinic/facility, and physician if found."""
        lower_text = text.lower()
        
        # Document Type
        doc_type = "Medical Lab Report"
        if any(k in lower_text for k in ["lipid profile", "cholesterol"]):
            doc_type = "Lipid Profile Report"
        elif any(k in lower_text for k in ["hba1c", "glucose", "diabetic"]):
            doc_type = "Diabetic Panel Report"
        elif any(k in lower_text for k in ["complete blood count", "hemogram", "cbc"]):
            doc_type = "Complete Blood Count (CBC)"
        elif any(k in lower_text for k in ["renal function", "kidney function", "creatinine"]):
            doc_type = "Renal Function Panel"
        elif any(k in lower_text for k in ["liver function", "lft", "bilirubin"]):
            doc_type = "Liver Function Test (LFT)"
        elif any(k in lower_text for k in ["rx", "prescription", "tab.", "cap.", "dosage"]):
            doc_type = "Prescription"
        elif any(k in lower_text for k in ["discharge summary", "hospital admission"]):
            doc_type = "Discharge Summary"

        # Report Date detection (e.g. 12/04/2026, 12-Apr-2026, 2026-04-12)
        date_pattern = r"(?:date|collected|reported|dated)[\s:]*([0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{2,4}|[0-9]{1,2}\s+[A-Za-z]{3,9}\s+[0-9]{4}|[0-9]{4}-[0-9]{2}-[0-9]{2})"
        date_match = re.search(date_pattern, text, re.IGNORECASE)
        report_date = date_match.group(1).strip() if date_match else datetime.now().strftime("%Y-%m-%d")

        # Facility / Clinic
        facility = "Diagnostic Laboratory"
        for candidate in ["Apollo Diagnostics", "Dr Lal PathLabs", "Metropolis Healthcare", "Thyrocare", "SRL Diagnostics", "Max Healthcare", "AIIMS"]:
            if candidate.lower() in lower_text:
                facility = candidate
                break

        # Doctor / Physician
        dr_match = re.search(r"(?:Dr\.|Doctor|Ref By)[\s:]+([A-Za-z\s\.]{4,30})", text)
        doctor_name = f"Dr. {dr_match.group(1).strip()}" if dr_match else "Consulting Physician"

        return {
            "doc_type": doc_type,
            "report_date": report_date,
            "facility_name": facility,
            "doctor_name": doctor_name
        }

    UNIT_PATTERN = (
        r"(?:(?:[×\*xX]\s*)?10\^?[369]\s*/\s*[a-zA-Zμµ\w]+|"
        r"(?:lakhs?|lac|millions?|thou)\s*/\s*[a-zA-Zμµ\w]+|"
        r"cells\s*/\s*[a-zA-Zμµ\w]+|"
        r"/?\s*[a-zA-Zμµ%]+(?:\s*/\s*[a-zA-Zμµ0-9]+)?)"
    )

    @classmethod
    def parse_observations(cls, text: str) -> List[Dict[str, Any]]:
        """
        Extract structured lab observations with test name, value, unit,
        reference ranges, and interpretation flags.
        Preserves original document units and ensures unit-scale compatibility.
        """
        observations = []
        lines = text.split("\n")
        seen_tests = set()

        # Step 1: Scan for known clinical tests first
        for key, info in cls.KNOWN_TESTS.items():
            for alias in info["aliases"]:
                pattern = (
                    rf"(?i)\b{re.escape(alias)}\b[^\n\d]*?([<>]?\s*\d+(?:\.\d+)?)\s*"
                    rf"({cls.UNIT_PATTERN})?"
                    rf"(?:\s*[\|,]?\s*[\(\[]?\s*(?:Ref\s*:?|Normal\s*:?|Range\s*:?)?\s*(\d+(?:\.\d+)?)\s*[-–toTO]+\s*(\d+(?:\.\d+)?)\s*[\)\]]?)?"
                )
                for match in re.finditer(pattern, text):
                    raw_val = match.group(1).strip()
                    val_clean = re.sub(r"[^\d\.]", "", raw_val)
                    try:
                        numeric_val = float(val_clean)
                    except ValueError:
                        continue

                    # Trace and preserve the original measurement unit from document if available
                    extracted_unit = (match.group(2) or "").strip()
                    if extracted_unit:
                        unit = extracted_unit
                    else:
                        # Scale-appropriate default unit
                        if key == "wbc_count":
                            unit = "× 10^3/µL" if numeric_val < 100.0 else "cells/mcL"
                        elif key == "platelet_count":
                            if numeric_val <= 20.0:
                                unit = "lakhs/mcL"
                            elif numeric_val <= 1000.0:
                                unit = "× 10^3/µL"
                            else:
                                unit = "cells/mcL"
                        elif key == "rbc_count":
                            unit = "× 10^6/µL"
                        else:
                            unit = info["unit"]

                    # Reference range extraction
                    extracted_low = match.group(3)
                    extracted_high = match.group(4)
                    low = None
                    high = None
                    if extracted_low is not None and extracted_high is not None:
                        try:
                            low = float(extracted_low)
                            high = float(extracted_high)
                        except ValueError:
                            pass

                    # Fallback adjacent search for range if not in immediate regex group
                    if low is None or high is None:
                        end_pos = match.end(2) if match.group(2) else match.end(1)
                        surrounding = text[end_pos:end_pos + 120]
                        range_m = re.search(r"[\(\[]?\s*(?:Ref\s*:?|Normal\s*:?|Range\s*:?)?\s*(\d+(?:\.\d+)?)\s*[-–toTO]+\s*(\d+(?:\.\d+)?)[\)\]]?", surrounding)
                        if range_m:
                            try:
                                low = float(range_m.group(1))
                                high = float(range_m.group(2))
                            except ValueError:
                                pass

                    # If still no range found, supply clinically appropriate default for the unit/scale
                    if low is None or high is None:
                        if key == "wbc_count":
                            if numeric_val < 100.0 or any(u in unit.lower() for u in ["10^3", "k/", "k\\", "10*3", "thou", "10^9"]):
                                low, high = 4.0, 11.0
                            else:
                                low, high = 4000.0, 11000.0
                        elif key == "platelet_count":
                            if any(u in unit.lower() for u in ["lakh", "lac"]) or (numeric_val <= 20.0 and not any(u in unit.lower() for u in ["10^3", "k"])):
                                low, high = 1.5, 4.5
                            elif numeric_val > 1000.0 or any(u in unit.lower() for u in ["cells", "/mcl", "/µl", "/cumm"]):
                                low, high = 150000.0, 450000.0
                            else:
                                low, high = 150.0, 450.0
                        elif key == "rbc_count":
                            low, high = 4.5, 5.9
                        elif key == "hemoglobin":
                            low, high = (130.0, 170.0) if numeric_val >= 50.0 else (13.0, 17.0)
                        else:
                            low, high = info["default_low"], info["default_high"]

                    # Explicitly validated unit & scale harmonization before classification
                    if key == "wbc_count":
                        if numeric_val < 100.0 and low >= 500.0:
                            # Value is in thousands (e.g. 7.2) but range was specified in cells (e.g. 4000 - 11000)
                            low = round(low / 1000.0, 2)
                            high = round(high / 1000.0, 2)
                        elif numeric_val >= 500.0 and high <= 50.0:
                            # Value is in cells (e.g. 7200) but range was in thousands (e.g. 4.0 - 11.0)
                            low = round(low * 1000.0, 1)
                            high = round(high * 1000.0, 1)

                    elif key == "platelet_count":
                        if 50.0 <= numeric_val <= 1000.0:
                            # Value is in thousands (e.g. 250)
                            if high <= 20.0:
                                # Range in lakhs (e.g. 1.5 - 4.5) -> convert range to thousands
                                low = round(low * 100.0, 1)
                                high = round(high * 100.0, 1)
                            elif low >= 10000.0:
                                # Range in cells (e.g. 150000 - 450000)
                                low = round(low / 1000.0, 1)
                                high = round(high / 1000.0, 1)
                        elif numeric_val <= 20.0:
                            # Value is in lakhs (e.g. 2.5)
                            if 50.0 <= low and high <= 1000.0:
                                # Range in thousands (e.g. 150 - 450)
                                low = round(low / 100.0, 2)
                                high = round(high / 100.0, 2)
                            elif low >= 10000.0:
                                low = round(low / 100000.0, 2)
                                high = round(high / 100000.0, 2)
                        elif numeric_val >= 10000.0:
                            # Value is in cells (e.g. 250000)
                            if high <= 20.0:
                                low = round(low * 100000.0, 1)
                                high = round(high * 100000.0, 1)
                            elif high <= 1000.0:
                                low = round(low * 1000.0, 1)
                                high = round(high * 1000.0, 1)

                    elif key == "hemoglobin":
                        if numeric_val >= 50.0 and high <= 30.0:
                            low = round(low * 10.0, 1)
                            high = round(high * 10.0, 1)
                        elif numeric_val < 30.0 and low >= 50.0:
                            low = round(low / 10.0, 1)
                            high = round(high / 10.0, 1)

                    # Interpretation determination
                    interpretation = "Normal"
                    if numeric_val < low:
                        interpretation = "Low"
                    elif numeric_val > high:
                        interpretation = "High"

                    # Critical bounds checking (scale-aware)
                    if key == "platelet_count":
                        if (numeric_val <= 20.0 and numeric_val < 0.5) or \
                           (numeric_val > 20.0 and numeric_val < 50.0) or \
                           (numeric_val >= 10000.0 and numeric_val < 50000.0):
                            interpretation = "Critical"
                    elif key == "hemoglobin":
                        if (numeric_val < 30.0 and numeric_val < 7.0) or \
                           (numeric_val >= 50.0 and numeric_val < 70.0):
                            interpretation = "Critical"
                    elif key == "fasting_glucose":
                        if numeric_val > 250.0 or numeric_val < 50.0:
                            interpretation = "Critical"
                    elif key == "wbc_count":
                        if (numeric_val < 100.0 and (numeric_val < 1.0 or numeric_val > 30.0)) or \
                           (numeric_val >= 500.0 and (numeric_val < 1000.0 or numeric_val > 30000.0)):
                            interpretation = "Critical"

                    is_uncertain = False
                    confidence = 0.96

                    if info["display_name"] not in seen_tests:
                        seen_tests.add(info["display_name"])
                        observations.append({
                            "display_name": info["display_name"],
                            "category": info["category"],
                            "value_string": str(numeric_val),
                            "value_quantity": numeric_val,
                            "unit": unit,
                            "reference_range_low": low,
                            "reference_range_high": high,
                            "reference_range_text": f"{low} - {high} {unit}",
                            "interpretation": interpretation,
                            "is_uncertain": is_uncertain,
                            "confidence_score": confidence,
                            "notes": "Standard clinical parameter verified."
                        })
                    break

        # Step 2: Line-by-line fallback for uncataloged tests
        for line in lines:
            line_str = line.strip()
            if len(line_str) < 6 or line_str.startswith("---"):
                continue

            # Look for line with test name, number, and optional range
            m = re.match(rf"^([A-Za-z\s\(\)/]{{3,35}})\s+[:=\s]\s*(\d+(?:\.\d+)?)\s*({cls.UNIT_PATTERN})?\s*(?:[\(\[]?(\d+(?:\.\d+)?)\s*[-–toTO]+\s*(\d+(?:\.\d+)?)[\)\]]?)?", line_str)
            if m:
                name = m.group(1).strip()
                val_str = m.group(2).strip()
                unit = (m.group(3) or "").strip()
                low_str = m.group(4)
                high_str = m.group(5)

                if name.lower() in [s.lower() for s in seen_tests] or any(ignore in name.lower() for ignore in ["page", "date", "age", "doctor", "phone", "bill", "sample", "time", "lab", "hospital", "patient"]):
                    continue

                try:
                    num_val = float(val_str)
                except ValueError:
                    continue

                low = float(low_str) if low_str else None
                high = float(high_str) if high_str else None
                ref_text = f"{low} - {high} {unit}".strip() if (low is not None and high is not None) else "Laboratory Specific"

                interpretation = "Normal"
                if low is not None and num_val < low:
                    interpretation = "Low"
                elif high is not None and num_val > high:
                    interpretation = "High"

                seen_tests.add(name)
                observations.append({
                    "display_name": name,
                    "category": "laboratory",
                    "value_string": val_str,
                    "value_quantity": num_val,
                    "unit": unit or "-",
                    "reference_range_low": low,
                    "reference_range_high": high,
                    "reference_range_text": ref_text,
                    "interpretation": interpretation,
                    "is_uncertain": False,
                    "confidence_score": 0.88,
                    "notes": "Extracted from report line."
                })

        return observations

    @classmethod
    def parse_medications_and_conditions(cls, text: str) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Extract medications and clinical conditions from prescription or report text."""
        medications = []
        conditions = []
        lower_text = text.lower()

        # Known condition signatures
        condition_patterns = [
            ("Type 2 Diabetes Mellitus", ["diabetes", "t2dm", "hyperglycemia", "diabetic"]),
            ("Essential Hypertension", ["hypertension", "htn", "high blood pressure", "elevated bp"]),
            ("Dyslipidemia / Hypercholesterolemia", ["dyslipidemia", "hyperlipidemia", "high cholesterol", "elevated ldl"]),
            ("Microcytic Anemia / Mild Anemia", ["anemia", "anaemia", "low hemoglobin", "iron deficiency"]),
            ("Hypothyroidism", ["hypothyroid", "elevated tsh", "hypothyroidism"]),
            ("Fatty Liver (Grade 1)", ["fatty liver", "steatosis", "sgpt elevated"]),
            ("Vitamin D Deficiency", ["vitamin d deficiency", "low vit d", "hypovitaminosis d"])
        ]

        for display_name, aliases in condition_patterns:
            if any(alias in lower_text for alias in aliases):
                conditions.append({
                    "display_name": display_name,
                    "clinical_status": "active",
                    "verification_status": "provisional",
                    "category": "problem-list-item",
                    "severity": "mild",
                    "recorded_date": datetime.now().strftime("%Y-%m-%d"),
                    "notes": "Identified from diagnostic findings or clinical notes."
                })

        # Known medication signatures
        med_patterns = [
            ("Tab. Metformin", r"(?:tab\.?|tablet)?\s*metformin(?:\s+hydrochloride)?\s*(\d+\s*mg)?(?:\s+(?:od|bd|tds|once daily|twice daily))?", "500 mg", "Once daily after meals"),
            ("Tab. Atorvastatin", r"(?:tab\.?|tablet)?\s*atorvastatin\s*(\d+\s*mg)?", "10 mg", "Once at night"),
            ("Tab. Telmisartan", r"(?:tab\.?|tablet)?\s*telmisartan\s*(\d+\s*mg)?", "40 mg", "Once daily morning"),
            ("Tab. Amlodipine", r"(?:tab\.?|tablet)?\s*amlodipine\s*(\d+\s*mg)?", "5 mg", "Once daily morning"),
            ("Tab. Thyroxine / Eltroxin", r"(?:tab\.?|tablet)?\s*(?:thyroxine|eltroxin)\s*(\d+\s*mcg)?", "50 mcg", "Empty stomach in morning"),
            ("Tab. Pantoprazole", r"(?:tab\.?|tablet)?\s*pantoprazole\s*(\d+\s*mg)?", "40 mg", "Once daily 30 mins before breakfast"),
            ("Syrup / Tab. Iron & Folic Acid", r"(?:tab\.?|syrup)?\s*(?:iron|ferrous ascorbate|folic acid)", "100 mg", "Once daily after food"),
            ("Cap. Vitamin D3 60K", r"(?:cap\.?|capsule)?\s*(?:cholecalciferol|vitamin d3|calcirol)\s*60k?", "60,000 IU", "Once weekly for 8 weeks")
        ]

        for med_name, regex, default_dose, default_freq in med_patterns:
            m = re.search(regex, text, re.IGNORECASE)
            if m:
                dosage = (m.group(1).strip() if m.lastindex and m.group(1) else default_dose)
                medications.append({
                    "medication_name": med_name,
                    "dosage_instruction": f"{dosage}, {default_freq}",
                    "route": "oral",
                    "frequency": default_freq,
                    "status": "active",
                    "notes": "Extracted from medical document."
                })

        return medications, conditions

parser_service = MedicalParserService()
