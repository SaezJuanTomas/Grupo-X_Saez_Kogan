# Frontend Integration Guide - n8n Vulnerability Display

## Overview

After n8n processes vulnerabilities and stores them in the backend, the frontend automatically displays them. This guide explains how to enhance the display with:

- 🟨 Critical vulnerability highlighting (yellow background)
- 🚨 "Alerta crítica" badge
- 📊 Smart sorting (critical first, then by IRC descending)
- ⚡ Auto-refresh capability

---

## Current Implementation (VulnerabilitiesPage.tsx)

Your existing page fetches and displays vulnerabilities. We'll enhance it with critical highlighting.

### Component Enhancement

Add a helper function to determine highlight styles:

```typescript
// At the top of VulnerabilitiesPage.tsx
const getSeverityStyle = (severity: string, irc: number) => {
  const baseClasses = 'p-4 border-l-4 rounded-md transition-colors';
  
  if (severity === 'Crítica') {
    return `${baseClasses} bg-yellow-50 border-yellow-500 shadow-sm hover:bg-yellow-100`;
  }
  if (severity === 'Alta') {
    return `${baseClasses} bg-red-50 border-red-500`;
  }
  if (severity === 'Media') {
    return `${baseClasses} bg-orange-50 border-orange-500`;
  }
  return `${baseClasses} bg-blue-50 border-blue-500`;
};

const renderCriticalBadge = (severity: string) => {
  if (severity === 'Crítica') {
    return (
      <span className="inline-block ml-2 px-2 py-1 bg-red-600 text-white text-xs font-bold rounded">
        Alerta crítica
      </span>
    );
  }
  return null;
};
```

### Sorting Enhancement

Enhance the vulnerability list with smart sorting:

```typescript
// Add sorting logic in component
const sortedVulnerabilities = useMemo(() => {
  const sorted = [...vulnerabilities];
  
  // Primary sort: Critical first
  sorted.sort((a, b) => {
    if (a.severity === 'Crítica' && b.severity !== 'Crítica') return -1;
    if (a.severity !== 'Crítica' && b.severity === 'Crítica') return 1;
    
    // Secondary sort: By IRC descending
    return (b.irc || 0) - (a.irc || 0);
  });
  
  return sorted;
}, [vulnerabilities]);
```

### Render Vulnerability Card

```tsx
{sortedVulnerabilities.map((vuln) => (
  <div
    key={vuln.id}
    className={getSeverityStyle(vuln.severity, vuln.irc)}
    onClick={() => handleSelect(vuln.id)}
  >
    <div className="flex justify-between items-start">
      <div className="flex-1">
        <h3 className="font-bold text-lg">
          {vuln.cve}
          {renderCriticalBadge(vuln.severity)}
        </h3>
        
        <p className="text-sm text-gray-600 mt-2">{vuln.description}</p>
        
        <div className="grid grid-cols-2 gap-3 mt-3 text-sm">
          <div>
            <span className="font-semibold">IRC:</span> {vuln.irc?.toFixed(2)}
          </div>
          <div>
            <span className="font-semibold">Severidad:</span> {vuln.severity}
          </div>
          <div>
            <span className="font-semibold">Empresa:</span> {vuln.company?.name}
          </div>
          <div>
            <span className="font-semibold">Analista:</span>{' '}
            {vuln.analyst?.username || 'Sin asignar'}
          </div>
        </div>
        
        <div className="text-xs text-gray-500 mt-2 pt-2 border-t border-gray-200">
          Creado: {new Date(vuln.created_at).toLocaleDateString()}
        </div>
      </div>
    </div>
  </div>
))}
```

---

## Complete Implementation Example

### Full VulnerabilitiesPage Enhancement

