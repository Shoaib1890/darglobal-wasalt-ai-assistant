/**
 * Detects whether a text contains predominantly Arabic characters.
 */
export function isArabicText(text: string): boolean {
  if (!text) return false;
  // Count Arabic characters
  const arabicRegex = /[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF]/g;
  const arabicMatches = text.match(arabicRegex);
  const arabicCount = arabicMatches ? arabicMatches.length : 0;
  
  // Total alphabetic characters
  const totalLetters = text.replace(/[\s\d\p{P}]/gu, '').length;
  if (totalLetters === 0) return false;
  
  return (arabicCount / totalLetters) > 0.3;
}

export function formatTimestamp(date: Date = new Date()): string {
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}
