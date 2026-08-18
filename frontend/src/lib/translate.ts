const TRANSLATIONS: Record<string, string> = {
  // Severity
  'critical': 'crítica', 'high': 'alta', 'medium': 'media', 'low': 'baja',
  'Critical': 'Crítica', 'High': 'Alta', 'Medium': 'Media', 'Low': 'Baja',
  // Types
  'vulnerability': 'vulnerabilidad', 'Vulnerability': 'Vulnerabilidad',
  'remote code execution': 'ejecución remota de código',
  'denial of service': 'denegación de servicio',
  'cross-site scripting': 'cross-site scripting (XSS)',
  'sql injection': 'inyección SQL',
  'buffer overflow': 'desbordamiento de búfer',
  'authentication bypass': 'bypass de autenticación',
  'privilege escalation': 'escalada de privilegios',
  'information disclosure': 'divulgación de información',
  'security bypass': 'bypass de seguridad',
  'input validation': 'validación de entrada',
  'improper input validation': 'validación de entrada defectuosa',
  'improper access control': 'control de acceso defectuoso',
  'missing authentication': 'autenticación ausente',
  'missing authorization': 'autorización ausente',
  'path traversal': 'traversal de rutas',
  'directory traversal': 'traversal de directorios',
  'code injection': 'inyección de código',
  'command injection': 'inyección de comandos',
  'server-side request forgery': 'falsificación de solicitudes del lado del servidor',
  'insecure deserialization': 'deserialización insegura',
  'use after free': 'uso después de liberación',
  'out-of-bounds write': 'escritura fuera de límites',
  'out-of-bounds read': 'lectura fuera de límites',
  'null pointer dereference': 'referencia a puntero nulo',
  'race condition': 'condición de carrera',
  // Products & tech
  'Windows': 'Windows', 'Linux': 'Linux', 'Apache': 'Apache',
  'nginx': 'nginx', 'Chrome': 'Chrome', 'Firefox': 'Firefox',
  'WordPress': 'WordPress', 'Joomla': 'Joomla',
  'SQL Server': 'SQL Server', 'MySQL': 'MySQL', 'PostgreSQL': 'PostgreSQL',
  'Oracle': 'Oracle', 'Java': 'Java', 'PHP': 'PHP', 'Python': 'Python',
  'Node.js': 'Node.js', 'Docker': 'Docker', 'Kubernetes': 'Kubernetes',
  'VMware': 'VMware', 'Microsoft': 'Microsoft', 'Google': 'Google',
  'Apple': 'Apple', 'Cisco': 'Cisco', 'Adobe': 'Adobe',
  // Verbs
  'allows': 'permite', 'enables': 'habilita',
  'An attacker': 'Un atacante', 'an attacker': 'un atacante',
  'The attacker': 'El atacante', 'the attacker': 'el atacante',
  'This could': 'Esto podría', 'this could': 'esto podría',
  'may be exploited': 'puede ser explotada',
  'can be exploited': 'puede ser explotada',
  'leading to': 'lo que puede provocar',
  'resulting in': 'resultando en',
  'which allows': 'lo que permite',
  'allowing': 'permitiendo',
  'remote attackers': 'atacantes remotos',
  'local attackers': 'atacantes locales',
  'unauthenticated attackers': 'atacantes no autenticados',
  'authenticated attackers': 'atacantes autenticados',
  'via': 'mediante',
  'through': 'a través de',
  'in the context of': 'en el contexto de',
  'Note': 'Nota',
  'NOTE': 'NOTA',
}

export function translateDescription(text: string): string {
  if (!text) return text
  let result = text
  // Sort by length descending so longer phrases match first
  const sorted = Object.entries(TRANSLATIONS).sort((a, b) => b[0].length - a[0].length)
  for (const [en, es] of sorted) {
    result = result.split(en).join(es)
  }
  return result
}