```tsx
import React, { useMemo, useState, useEffect } from 'react';
import { Vulnerability } from '../types';
import { api } from '../lib/api';

export function VulnerabilitiesPage() {
  const [vulnerabilities, setVulnerabilities] = useState<Vulnerability[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedId, setSelectedId] = useState<number | null>(null);

  // Load vulnerabilities on mount
  useEffect(() => {
    loadVulnerabilities();
  }, []);

  const loadVulnerabilities = async () => {
    try {
      setLoading(true);
      const data = await api.get<Vulnerability[]>('/vulnerabilidades');
      setVulnerabilities(data);
    } catch (error) {
      console.error('Error loading vulnerabilities:', error);
    } finally {
      setLoading(false);
    }
  };

  // Auto-refresh every 10 seconds (optional)
  useEffect(() => {
    const interval = setInterval(loadVulnerabilities, 10000);
    return () => clearInterval(interval);
  }, []);

  // Sort vulnerabilities: critical first, then by IRC descending
  const sortedVulnerabilities = useMemo(() => {
    const sorted = [...vulnerabilities];
    sorted.sort((a, b) => {
      // Critical vulnerabilities first
      if (a.severity === 'Crítica' && b.severity !== 'Crítica') return -1;
      if (a.severity !== 'Crítica' && b.severity === 'Crítica') return 1;
      // Then by IRC score descending
      return (b.irc || 0) - (a.irc || 0);
    });
    return sorted;
  }, [vulnerabilities]);

  // Determine styling based on severity
  const getSeverityStyle = (severity: string): string => {
    const baseClasses = 'p-4 border-l-4 rounded-md transition-colors duration-200';
    switch (severity) {
      case 'Crítica':
        return `${baseClasses} bg-yellow-50 border-yellow-500 shadow-sm hover:bg-yellow-100`;
      case 'Alta':
        return `${baseClasses} bg-red-50 border-red-500 hover:bg-red-100`;
      case 'Media':
        return `${baseClasses} bg-orange-50 border-orange-500 hover:bg-orange-100`;
      case 'Baja':
        return `${baseClasses} bg-blue-50 border-blue-500 hover:bg-blue-100`;
      default:
        return `${baseClasses} bg-gray-50 border-gray-500`;
    }
  };

  // Render critical alert badge
  const renderCriticalBadge = (severity: string): React.ReactNode => {
    if (severity === 'Crítica') {
      return (
        <span className="ml-2 inline-block px-3 py-1 bg-red-600 text-white text-xs font-bold rounded-full animate-pulse">
          ⚠️ Alerta crítica
        </span>
      );
    }
    return null;
  };

  // Count critical vulnerabilities
  const criticalCount = useMemo(
    () => vulnerabilities.filter(v => v.severity === 'Crítica').length,
    [vulnerabilities]
  );

  if (loading) {
    return <div className="p-6 text-center">Cargando vulnerabilidades...</div>;
  }

  return (
    <div className="p-6 space-y-4">
      {/* Header with stats */}
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Vulnerabilidades</h1>
        <div className="flex gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-red-600">{criticalCount}</div>
            <div className="text-xs text-gray-600">Críticas</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-700">{vulnerabilities.length}</div>
            <div className="text-xs text-gray-600">Total</div>
          </div>
          <button
            onClick={loadVulnerabilities}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Actualizar
          </button>
        </div>
      </div>

      {/* Vulnerabilities list */}
      <div className="space-y-3">
        {sortedVulnerabilities.length === 0 ? (
          <div className="text-center text-gray-500 py-8">
            No hay vulnerabilidades registradas
          </div>
        ) : (
          sortedVulnerabilities.map((vuln) => (
            <div
              key={vuln.id}
              className={`cursor-pointer ${getSeverityStyle(vuln.severity)}`}
              onClick={() => setSelectedId(selectedId === vuln.id ? null : vuln.id)}
            >
              {/* Header row */}
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <h3 className="font-bold text-lg flex items-center">
                    {vuln.cve}
                    {renderCriticalBadge(vuln.severity)}
                  </h3>
                </div>
                <div className="text-right">
                  <div className="font-bold text-lg">{vuln.severity}</div>
                  <div className="text-xs text-gray-600">IRC: {vuln.irc?.toFixed(2)}</div>
                </div>
              </div>

              {/* Description */}
              <p className="text-sm text-gray-700 mt-2 line-clamp-2">{vuln.description}</p>

              {/* Details grid */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-3 text-sm">
                <div>
                  <span className="font-semibold">IRC Score:</span>
                  <div className="text-base font-bold">{vuln.irc?.toFixed(2)}</div>
                </div>
                <div>
                  <span className="font-semibold">Empresa:</span>
                  <div>{vuln.company?.name || '-'}</div>
                </div>
                <div>
                  <span className="font-semibold">Analista:</span>
                  <div>{vuln.analyst?.username || 'Sin asignar'}</div>
                </div>
                <div>
                  <span className="font-semibold">Estado:</span>
                  <div>{vuln.status}</div>
                </div>
              </div>

              {/* Footer with timestamps */}
              <div className="text-xs text-gray-500 mt-3 pt-3 border-t border-gray-300">
                Creado: {new Date(vuln.created_at).toLocaleString('es-ES')}
              </div>

              {/* Expandable details (optional) */}
              {selectedId === vuln.id && (
                <div className="mt-4 pt-4 border-t border-gray-300 space-y-2 text-sm">
                  <div>
                    <span className="font-semibold">Descripción completa:</span>
                    <p className="mt-1 text-gray-700">{vuln.description}</p>
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <span className="font-semibold">Creado:</span>
                      <div>{new Date(vuln.created_at).toLocaleString('es-ES')}</div>
                    </div>
                    <div>
                      <span className="font-semibold">Actualizado:</span>
                      <div>{new Date(vuln.updated_at).toLocaleString('es-ES')}</div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default VulnerabilitiesPage;
```

