import React, { createContext, useContext, useState, useEffect } from 'react';

export type Language = 'en' | 'ta';

interface LanguageContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  toggleLanguage: () => void;
  t: (key: string) => string;
}

const translations: Record<Language, Record<string, string>> = {
  en: {
    // Brand & App
    appName: "MediMate AI",
    appSubtitle: "Personal Health Copilot",
    hackathonBadge: "HacXLerate 2026",
    challengeName: "Challenge 1: Personal Health Copilot",
    demoDataBadge: "DEMO DATA (SYNTHETIC PATIENT)",
    
    // Navigation
    navHome: "Home",
    navDashboard: "Dashboard",
    navUpload: "Upload Records",
    navReportAnalysis: "Report Analysis",
    navHistory: "Health Timeline",
    navSettings: "Settings",

    // Common Actions
    getStarted: "Get Started",
    uploadDocument: "Upload Medical Record",
    viewReport: "View Report",
    editTest: "Edit Result",
    saveChanges: "Save Changes",
    cancel: "Cancel",
    delete: "Delete",
    regenerateSummary: "Regenerate AI Summary",
    viewRawText: "View Raw Extracted Text",
    backToDashboard: "Back to Dashboard",
    learnMore: "Learn More",
    quickSample: "Load Sample Demo Report",

    // Dashboard Metrics
    totalReports: "Total Records",
    totalTests: "Parameters Tracked",
    abnormalTests: "Outside Range",
    activeMeds: "Active Medications",
    recentUploads: "Recent Medical Records",
    timelinePreview: "Health History Preview",
    recentAbnormalAlerts: "Key Clinical Highlights",

    // Disclaimer
    disclaimerTitle: "Medical Disclaimer & Limitations",
    disclaimerShort: "MediMate AI is an educational health copilot and does NOT provide medical diagnosis or prescribe treatments. Always consult your doctor.",
    disclaimerFull: "MediMate AI is an informational educational copilot designed to help you understand health data. It does NOT provide medical diagnosis, treatment plans, or medication prescriptions. Abnormal results are common and should always be reviewed by a licensed physician or healthcare specialist in the context of your symptoms and medical history. Never alter prescribed dosages without doctor consultation.",

    // Analysis page
    summaryTitle: "AI Health Summary",
    tamilSummaryTitle: "தமிழ் மருத்துவ விளக்கம் (Tamil Summary)",
    keyFindings: "Key Observations",
    questionsForDoctor: "Questions to Ask Your Doctor",
    labResultsTable: "Extracted Laboratory Investigations",
    testName: "Investigation / Parameter",
    observedValue: "Observed Value",
    unit: "Unit",
    referenceRange: "Reference Range",
    status: "Interpretation",
    actions: "Actions",
    medicationsTitle: "Identified Prescriptions & Medications",
    conditionsTitle: "Identified Clinical Conditions",

    // Statuses
    normal: "Normal",
    high: "High",
    low: "Low",
    critical: "Attention / Critical",
    verified: "User Verified",
    uncertain: "Check Needed",

    // Settings
    settingsTitle: "System & AI Copilot Settings",
    languageSetting: "Interface & Explanation Language",
    apiKeySetting: "Gemini AI API Key (Optional)",
    apiStatus: "Active AI Engine",
    resetData: "Reset Synthetic Demo Data",
    dataSeededSuccess: "Sample patient dataset refreshed successfully."
  },
  ta: {
    // Brand & App
    appName: "மெடிமேட் AI (MediMate)",
    appSubtitle: "உங்கள் தனிப்பட்ட நல்வாழ்வு வழிகாட்டி",
    hackathonBadge: "HacXLerate 2026",
    challengeName: "சவால் 1: பர்சனல் ஹெல்த் கோபைலட்",
    demoDataBadge: "மாதிரி நோயாளி தரவு (Demo Data)",

    // Navigation
    navHome: "முகப்பு",
    navDashboard: "கட்டுப்பாட்டகம் (Dashboard)",
    navUpload: "அறிக்கை பதிவேற்றம்",
    navReportAnalysis: "அறிக்கை பகுப்பாய்வு",
    navHistory: "உடல்நல வரலாறு (Timeline)",
    navSettings: "அமைப்புகள் (Settings)",

    // Common Actions
    getStarted: "தொடங்குங்கள்",
    uploadDocument: "மருத்துவ ஆவணத்தைப் பதிவேற்றவும்",
    viewReport: "அறிக்கையைக் காண்க",
    editTest: "மாற்றியமைக்க",
    saveChanges: "சேமிக்கவும்",
    cancel: "ரத்து செய்",
    delete: "நீக்குக",
    regenerateSummary: "AI விளக்கத்தை புதுப்பிக்கவும்",
    viewRawText: "அசல் எழுத்துக்களைக் காண்க (Raw Text)",
    backToDashboard: "கட்டுப்பாட்டகத்திற்கு திரும்புக",
    learnMore: "மேலும் அறிய",
    quickSample: "மாதிரி அறிக்கையை ஏற்று",

    // Dashboard Metrics
    totalReports: "மொத்த அறிக்கைகள்",
    totalTests: "கண்காணிக்கப்படும் சோதனைகள்",
    abnormalTests: "மாறுபட்ட அளவுகள்",
    activeMeds: "தற்போதைய மருந்துகள்",
    recentUploads: "சமீபத்திய மருத்துவ அறிக்கைகள்",
    timelinePreview: "உடல்நல வரலாற்று முன்னோட்டம்",
    recentAbnormalAlerts: "முக்கிய மருத்துவ குறிப்புகள்",

    // Disclaimer
    disclaimerTitle: "முக்கிய மருத்துவ எச்சரிக்கை",
    disclaimerShort: "MediMate AI என்பது மருத்துவ அறிக்கைகளை எளிதாக புரிந்து கொள்ள உதவும் தகவல் வழிகாட்டி மட்டுமே. இது நோயறிதலையோ சிகிச்சையையோ வழங்காது.",
    disclaimerFull: "MediMate AI என்பது மருத்துவ அறிக்கைகளை எளிதாக புரிந்து கொள்ள உதவும் தகவல் வழிகாட்டி மட்டுமே. இது எந்தவொரு நோயறிதலையும் (Medical Diagnosis) வழங்காது, மருந்துகளையோ அல்லது சிகிச்சை முறைகளையோ பரிந்துரைக்காது. ஏதேனும் மாறுபட்ட முடிவுகள் இருந்தால், தயவுசெய்து உங்கள் மருத்துவரை நேரில் சந்தித்து ஆலோசனை பெறவும். மருத்துவரின் பரிந்துரை இல்லாமல் மருந்துகளின் அளவை மாற்ற வேண்டாம்.",

    // Analysis page
    summaryTitle: "AI உடல்நல சுருக்கம்",
    tamilSummaryTitle: "தமிழ் மருத்துவ விளக்கம்",
    keyFindings: "முக்கிய கண்டுபிடிப்புகள்",
    questionsForDoctor: "மருத்துவரிடம் கேட்க வேண்டிய கேள்விகள்",
    labResultsTable: "பகுப்பாய்வு செய்யப்பட்ட பரிசோதனை முடிவுகள்",
    testName: "பரிசோதனை பெயர்",
    observedValue: "கண்டறியப்பட்ட அளவு",
    unit: "அளவீட்டு அலகு",
    referenceRange: "பரிந்துரைக்கப்பட்ட வரம்பு",
    status: "நிலை (Interpretation)",
    actions: "செயல்கள்",
    medicationsTitle: "பரிந்துரைக்கப்பட்ட மருந்துகள்",
    conditionsTitle: "குறிப்பிடப்பட்ட உடல்நல நிலைமைகள்",

    // Statuses
    normal: "சாதாரண அளவு (Normal)",
    high: "அதிகம் (High)",
    low: "குறைவு (Low)",
    critical: "கவனிக்கப்பட வேண்டியது (Critical)",
    verified: "சரிபார்க்கப்பட்டது",
    uncertain: "சரிபார்க்க வேண்டும்",

    // Settings
    settingsTitle: "அமைப்புகள் & AI வழிகாட்டி",
    languageSetting: "மொழி தேர்வு (Language)",
    apiKeySetting: "Gemini AI API Key (விருப்பத்தேர்வு)",
    apiStatus: "செயலில் உள்ள AI இன்ஜின்",
    resetData: "மாதிரி தரவை மீட்டமைக்கவும்",
    dataSeededSuccess: "மாதிரி தரவு வெற்றிகரமாக புதுப்பிக்கப்பட்டது."
  }
};

const LanguageContext = createContext<LanguageContextType>({
  language: 'en',
  setLanguage: () => {},
  toggleLanguage: () => {},
  t: (key: string) => key,
});

export const LanguageProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [language, setLanguageState] = useState<Language>(() => {
    const saved = localStorage.getItem('medimate_lang');
    return (saved === 'ta' || saved === 'en') ? saved : 'en';
  });

  const setLanguage = (lang: Language) => {
    setLanguageState(lang);
    localStorage.setItem('medimate_lang', lang);
  };

  const toggleLanguage = () => {
    const nextLang = language === 'en' ? 'ta' : 'en';
    setLanguage(nextLang);
  };

  const t = (key: string): string => {
    return translations[language][key] || translations['en'][key] || key;
  };

  return (
    <LanguageContext.Provider value={{ language, setLanguage, toggleLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = () => useContext(LanguageContext);
