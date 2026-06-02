// Slur censoring list
const SLURS = [
  'fuck', 'fucking', 'fucked', 'fucks', 'f***',
  'shit', 'shitty', 'shitty', 'damn', 'dammit',
  'asshole', 'bastard', 'bitch', 'bitches',
  'crap', 'pissed', 'piss', 'ass', 'arse'
];

// Slang dictionary for different languages
const SLANG_DICTIONARY = {
  // Chinese slang
  'zh': {
    '哈': 'haha',
    '呃': 'uh',
    '嗯': 'um',
    '滚': 'get lost',
    '牛逼': 'awesome',
    '傻逼': 'idiot',
    '给力': 'awesome',
    '很HIGH': 'excited',
    '不爽': 'upset'
  },
  // Brazilian Portuguese slang
  'pt': {
    'mano': 'man',
    'cara': 'dude',
    'véio': 'old man',
    'véia': 'old woman',
    'beleza': 'ok',
    'blz': 'ok',
    'tmj': 'together',
    'bolado': 'angry',
    'maconha': 'marijuana',
    'virado': 'turned on',
    'zoado': 'messed up'
  },
  // Vietnamese slang
  'vi': {
    'dạo này': 'lately',
    'tình hình': 'situation',
    'bọn': 'group/gang',
    'gái gú': 'pretty girl',
    'bạn bè': 'friends',
    'ngang ngược': 'stubborn',
    'vô duyên': 'tactless',
    'khó tính': 'picky'
  },
  // German slang
  'de': {
    'Kerl': 'guy',
    'Mädel': 'girl',
    'Alter': 'dude',
    'dufte': 'cool',
    'blöd': 'stupid',
    'nervig': 'annoying',
    'kacke': 'crap',
    'verdammt': 'damn',
    'super': 'great'
  }
};

/**
 * Detect language from text
 */
export function detectLanguage(text) {
  // Simple language detection based on character ranges
  const chineseRegex = /[\u4E00-\u9FA5]/g;
  const vietnameseRegex = /[\u0102\u0103\u0110\u0111\u0128\u0129\u0168\u0169\u01A0\u01A1]/g;
  
  if (chineseRegex.test(text)) {
    return 'zh';
  }
  if (vietnameseRegex.test(text)) {
    return 'vi';
  }
  
  // Check for Portuguese patterns
  if (/[àáâãäåèéêëìíîïòóôõöùúûü]/g.test(text)) {
    return 'pt';
  }
  
  // Check for German patterns
  if (/[äöüß]/g.test(text)) {
    return 'de';
  }
  
  return 'en';
}

/**
 * Censor slurs in text
 */
export function censorSlurs(text) {
  let censored = text;
  
  SLURS.forEach(slur => {
    const regex = new RegExp(`\\b${slur}\\b`, 'gi');
    censored = censored.replace(regex, '***');
  });
  
  return censored;
}

/**
 * Replace slang with more formal/translated versions
 */
export function translateSlang(text, language) {
  let translated = text;
  const slangMap = SLANG_DICTIONARY[language] || {};
  
  Object.entries(slangMap).forEach(([slang, formal]) => {
    const regex = new RegExp(`\\b${slang}\\b`, 'gi');
    translated = translated.replace(regex, formal);
  });
  
  return translated;
}

/**
 * Main translation function using free translation API
 */
export async function translateText(text, targetLanguage = 'en') {
  try {
    // Detect source language
    const sourceLanguage = detectLanguage(text);
    
    // If already English, just censor slurs
    if (sourceLanguage === 'en') {
      return censorSlurs(text);
    }
    
    // Use Google Translate API (free version via script tag)
    const response = await fetch('https://api.mymemory.translated.net/get', {
      method: 'GET',
      headers: {
        'Accept': 'application/json'
      }
    });
    
    // For now, we'll use a simpler approach with built-in translation support
    let translatedText = await simpleTranslate(text, sourceLanguage, targetLanguage);
    
    // Apply slang translation
    translatedText = translateSlang(translatedText, sourceLanguage);
    
    // Censor slurs
    translatedText = censorSlurs(translatedText);
    
    return translatedText;
  } catch (error) {
    console.error('Translation error:', error);
    return text; // Return original if translation fails
  }
}

/**
 * Simple translate using free API
 */
async function simpleTranslate(text, from, to) {
  try {
    const url = `https://api.mymemory.translated.net/get?q=${encodeURIComponent(text)}&langpair=${from}|${to}`;
    const response = await fetch(url);
    const data = await response.json();
    
    if (data.responseStatus === 200) {
      return data.responseData.translatedText;
    }
    return text;
  } catch (error) {
    console.error('Simple translate error:', error);
    return text;
  }
}

/**
 * Batch process messages with translation
 */
export async function processMessage(message) {
  const content = message.content;
  const detectedLang = detectLanguage(content);
  
  // Skip if already English
  if (detectedLang === 'en') {
    return censorSlurs(content);
  }
  
  // Translate to English
  const translated = await translateText(content, 'en');
  return translated;
}
