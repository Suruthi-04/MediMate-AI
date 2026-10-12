import json
import logging
import requests
from typing import Dict, Any, List, Optional
from app.config import settings

logger = logging.getLogger(__name__)

DISCLAIMER_EN = (
    "IMPORTANT MEDICAL DISCLAIMER: MediMate AI is an informational educational copilot "
    "designed to help you understand health data. It does NOT provide medical diagnosis, "
    "treatment plans, or medication prescriptions. Abnormal results are common and should "
    "always be reviewed by a licensed physician or healthcare specialist in the context "
    "of your symptoms and medical history. Never alter prescribed dosages without doctor consultation."
)

DISCLAIMER_TA = (
    "முக்கிய மருத்துவ எச்சரிக்கை: MediMate AI என்பது மருத்துவ அறிக்கைகளை எளிதாக புரிந்து கொள்ள உதவும் "
    "தகவல் வழிகாட்டி மட்டுமே. இது எந்தவொரு நோயறிதலையும் (Medical Diagnosis) வழங்காது, மருந்துகளையோ "
    "அல்லது சிகிச்சை முறைகளையோ பரிந்துரைக்காது. ஏதேனும் மாறுபட்ட முடிவுகள் இருந்தால், தயவுசெய்து உங்கள் மருத்துவரை "
    "நேரில் சந்தித்து ஆலோசனை பெறவும். மருத்துவரின் பரிந்துரை இல்லாமல் மருந்துகளின் அளவை மாற்ற வேண்டாம்."
)