---

## Tailwind CSS Classes Used

These are standard Tailwind classes. Ensure your project has Tailwind configured:

```bash
# If not already installed
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

### Color Scheme

| Severity | Background | Border | Hover |
|----------|-----------|--------|-------|
| Crítica | `bg-yellow-50` | `border-yellow-500` | `bg-yellow-100` |
| Alta | `bg-red-50` | `border-red-500` | `bg-red-100` |
| Media | `bg-orange-50` | `border-orange-500` | `bg-orange-100` |
| Baja | `bg-blue-50` | `border-blue-500` | `bg-blue-100` |

---

## API Response Format

The n8n workflow sends vulnerabilities with this structure:

```json
{
  "id": 1,
  "cve": "CVE-2025-1234",
  "description": "Vulnerability description...",
  "irc": 8.25,
  "severity": "Crítica",
  "status": "Pendiente",
  "company_id": 1,
  "assigned_analyst_id": 2,
  "created_at": "2025-05-13T10:30:00Z",
  "updated_at": "2025-05-13T10:30:00Z",
  "company": {
    "id": 1,
    "name": "Saez Logistics",
    "sector": "Logistica",
    "contact": "ciso@saezlogistics.local"
  },
  "analyst": {
    "id": 2,
    "username": "analyst",
    "email": "analyst@grupox.local",
    "role": "analyst"
  }
}
```

Your `types.ts` should already have `Vulnerability` interface compatible with this.

---

## Optional Enhancements

### 1. Auto-Refresh Banner

```tsx
const [autoRefresh, setAutoRefresh] = useState(false);

return (
  <div>
    {autoRefresh && (
      <div className="bg-blue-100 border border-blue-400 text-blue-700 px-4 py-3 rounded mb-4">
        🔄 Auto-actualización activa (cada 10 segundos)
      </div>
    )}
    <button onClick={() => setAutoRefresh(!autoRefresh)} className="btn">
      {autoRefresh ? 'Pausar' : 'Auto-actualizar'}
    </button>
  </div>
);
```

### 2. Filter by Severity

```tsx
const [filter, setFilter] = useState<string>('all');

const filteredVulns = useMemo(() => {
  if (filter === 'all') return sortedVulnerabilities;
  return sortedVulnerabilities.filter(v => v.severity === filter);
}, [sortedVulnerabilities, filter]);
```

### 3. Export to CSV

```tsx
const exportToCSV = () => {
  const csv = vulnerabilities.map(v => 
    `${v.cve},${v.severity},${v.irc},${v.company?.name}`
  ).join('\n');
  
  const blob = new Blob([csv], { type: 'text/csv' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `vulnerabilities-${new Date().toISOString()}.csv`;
  a.click();
};
```

---

## Types Definition (types.ts)

Ensure your types file includes:

```typescript
export interface Company {
  id: number;
  name: string;
  sector: string;
  contact: string;
}

export interface User {
  id: number;
  username: string;
  email: string;
  role: 'admin' | 'analyst';
}

export interface Vulnerability {
  id: number;
  cve: string;
  description: string;
  irc: number;
  severity: 'Crítica' | 'Alta' | 'Media' | 'Baja';
  status: string;
  company_id: number;
  assigned_analyst_id: number | null;
  created_at: string;
  updated_at: string;
  company?: Company;
  analyst?: User;
}
```

---

## Testing the Integration

### Test Checklist

- [ ] Vulnerabilities load on page load
- [ ] Critical vulnerabilities display with yellow background
- [ ] "Alerta crítica" badge appears on critical items
- [ ] Critical items appear first in list
- [ ] Clicking item expands details
- [ ] Update button refreshes list
- [ ] Auto-refresh (if enabled) updates every 10s
- [ ] No console errors
- [ ] Responsive on mobile

---

## Deployment Notes

### Production Considerations

1. **Remove Auto-Refresh from Production**
   - Currently set to 10 seconds
   - Increase to 60+ seconds or disable
   - Monitor database/API load

2. **Add Error Handling**
   ```tsx
   const [error, setError] = useState<string | null>(null);
   
   const loadVulnerabilities = async () => {
     try {
       // ... load code
     } catch (error) {
       setError('Error loading vulnerabilities');
       console.error(error);
     }
   };
   ```

3. **Cache Strategy**
   - Consider caching responses
   - Add "Loaded at: HH:MM:SS" timestamp

---

## Summary

After implementing these changes:

✅ Critical vulnerabilities display with yellow highlighting  
✅ "Alerta crítica" badge shows on critical items  
✅ Automatic sorting (critical first, then by IRC)  
✅ Auto-refresh capability  
✅ Expandable details  
✅ Professional appearance  
✅ Ready for thesis defense  

---

**Last Updated:** May 2026