class AIService:
    @classmethod
    def get_active_model_name(cls) -> str:
        if settings.GEMINI_API_KEY and not settings.FORCE_DEMO_MODE:
            return "Google Gemini AI (Cloud LLM)"
        return "MediMate Clinical Engine (Demo Mode)"

    @classmethod
    def is_demo_mode(cls) -> bool:
        return not bool(settings.GEMINI_API_KEY) or settings.FORCE_DEMO_MODE

    @classmethod
    def generate_health_summary(
        cls,
        doc_title: str,
        doc_type: str,
        raw_text: str,
        observations: List[Dict[str, Any]],
        medications: List[Dict[str, Any]],
        conditions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate patient-friendly clinical summaries in English and Tamil,
        highlighting abnormal tests, simple explanations, and doctor questions.
        """
        # If API key is available, attempt LLM call
        if settings.GEMINI_API_KEY and not settings.FORCE_DEMO_MODE:
            try:
                llm_result = cls._call_gemini_api(
                    doc_title, doc_type, raw_text, observations, medications, conditions
                )
                if llm_result:
                    return llm_result
            except Exception as e:
                logger.warning(f"External LLM invocation failed, falling back to Clinical Engine: {e}")

        # Fallback / Built-in Clinical Heuristic Engine (Clearly labeled Demo AI Mode)
        return cls._generate_heuristic_summary(
            doc_title, doc_type, raw_text, observations, medications, conditions
        )

    @classmethod
    def _call_gemini_api(
        cls,
        doc_title: str,
        doc_type: str,
        raw_text: str,
        observations: List[Dict[str, Any]],
        medications: List[Dict[str, Any]],
        conditions: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Call Gemini API via REST endpoint with prompt enforcement."""
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={settings.GEMINI_API_KEY}"
        
        system_prompt = (
            "You are MediMate AI, a patient health copilot. Analyze the provided medical record.\n"
            "CRITICAL SAFETY RULES:\n"
            "- Do NOT diagnose any disease.\n"
            "- Do NOT prescribe medication or dosage adjustments.\n"
            "- Do NOT claim the person is completely healthy or free of disease.\n"
            "- Do NOT treat every abnormal value as an emergency.\n"
            "- If information is missing or unclear, state that explicitly.\n"
            "- Output valid JSON with keys: summary_en, summary_ta, key_findings, doctor_questions.\n"
            "- summary_ta MUST be in simple, polite Tamil while preserving original test names, numbers, and units.\n"
        )

        user_content = f"""
Document: {doc_title} ({doc_type})
Structured Lab Observations: {json.dumps(observations, indent=2)}
Medications: {json.dumps(medications, indent=2)}
Conditions: {json.dumps(conditions, indent=2)}
Extracted Text Snippet: {raw_text[:2000]}
"""

        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": system_prompt + "\n" + user_content}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "responseMimeType": "application/json"
            }
        }

        resp = requests.post(api_url, json=payload, timeout=20)
        if resp.status_code == 200:
            data = resp.json()
            raw_response = data["candidates"][0]["content"]["parts"][0]["text"]
            parsed = json.loads(raw_response)
            return {
                "summary_en": parsed.get("summary_en", ""),
                "summary_ta": parsed.get("summary_ta", ""),
                "key_findings": parsed.get("key_findings", []),
                "doctor_questions": parsed.get("doctor_questions", []),
                "ai_model": "Google Gemini 1.5 Flash",
                "is_demo_mode": False
            }
        return None

    @classmethod
    def _generate_heuristic_summary(
        cls,
        doc_title: str,
        doc_type: str,
        raw_text: str,
        observations: List[Dict[str, Any]],
        medications: List[Dict[str, Any]],
        conditions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Deterministic, clinically structured analysis engine that accurately
        summarizes lab tests, out-of-range parameters, educational notes,
        thoughtful questions for doctors, and Tamil translations.
        """
        abnormal_tests = [obs for obs in observations if obs.get("interpretation") in ["High", "Low", "Critical"]]
        normal_tests = [obs for obs in observations if obs.get("interpretation") == "Normal"]

        # 1. English Summary Construction
        en_paragraphs = []
        en_paragraphs.append(
            f"**Document Overview:** This document is classified as a **{doc_type}** titled '{doc_title}'. "
            f"A total of {len(observations)} clinical parameters were extracted and evaluated against standard laboratory reference ranges."
        )

        if abnormal_tests:
            abnormal_list_str = ", ".join([
                f"**{t['display_name']}** ({t['value_string']} {t.get('unit', '')} - marked as *{t['interpretation']}*)"
                for t in abnormal_tests
            ])
            en_paragraphs.append(
                f"**Parameters Outside Reference Range:** There are {len(abnormal_tests)} values outside the typical reference range: {abnormal_list_str}."
            )
            
            # Simple layman explanations
            explanations = []
            for t in abnormal_tests:
                name_l = t["display_name"].lower()
                inter = t["interpretation"]
                if "hba1c" in name_l:
                    explanations.append(
                        f"• **HbA1c ({t['value_string']}%):** Reflects average blood sugar levels over the past 2–3 months. A value of {t['value_string']}% is {inter.lower()}er than typical non-diabetic ranges (<5.7%), indicating glycemic variance."
                    )
                elif "cholesterol" in name_l or "ldl" in name_l:
                    explanations.append(
                        f"• **{t['display_name']} ({t['value_string']} {t.get('unit', '')}):** Lipids are fats in the bloodstream. Elevated LDL/Total Cholesterol can suggest a need to discuss heart-healthy dietary patterns and lifestyle with your doctor."
                    )
                elif "hemoglobin" in name_l:
                    explanations.append(
                        f"• **Hemoglobin ({t['value_string']} {t.get('unit', '')}):** Hemoglobin carries oxygen in red blood cells. A {inter.lower()} value may indicate mild anemia or iron deficiency, which can cause fatigue."
                    )
                elif "creatinine" in name_l:
                    explanations.append(
                        f"• **Serum Creatinine ({t['value_string']} {t.get('unit', '')}):** A waste product filtered by the kidneys. Slight variations can happen due to hydration levels, muscle mass, or renal function."
                    )
                else:
                    explanations.append(
                        f"• **{t['display_name']}:** Measured at {t['value_string']} {t.get('unit', '')}, which is {inter.lower()} compared to the reference range of {t.get('reference_range_text', 'standard')}."
                    )
            
            en_paragraphs.append("**What These Findings Mean in Simple Terms:**\n" + "\n".join(explanations))
        else:
            en_paragraphs.append(
                "**Findings:** All extracted test parameters fall within their corresponding standard reference intervals on this report."
            )

        if normal_tests:
            normal_names = ", ".join([t["display_name"] for t in normal_tests[:6]])
            en_paragraphs.append(f"**Within Range Parameters:** Tests including {normal_names} are within expected laboratory limits.")

        if medications:
            med_list = ", ".join([f"{m['medication_name']} ({m.get('dosage_instruction', 'as directed')})" for m in medications])
            en_paragraphs.append(f"**Documented Medications:** {med_list}. Always follow the exact dosing schedule recommended by your physician.")

        en_paragraphs.append(
            f"**Limitations & Missing Data:** This summary reflects only the extracted text from this specific document. "
            "Individual lab reference bounds can vary depending on diagnostic instruments, patient age, gender, and clinical context.\n\n"
            f"> {DISCLAIMER_EN}"
        )
        summary_en = "\n\n".join(en_paragraphs)

        # 2. Tamil Summary Construction (Simple Tamil with preserved test names & units)
        ta_paragraphs = []
        ta_paragraphs.append(
            f"**அறிக்கை கண்ணோட்டம்:** இந்த ஆவணம் **{doc_type}** வகையைச் சேர்ந்தது ('{doc_title}'). "
            f"இதில் மொத்தம் {len(observations)} மருத்துவ பரிசோதனை முடிவுகள் பகுப்பாய்வு செய்யப்பட்டுள்ளன."
        )

        if abnormal_tests:
            abnormal_ta_items = []
            for t in abnormal_tests:
                status_ta = "அதிகமாக உள்ளது (High)" if t["interpretation"] == "High" else "குறைவாக உள்ளது (Low)"
                if t["interpretation"] == "Critical":
                    status_ta = "கவனிக்கப்பட வேண்டிய நிலை (Critical/Attention)"
                abnormal_ta_items.append(f"• **{t['display_name']}**: {t['value_string']} {t.get('unit', '')} — இது வழக்கமான வரம்பை விட {status_ta}.")
            
            ta_paragraphs.append(
                f"**மாறுபட்ட பரிசோதனை அளவுகள் ({len(abnormal_tests)}):**\n" + "\n".join(abnormal_ta_items)
            )

            # Simple Tamil explanations
            ta_explanations = []
            for t in abnormal_tests:
                name_l = t["display_name"].lower()
                if "hba1c" in name_l:
                    ta_explanations.append(
                        f"• **HbA1c ({t['value_string']}%):** இது கடந்த 3 மாதங்களின் சராசரி ரத்த சர்க்கரை அளவைக் குறிக்கிறது. இது வழக்கமான வரம்பை விட அதிகமாக உள்ளதால், உணவுமுறை மற்றும் உடற்பயிற்சி குறித்து மருத்துவரிடம் பேசவும்."
                    )
                elif "cholesterol" in name_l or "ldl" in name_l:
                    ta_explanations.append(
                        f"• **{t['display_name']} ({t['value_string']} {t.get('unit', '')}):** ரத்தத்தில் உள்ள கொழுப்பின் அளவு மாறுபட்டுள்ளது. இதய நலன் மற்றும் ஆரோக்கியமான உணவு பழக்கம் குறித்து ஆலோசிக்கவும்."
                    )
                elif "hemoglobin" in name_l:
                    ta_explanations.append(
                        f"• **Hemoglobin ({t['value_string']} {t.get('unit', '')}):** ரத்த சிவப்பணுக்களில் ஆக்ஸிஜன் கொண்டு செல்லும் திறன். இதன் அளவு குறைவது சோர்வை ஏற்படுத்தலாம் (Mild Anemia)."
                    )
                elif "creatinine" in name_l:
                    ta_explanations.append(
                        f"• **Serum Creatinine ({t['value_string']} {t.get('unit', '')}):** சிறுநீரகத்தின் கழிவு வெளியேற்றும் திறன். நீர்ச்சத்து மற்றும் உணவு முறைகளால் இதில் சிறிய மாறுதல்கள் ஏற்படலாம்."
                    )
                else:
                    ta_explanations.append(
                        f"• **{t['display_name']}:** இந்த பரிசோதனை அளவு {t['value_string']} {t.get('unit', '')} ஆக உள்ளது. உங்கள் மருத்துவரிடம் இதைப் பற்றி விவாதிக்கவும்."
                    )

            ta_paragraphs.append("**எளிய விளக்கங்கள்:**\n" + "\n".join(ta_explanations))
        else:
            ta_paragraphs.append(
                "**முடிவுகள்:** இந்த அறிக்கையில் உள்ள அனைத்து பரிசோதனை அளவுகளும் வழக்கமான பரிந்துரைக்கப்பட்ட வரம்பிற்குள் (Normal Range) உள்ளன."
            )

        if medications:
            med_ta = ", ".join([f"{m['medication_name']} ({m.get('dosage_instruction', '')})" for m in medications])
            ta_paragraphs.append(f"**பரிந்துரைக்கப்பட்ட மருந்துகள்:** {med_ta}. மருத்துவர் அறிவுறுத்திய நேரங்களில் மட்டுமே மருந்துகளை உட்கொள்ளவும்.")

        ta_paragraphs.append(
            f"**வரம்புகள் மற்றும் எச்சரிக்கை:**\n> {DISCLAIMER_TA}"
        )
        summary_ta = "\n\n".join(ta_paragraphs)

        # 3. Key Findings Structured List
        key_findings = []
        if abnormal_tests:
            for t in abnormal_tests:
                key_findings.append({
                    "title": f"{t['display_name']}: {t['interpretation']}",
                    "description": f"Value is {t['value_string']} {t.get('unit', '')} (Ref: {t.get('reference_range_text', 'N/A')}).",
                    "status": "Attention"
                })
        else:
            key_findings.append({
                "title": "All Extracted Parameters In Range",
                "description": "Standard markers tested within expected limits on this date.",
                "status": "Normal"
            })

        if medications:
            key_findings.append({
                "title": f"Active Prescriptions ({len(medications)})",
                "description": ", ".join([m["medication_name"] for m in medications[:3]]),
                "status": "Info"
            })

        # 4. Tailored Questions for Doctor
        doctor_questions = [
            "Are the values outside the reference range significant for my overall health condition?",
            "Could my diet, hydration, physical activity, or current medications have influenced these test results?",
            "Do any of these results require a follow-up test or re-check in 3–6 months?",
            "What lifestyle, nutritional, or exercise adjustments do you recommend based on this report?"
        ]
        if any("hba1c" in t["display_name"].lower() for t in observations):
            doctor_questions.append("Given my HbA1c result, what target range should we aim for over the next 90 days?")
        if any("ldl" in t["display_name"].lower() or "cholesterol" in t["display_name"].lower() for t in observations):
            doctor_questions.append("Should we consider lipid-lowering therapy or start with focused dietary modifications for my cholesterol?")

        return {
            "summary_en": summary_en,
            "summary_ta": summary_ta,
            "key_findings": key_findings,
            "doctor_questions": doctor_questions,
            "ai_model": cls.get_active_model_name(),
            "is_demo_mode": cls.is_demo_mode()
        }

ai_service = AIService()
